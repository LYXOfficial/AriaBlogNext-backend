from fastapi import APIRouter, Depends, HTTPException, Request
import motor.motor_asyncio as motor
import asyncio
import os
import re
import time
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional

from flink.mail import (
    mail_configured,
    send_mail,
    application_received,
    admin_new_application,
)
from flink.screening import app as screening_app
from flink.screening import trigger_screening

from db import get_database

app = APIRouter()
app.include_router(screening_app)

MAX_NAME = 50
MAX_DESCR = 200
MAX_URL = 300
RATE_LIMIT_COUNT = 5  # 时间窗内同一 IP 允许的申请次数
RATE_LIMIT_WINDOW = 1800  # 秒

PENDING_LIMIT = 20  # 待审核队列上限
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


async def getLinksDb():
    return get_database()["FLinks"]


async def getApplicationsDb():
    return get_database()["FLinkApplications"]


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


def _norm_text(value) -> str:
    return (value or "").strip()


def _norm_url_text(value) -> str:
    text = _norm_text(value)
    return text[:-1] if text.endswith("/") else text


def _norm_color(value) -> str:
    # 卡片渲染时缺省用 #888888，这里保持一致
    return (_norm_text(value) or "#888888").lower()


def is_same_as_current(current: dict, name, link, avatar, descr, color) -> bool:
    """修改申请的内容与现网友链完全一致时返回 True（无变化）"""
    return (
        _norm_text(current.get("name")) == _norm_text(name)
        and _norm_url_text(current.get("url")) == _norm_url_text(link)
        and _norm_text(current.get("avatar")) == _norm_text(avatar)
        and _norm_text(current.get("description")) == _norm_text(descr)
        and _norm_color(current.get("color")) == _norm_color(color)
    )


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


_DUPLICATE_PENDING_ERROR = {
    "status_code": 409,
    "detail": {
        "message": "fail",
        "error": "已有一条内容完全相同的申请在等待审核，无需重复提交",
    },
}


def _application_identity(
    name, link, avatar, descr, color, email, app_type, target_id
) -> tuple:
    """判重用的归一化字段组：内容（含类型与修改对象）完全一致才算重复。

    与「无变化修改申请」同一套归一化：trim、URL 去结尾斜杠、颜色缺省 #888888；
    邮箱大小写不敏感。写错了任何一项都可以直接重新提交。"""
    return (
        _norm_text(name),
        _norm_url_text(link),
        _norm_text(avatar),
        _norm_text(descr),
        _norm_color(color),
        _norm_text(email).lower(),
        app_type,
        target_id,
    )


def _doc_identity(doc: dict) -> tuple:
    return _application_identity(
        doc.get("name"),
        doc.get("link"),
        doc.get("avatar"),
        doc.get("descr"),
        doc.get("color"),
        doc.get("email"),
        doc.get("type", 0),
        doc.get("targetId"),
    )


async def _has_identical_pending(applicationsDb, identity: tuple) -> bool:
    """待审队列里是否已有内容完全相同的申请。

    队列上限 20 条，全量取出来在应用侧比对，
    顺便规避库里 link 结尾斜杠两种写法导致的漏判。"""
    cursor = applicationsDb.find(
        {"status": "pending"},
        {
            "name": 1,
            "link": 1,
            "avatar": 1,
            "descr": 1,
            "color": 1,
            "email": 1,
            "type": 1,
            "targetId": 1,
        },
    )
    async for doc in cursor:
        if _doc_identity(doc) == identity:
            return True
    return False


async def _ensure_capacity(applicationsDb) -> None:
    """清理过期结果并检查待审队列是否已满。"""
    await purge_expired(applicationsDb)
    pending = await applicationsDb.count_documents({"status": "pending"})
    if pending >= PENDING_LIMIT:
        raise HTTPException(
            status_code=429,
            detail={"message": "fail", "error": "申请列表已满，请稍后再提交"},
        )


async def _check_new_request(linksDb, applicationsDb, fields: dict) -> None:
    """新增申请：网址已收录时拒绝；与某条待审申请内容完全一致也拒绝。

    只有部分字段相同（比如改完描述重新提交）直接放行——
    自助修改/撤销已下线，重新提交就是新的修改方式，旧的等博主审核时处理。"""
    if await find_link(linksDb, fields["link"]):
        raise HTTPException(
            status_code=409,
            detail={
                "message": "fail",
                "error": "该网址已经在友链里了，如需修改请提交修改申请",
            },
        )
    identity = _application_identity(
        fields["name"],
        fields["link"],
        fields["avatar"],
        fields["descr"],
        fields["color"],
        fields["email"],
        0,
        None,
    )
    if await _has_identical_pending(applicationsDb, identity):
        raise HTTPException(**_DUPLICATE_PENDING_ERROR)


async def _check_modify_request(linksDb, applicationsDb, target_url: str, fields: dict):
    """修改申请：目标友链必须存在、内容确有变化、且没有内容完全相同的待审申请。

    返回 (target_group, target_id)。
    """
    found = await find_link(linksDb, target_url)
    if not found:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "fail",
                "error": "没有找到这个网址的友链，请确认填写的是当前已收录的地址",
            },
        )
    if is_same_as_current(
        found["link"],
        fields["name"],
        fields["link"],
        fields["avatar"],
        fields["descr"],
        fields["color"],
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "message": "fail",
                "error": "内容与当前友链完全一致，无需提交修改申请",
            },
        )
    target_id = found["link"].get("id")
    identity = _application_identity(
        fields["name"],
        fields["link"],
        fields["avatar"],
        fields["descr"],
        fields["color"],
        fields["email"],
        1,
        target_id,
    )
    if await _has_identical_pending(applicationsDb, identity):
        raise HTTPException(**_DUPLICATE_PENDING_ERROR)
    return found["group"], target_id


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

    fields = {
        "name": name,
        "link": link,
        "avatar": avatar,
        "descr": descr,
        "color": color,
        "email": email,
    }

    try:
        await _ensure_capacity(applicationsDb)

        if body.type == 1:
            target_group, target_id = await _check_modify_request(
                linksDb, applicationsDb, body.targetUrl or "", fields
            )
        else:
            target_group = target_id = None
            await _check_new_request(linksDb, applicationsDb, fields)

        # 同一邮箱重新提交时，清掉它旧的「已出结果」记录（相当于重新排队）
        if email:
            await applicationsDb.delete_many(
                {"email": email, "status": {"$ne": "pending"}}
            )

        result = await applicationsDb.insert_one(
            {
                "type": body.type,
                **fields,
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
        # AI 初筛：入库后触发 GitHub Actions 抓站分析；失败不影响申请提交
        screening_triggered = await trigger_screening(
            str(result.inserted_id), link, name, descr
        )
        return {
            "message": "success",
            "screeningTriggered": screening_triggered,
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
async def getApplyStatus(
    email: Optional[str] = None,
    name: Optional[str] = None,
    applicationsDb=Depends(getApplicationsDb),
):
    """申请人用邮箱或站点名称自查进度（至少填一个，同时填时结果取并集）"""
    email = (email or "").strip()
    name = (name or "").strip()
    conditions = []
    if email:
        if not EMAIL_PATTERN.match(email):
            raise HTTPException(
                status_code=400,
                detail={"message": "fail", "error": "邮箱格式不正确"},
            )
        conditions.append({"email": email})
    if name:
        if len(name) > MAX_NAME:
            raise HTTPException(
                status_code=400,
                detail={"message": "fail", "error": "站点名称过长"},
            )
        # 站点名按大小写不敏感精确匹配，避免只敲半个名字就捞到别人的申请；
        # re.escape 防止输入里的正则元字符被当成模式执行
        conditions.append(
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
        )
    if not conditions:
        raise HTTPException(
            status_code=400,
            detail={"message": "fail", "error": "请填写申请时的邮箱或站点名称"},
        )
    try:
        await purge_expired(applicationsDb)
        cursor = (
            applicationsDb.find(
                {"$or": conditions} if len(conditions) > 1 else conditions[0],
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


# 申请人自助「修改/撤销」接口（/apply/update、/apply/withdraw）已下线：
# 没有可靠办法核实操作者就是申请人本人（邮箱可缺填，站名/网址又是公开信息），
# 改成「内容有变即可直接重新提交」，与待审申请完全相同的重复提交会被拦下，
# 旧的待审记录由博主在后台审批时一并处理（拒绝掉过期版本即可）。
