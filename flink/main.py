from fastapi import APIRouter, Depends, HTTPException, Request
import motor.motor_asyncio as motor
import asyncio
import os
import re
import time
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional

from flink.mail import (
    mail_configured,
    send_mail,
    application_received,
    admin_new_application,
)

app = APIRouter()

MAX_NAME = 50
MAX_DESCR = 200
MAX_URL = 300
RATE_LIMIT_COUNT = 5  # 时间窗内同一 IP 允许的申请次数
RATE_LIMIT_WINDOW = 1800  # 秒

PENDING_LIMIT = 10  # 待审核队列上限
RETENTION_DAYS = 14  # 审核结果保留天数（超时清理）


async def purge_expired(applicationsDb):
    """清理「已出结果」且超过保留期的申请记录（14 天）。

    待审核的不清理；时间字段以 decidedAt 为准。清理失败不影响主流程。
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    try:
        await applicationsDb.delete_many(
            {"status": {"$ne": "pending"}, "decidedAt": {"$lt": cutoff}}
        )
    except Exception:
        pass

# 任何带标签/协议/事件属性的输入都按 XSS 拒绝（老站同样返回 406）
XSS_PATTERN = re.compile(
    r"<\s*/?\s*[a-zA-Z!]|javascript\s*:|vbscript\s*:|data\s*:|on[a-z]+\s*=", re.I
)
URL_PATTERN = re.compile(r"^https?://[^\s<>\"'\\]+$", re.I)
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
# 颜色会被前端直接拼进 <style>，只允许十六进制/函数式/纯字母的色值，避免 CSS 注入
COLOR_PATTERN = re.compile(
    r"^(#[0-9a-fA-F]{3,8}|rgba?\([0-9.,%\s]+\)|hsla?\([0-9.,%\s]+\)|[a-zA-Z]{3,20})$"
)


class ApplyRequestBody(BaseModel):
    # 全部可选，缺失/为空统一由 validate_application 返回友好的 400，
    # 避免 Pydantic 先抛出 422 导致前端要处理两种错误格式
    name: Optional[str] = ""
    link: Optional[str] = ""
    avatar: Optional[str] = ""
    descr: Optional[str] = ""
    email: Optional[str] = ""
    color: Optional[str] = ""
    type: Optional[int] = 0  # 0=新增友链申请，1=修改已有友链
    targetUrl: Optional[str] = ""  # type=1 时填当前已收录的地址


class WithdrawBody(BaseModel):
    id: str = ""
    email: str = ""


class UpdateApplicationBody(ApplyRequestBody):
    """申请人修改自己待审申请的内容（类型与目标友链保持不变）"""

    id: str = ""


async def getLinksDb():
    mongoClient = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["FLinks"]


async def getApplicationsDb():
    mongoClient = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["FLinkApplications"]


# 进程内限流：Vercel 多实例下按实例独立，能挡住单点刷申请（与登录爆破防护同样的取舍）
_rate: dict[str, list[float]] = {}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _check_rate(ip: str) -> bool:
    now = time.time()
    hits = [t for t in _rate.get(ip, []) if now - t < RATE_LIMIT_WINDOW]
    if len(hits) >= RATE_LIMIT_COUNT:
        _rate[ip] = hits
        return False
    hits.append(now)
    _rate[ip] = hits
    if len(_rate) > 5000:  # 防止字典无限增长
        for key in [k for k, v in _rate.items() if not any(now - t < RATE_LIMIT_WINDOW for t in v)]:
            _rate.pop(key, None)
    return True


def normalize_url(url: str) -> str:
    """用于判重/匹配：统一小写主机名并去掉结尾斜杠"""
    url = (url or "").strip()
    return url[:-1] if url.endswith("/") else url


async def find_link(linksDb, url: str) -> Optional[dict]:
    """按网址查已收录的友链，兼容「结尾有没有斜杠」两种写法。
    返回 {"group": 分组名, "link": 友链对象}，找不到返回 None。"""
    base = normalize_url(url)
    for candidate in (base, base + "/"):
        doc = await linksDb.find_one(
            {"links.url": candidate}, {"name": 1, "links.$": 1}
        )
        if doc and doc.get("links"):
            return {"group": doc.get("name"), "link": doc["links"][0]}
    return None


def validate_application(body: ApplyRequestBody) -> Optional[tuple[int, str]]:
    """返回 (状态码, 提示) 表示校验失败，None 表示通过。
    与业务无关，便于单测。"""
    fields = {
        "站点名称": body.name,
        "网址": body.link,
        "头像": body.avatar,
        "描述": body.descr,
        "邮箱": body.email,
        "颜色": body.color or "",
        "当前网址": body.targetUrl or "",
    }
    for label, value in fields.items():
        if value and XSS_PATTERN.search(value):
            return 406, f"{label}包含不被允许的内容"

    name = (body.name or "").strip()
    descr = (body.descr or "").strip()
    email = (body.email or "").strip()
    link = (body.link or "").strip()
    avatar = (body.avatar or "").strip()
    color = (body.color or "").strip()

    if not name or not link or not avatar:
        return 400, "站点名称、网址、头像均为必填"
    if len(name) > MAX_NAME or len(descr) > MAX_DESCR:
        return 400, f"站点名称不超过 {MAX_NAME} 字，描述不超过 {MAX_DESCR} 字"
    if not URL_PATTERN.match(link) or len(link) > MAX_URL:
        return 400, "网址格式不正确，必须以 http:// 或 https:// 开头"
    if not URL_PATTERN.match(avatar) or len(avatar) > MAX_URL:
        return 400, "头像格式不正确，必须以 http:// 或 https:// 开头"
    if email and not EMAIL_PATTERN.match(email):
        return 400, "邮箱格式不正确"
    if color and not COLOR_PATTERN.match(color):
        return 400, "颜色只支持 #十六进制 / rgb() / rgba() / hsl() / 颜色名"
    if body.type not in (0, 1):
        return 400, "申请类型不正确"
    if body.type == 1:
        target = (body.targetUrl or "").strip()
        if not URL_PATTERN.match(target):
            return 400, "修改申请需要填写当前已收录的网址"
    return None


@app.post("/apply")
async def applyFlink(
    body: ApplyRequestBody,
    request: Request,
    linksDb=Depends(getLinksDb),
    applicationsDb=Depends(getApplicationsDb),
):
    invalid = validate_application(body)
    if invalid:
        status, message = invalid
        raise HTTPException(status_code=status, detail={"message": "fail", "error": message})

    ip = _client_ip(request)
    if not _check_rate(ip):
        raise HTTPException(
            status_code=429,
            detail={"message": "fail", "error": "提交过于频繁，请稍后再试"},
        )

    name = (body.name or "").strip()
    link = (body.link or "").strip()
    avatar = (body.avatar or "").strip()
    descr = (body.descr or "").strip()
    email = (body.email or "").strip()
    color = (body.color or "").strip()

    try:
        # 先清掉过期结果，再判断队列容量
        await purge_expired(applicationsDb)
        pending = await applicationsDb.count_documents({"status": "pending"})
        if pending >= PENDING_LIMIT:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "fail",
                    "error": "申请列表已满，请稍后再提交",
                },
            )

        target_id = None
        target_group = None

        if body.type == 1:
            # 修改申请：必须能在已收录友链里找到，记录目标便于审批时定位
            found = await find_link(linksDb, body.targetUrl or "")
            if not found:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "message": "fail",
                        "error": "没有找到这个网址的友链，请确认填写的是当前已收录的地址",
                    },
                )
            target_group = found["group"]
            target_id = found["link"].get("id")
            # 同一个友链只允许存在一条待审的修改申请
            duplicated = await applicationsDb.find_one(
                {"targetId": target_id, "type": 1, "status": "pending"}, {"_id": 1}
            )
        else:
            # 新增申请：已收录 / 已提交过的都拦下来，避免重复
            exists = await find_link(linksDb, link)
            if exists:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "message": "fail",
                        "error": "该网址已经在友链里了，如需修改请提交修改申请",
                    },
                )
            duplicated = await applicationsDb.find_one(
                {"link": normalize_url(link), "type": 0, "status": "pending"},
                {"_id": 1},
            )

        if duplicated:
            raise HTTPException(
                status_code=409,
                detail={"message": "fail", "error": "该网址已有待审核的申请，请耐心等待"},
            )

        # 同一邮箱重新提交时，清掉它旧的「已出结果」记录（相当于重新排队）
        if email:
            await applicationsDb.delete_many(
                {"email": email, "status": {"$ne": "pending"}}
            )

        await applicationsDb.insert_one(
            {
                "type": body.type,
                "name": name,
                "link": link,
                "avatar": avatar,
                "descr": descr,
                "color": color,
                "email": email,
                "targetId": target_id,
                "targetGroup": target_group,
                "targetUrl": (body.targetUrl or "").strip(),
                "status": "pending",
                "reason": "",
                "createdAt": datetime.now(timezone.utc),
                "decidedAt": None,
                "ip": ip,
            }
        )
        return {
            "message": "success",
            "mailSent": await _notify_new_application(
                name, link, email, body.type, avatar, descr
            ),
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


async def _notify_new_application(
    name: str, link: str, email: str, kind: int, avatar: str = "", descr: str = ""
) -> bool:
    """给申请人发回执、给博主（若配置了 FLINK_ADMIN_EMAIL）发提醒。
    邮件失败不影响申请本身，只把结果回给前端用于提示。"""
    if not mail_configured():
        return False
    is_modify = kind == 1
    sent = False
    if email:
        subject, text, html = application_received(name, link, is_modify, avatar, descr)
        sent = await asyncio.to_thread(send_mail, email, subject, text, html)
    admin_email = (os.environ.get("FLINK_ADMIN_EMAIL") or "").strip()
    if admin_email:
        a_subject, a_text, a_html = admin_new_application(
            name, link, email or "（未填写）", is_modify, avatar, descr
        )
        await asyncio.to_thread(send_mail, admin_email, a_subject, a_text, a_html)
    return sent


@app.get("/apply/status")
async def getApplyStatus(email: str, applicationsDb=Depends(getApplicationsDb)):
    """申请人用邮箱自查进度"""
    email = (email or "").strip()
    if not EMAIL_PATTERN.match(email):
        raise HTTPException(
            status_code=400,
            detail={"message": "fail", "error": "邮箱格式不正确"},
        )
    try:
        await purge_expired(applicationsDb)
        cursor = (
            applicationsDb.find(
                {"email": email},
                {
                    "_id": 1,
                    "type": 1,
                    "name": 1,
                    "link": 1,
                    "avatar": 1,
                    "descr": 1,
                    "color": 1,
                    "targetUrl": 1,
                    "targetGroup": 1,
                    "status": 1,
                    "reason": 1,
                    "createdAt": 1,
                    "decidedAt": 1,
                },
            )
            .sort("createdAt", -1)
        )
        results = await cursor.to_list(length=20)
        for item in results:
            item["id"] = str(item.pop("_id"))
            for key in ("createdAt", "decidedAt"):
                value = item.get(key)
                item[key] = (
                    value.isoformat() if hasattr(value, "isoformat") else value
                )
        return {"message": "success", "data": results}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


async def _own_pending(applicationsDb, app_id: str, email: str):
    """取出「属于该邮箱、且仍在待审」的申请；否则抛出对应错误。"""
    try:
        oid = ObjectId(app_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail={"message": "fail", "error": "申请 id 不合法"},
        )
    doc = await applicationsDb.find_one({"_id": oid})
    if not doc:
        raise HTTPException(
            status_code=404,
            detail={"message": "fail", "error": "申请不存在或已被处理"},
        )
    if not (doc.get("email") or "").strip():
        raise HTTPException(
            status_code=409,
            detail={
                "message": "fail",
                "error": "该申请提交时没有填写邮箱，无法自助修改或撤销",
            },
        )
    if (doc.get("email") or "").strip().lower() != (email or "").strip().lower():
        raise HTTPException(
            status_code=403,
            detail={"message": "fail", "error": "邮箱与申请不匹配"},
        )
    if doc.get("status") != "pending":
        raise HTTPException(
            status_code=409,
            detail={"message": "fail", "error": "该申请已处理，无法再操作"},
        )
    return doc


@app.post("/apply/withdraw")
async def withdrawApplication(
    body: WithdrawBody, applicationsDb=Depends(getApplicationsDb)
):
    """申请人撤销自己的待审申请，撤销后立即移出队列。"""
    doc = await _own_pending(applicationsDb, body.id, body.email)
    try:
        await applicationsDb.delete_one({"_id": doc["_id"]})
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.post("/apply/update")
async def updateApplication(
    body: UpdateApplicationBody,
    linksDb=Depends(getLinksDb),
    applicationsDb=Depends(getApplicationsDb),
):
    """申请人修改自己待审申请的内容（申请类型与目标友链保持不变）。"""
    doc = await _own_pending(applicationsDb, body.id, body.email)

    # 复用同一套字段校验；邮箱与类型取库里已存的，避免被改身份
    merged = ApplyRequestBody(
        name=body.name,
        link=body.link,
        avatar=body.avatar,
        descr=body.descr,
        email=doc.get("email") or "",
        color=body.color,
        type=doc.get("type", 0),
        targetUrl=doc.get("targetUrl") or "",
    )
    invalid = validate_application(merged)
    if invalid:
        status, message = invalid
        raise HTTPException(
            status_code=status, detail={"message": "fail", "error": message}
        )

    link = (body.link or "").strip()
    try:
        # 改成了新网址：重新做重复校验（已收录 / 别人的待审申请）
        if normalize_url(link) != normalize_url(doc.get("link") or ""):
            if doc.get("type", 0) == 0:
                exists = await find_link(linksDb, link)
                if exists:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "message": "fail",
                            "error": "该网址已经在友链里了，如需修改请提交修改申请",
                        },
                    )
                duplicated = await applicationsDb.find_one(
                    {
                        "link": normalize_url(link),
                        "type": 0,
                        "status": "pending",
                        "_id": {"$ne": doc["_id"]},
                    },
                    {"_id": 1},
                )
                if duplicated:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "message": "fail",
                            "error": "该网址已有待审核的申请，请耐心等待",
                        },
                    )

        await applicationsDb.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "name": merged.name.strip(),
                    "link": link,
                    "avatar": merged.avatar.strip(),
                    "descr": merged.descr.strip(),
                    "color": (merged.color or "").strip(),
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
        )
        return {"message": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )
