from fastapi import APIRouter, Depends, HTTPException, Header
import httpx
import motor.motor_asyncio as motor
import asyncio
import os, jwt, uuid
from datetime import datetime, timezone
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional

from flink.mail import (
    mail_configured,
    send_mail,
    application_approved,
    application_rejected,
)

app = APIRouter()
SECRET_KEY = os.environ.get("SECRET")
ALGORITHM = "HS256"


class PushFlinkStatusRequestBody(BaseModel):
    data: dict
    secret: str


class updateFlinkRequestBody(BaseModel):
    id: str
    name: str
    description: str
    url: str
    avatar: str
    color: str
    group: str


class addFlinkRequestBody(BaseModel):
    name: str
    description: str
    url: str
    avatar: str
    color: str
    group: str
    id: str
    latency: float


class MoveFlinkGroupBody(BaseModel):
    from_group: str
    to_group: str
    link_id: str


class GroupBody(BaseModel):
    name: str
    order: Optional[int] = 0
    description: Optional[str] = ""


class UpdateGroupBody(BaseModel):
    old_name: str
    name: str
    order: Optional[int] = 0
    description: Optional[str] = ""


async def verify(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


async def getDb():
    mongoClient = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["FLinks"]


@app.post("/pushFlinkStatus")
async def pushFlinkStatus(
    body: PushFlinkStatusRequestBody, currentCollection=Depends(getDb)
):
    try:
        if body.secret == SECRET_KEY:
            for item in body.data["linkStatus"]:
                await currentCollection.update_one(
                    {"links.id": item["id"]},
                    {"$set": {"links.$.latency": item["latency"]}},
                )
            return {"message": "success"}
        else:
            raise HTTPException(
                status_code=403,
                detail={"message": "fail", "error": "invalid secret key"},
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.put("/updateFlink")
async def updateFlink(
    body: updateFlinkRequestBody, currentCollection=Depends(getDb), user=Depends(verify)
):
    try:
        # 更新指定分组下的指定链接
        await currentCollection.update_one(
            {"name": body.group, "links.id": body.id},
            {
                "$set": {
                    "links.$.name": body.name,
                    "links.$.url": body.url,
                    "links.$.avatar": body.avatar,
                    "links.$.description": body.description,
                    "links.$.color": body.color,
                }
            },
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.delete("/deleteFlink")
async def deleteFlink(
    group: str, id: str, currentCollection=Depends(getDb), user=Depends(verify)
):
    try:
        # 从指定分组删除指定id的友链
        result = await currentCollection.update_one(
            {"name": group}, {"$pull": {"links": {"id": id}}}
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.post("/addFlink")
async def addFlink(
    body: addFlinkRequestBody, currentCollection=Depends(getDb), user=Depends(verify)
):
    try:
        # 添加到指定分组
        await currentCollection.update_one(
            {"name": body.group}, {"$push": {"links": body.model_dump()}}, upsert=True
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.post("/moveFlinkGroup")
async def moveFlinkGroup(
    body: MoveFlinkGroupBody, currentCollection=Depends(getDb), user=Depends(verify)
):
    try:
        # 先从原分组取出link
        from_doc = await currentCollection.find_one({"name": body.from_group})
        if not from_doc:
            raise HTTPException(status_code=404, detail="from_group not found")
        link = next((l for l in from_doc["links"] if l["id"] == body.link_id), None)
        if not link:
            raise HTTPException(status_code=404, detail="link not found in from_group")
        # 从原分组移除
        await currentCollection.update_one(
            {"name": body.from_group}, {"$pull": {"links": {"id": body.link_id}}}
        )
        # 添加到目标分组
        await currentCollection.update_one(
            {"name": body.to_group}, {"$push": {"links": link}}, upsert=True
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.post("/addGroup")
async def addGroup(
    body: GroupBody, currentCollection=Depends(getDb), user=Depends(verify)
):
    try:
        # 新增分组，links为空
        # 检查分组名是否已存在
        exists = await currentCollection.find_one({"name": body.name})
        if exists:
            raise HTTPException(status_code=400, detail="Group name already exists")
        await currentCollection.insert_one(
            {
                "name": body.name,
                "description": body.description or "",
                "order": body.order,
                "links": [],
            }
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.delete("/deleteGroup")
async def deleteGroup(
    name: str, currentCollection=Depends(getDb), user=Depends(verify)
):
    try:
        await currentCollection.delete_one({"name": name})
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.put("/updateGroup")
async def updateGroup(
    body: UpdateGroupBody, currentCollection=Depends(getDb), user=Depends(verify)
):
    try:
        await currentCollection.update_one(
            {"name": body.old_name},
            {
                "$set": {
                    "name": body.name,
                    "description": body.description,
                    "order": body.order,
                }
            },
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/dispatchCheckLatencyWorkflow")
async def dispatchCheckLatencyWorkflow(user=Depends(verify)):
    try:
        req = httpx.post(
            "https://api.github.com/repos/lyxofficial/check-flink/actions/workflows/check_links.yml/dispatches",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {os.environ.get('GH_TOKEN')}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={"ref": "main"},
        )
        if req.status_code >= 400:
            raise HTTPException(
                status_code=req.status_code,
                detail={"message": "fail", "error": req.text},
            )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


# ---------- 友链申请审批 ----------


class ApproveApplicationBody(BaseModel):
    id: str
    group: str
    # 以下均可选：审批时允许修改后再通过
    name: Optional[str] = None
    link: Optional[str] = None
    avatar: Optional[str] = None
    descr: Optional[str] = None
    color: Optional[str] = None


class RejectApplicationBody(BaseModel):
    id: str
    # 可选：填了理由才会给对方发邮件，不填则静默丢弃
    reason: Optional[str] = ""


async def getApplicationsDb():
    mongoClient = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["FLinkApplications"]


def _objectId(raw: str) -> ObjectId:
    try:
        return ObjectId(raw)
    except Exception:
        raise HTTPException(
            status_code=400, detail={"message": "fail", "error": "申请 id 不合法"}
        )


@app.get("/applications")
async def getApplications(
    applicationsDb=Depends(getApplicationsDb), user=Depends(verify)
):
    """待审核的友链申请（新增与修改申请都在这里，按提交时间排队）"""
    try:
        cursor = applicationsDb.find({"status": "pending"}).sort("createdAt", 1)
        results = await cursor.to_list(length=200)
        for item in results:
            item["id"] = str(item.pop("_id"))
            created = item.get("createdAt")
            item["createdAt"] = (
                created.isoformat() if hasattr(created, "isoformat") else created
            )
        return {"message": "success", "data": results}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.post("/approveApplication")
async def approveApplication(
    body: ApproveApplicationBody,
    linksDb=Depends(getDb),
    applicationsDb=Depends(getApplicationsDb),
    user=Depends(verify),
):
    """通过申请：type=0 追加到指定分组，type=1 覆盖原友链信息，随后删除申请"""
    try:
        application = await applicationsDb.find_one({"_id": _objectId(body.id)})
        if not application:
            raise HTTPException(
                status_code=404,
                detail={"message": "fail", "error": "申请不存在或已被处理"},
            )

        name = body.name or application.get("name", "")
        link = (body.link or application.get("link", "")).strip()
        avatar = body.avatar or application.get("avatar", "")
        descr = body.descr or application.get("descr", "")
        color = body.color if body.color is not None else application.get("color", "")

        if application.get("type", 0) == 1:
            target_group = application.get("targetGroup")
            target_id = application.get("targetId")
            if not target_group or not target_id:
                raise HTTPException(
                    status_code=409,
                    detail={"message": "fail", "error": "该修改申请缺少目标友链信息"},
                )
            result = await linksDb.update_one(
                {"name": target_group, "links.id": target_id},
                {
                    "$set": {
                        "links.$.name": name,
                        "links.$.url": link,
                        "links.$.avatar": avatar,
                        "links.$.description": descr,
                        "links.$.color": color,
                    }
                },
            )
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "message": "fail",
                        "error": "原友链已不存在（可能被删除或移动过分组），无法应用修改",
                    },
                )
        else:
            flink = {
                "name": name,
                "url": link,
                "avatar": avatar,
                "description": descr,
                "color": color,
                "id": uuid.uuid4().hex[:8],
                "latency": 0,
            }
            await linksDb.update_one(
                {"name": body.group}, {"$push": {"links": flink}}, upsert=True
            )

        await applicationsDb.update_one(
            {"_id": _objectId(body.id)},
            {
                "$set": {
                    "status": "approved",
                    "decidedAt": datetime.now(timezone.utc),
                    "reason": "",
                }
            },
        )

        # 审核通过后给申请人发通知（失败不影响结果，只回传给前端用于提示）
        mail_sent = False
        applicant_email = (application.get("email") or "").strip()
        is_modify = application.get("type", 0) == 1
        if mail_configured() and applicant_email:
            subject, content = application_approved(name, link, body.group, is_modify)
            mail_sent = await asyncio.to_thread(send_mail, applicant_email, subject, content)
        return {"message": "success", "mailSent": mail_sent}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.post("/rejectApplication")
async def rejectApplication(
    body: RejectApplicationBody,
    applicationsDb=Depends(getApplicationsDb),
    user=Depends(verify),
):
    """拒绝申请：可选填理由。

    - 填了理由：给申请人发邮件说明原因
    - 不填理由：静默丢弃，不发邮件
    两种都会把状态置为 rejected 并记录 decidedAt，保留 14 天（申请人可自查），到期后自动清理。
    """
    try:
        application = await applicationsDb.find_one({"_id": _objectId(body.id)})
        if not application:
            raise HTTPException(
                status_code=404,
                detail={"message": "fail", "error": "申请不存在或已被处理"},
            )

        reason = (body.reason or "").strip()
        await applicationsDb.update_one(
            {"_id": _objectId(body.id)},
            {
                "$set": {
                    "status": "rejected",
                    "reason": reason,
                    "decidedAt": datetime.now(timezone.utc),
                }
            },
        )

        mail_sent = False
        applicant_email = (application.get("email") or "").strip()
        if reason and mail_configured() and applicant_email:
            subject, content = application_rejected(
                application.get("name", ""), application.get("link", ""), reason
            )
            mail_sent = await asyncio.to_thread(
                send_mail, applicant_email, subject, content
            )
        return {"message": "success", "mailSent": mail_sent}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )
