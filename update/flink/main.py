from fastapi import APIRouter,Depends,HTTPException,Header
import motor.motor_asyncio as motor
import os,jwt
from pydantic import BaseModel
from typing import Optional, List
app=APIRouter()
SECRET_KEY=os.environ.get("SECRET")
ALGORITHM="HS256"
class PushFlinkStatusRequestBody(BaseModel):
    data:dict
    secret:str
class updateFlinkRequestBody(BaseModel):
    id:str
    name:str
    description:str
    url:str
    avatar:str
    color:str
    group:str
class addFlinkRequestBody(BaseModel):
    name:str
    description:str
    url:str
    avatar:str
    color:str
    group:str
class MoveFlinkGroupBody(BaseModel):
    from_group: str
    to_group: str
    link_id: str

class GroupBody(BaseModel):
    name: str
    description: Optional[str] = ""

class UpdateGroupBody(BaseModel):
    old_name: str
    name: str
    description: Optional[str] = ""
async def verify(authorization: str=Header(None)):
    if not authorization:
        raise HTTPException(status_code=401,detail="Authorization header missing")
    token=authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid token")
async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["FLinks"]
@app.post("/pushFlinkStatus")
async def pushFlinkStatus(body:PushFlinkStatusRequestBody,currentCollection=Depends(getDb)):
    try:
        if body.secret==SECRET_KEY:
            for item in body.data["linkStatus"]:
                await currentCollection.update_one({"links.id":item["id"]},{"$set":{"links.$.latency":item["latency"]}})
            return {"message":"success"}
        else:
            raise HTTPException(status_code=403,detail={"message":"fail","error":"invalid secret key"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})

@app.put("/updateFlink")
async def updateFlink(body: updateFlinkRequestBody, currentCollection=Depends(getDb), user=Depends(verify)):
    try:
        # 更新指定分组下的指定链接
        await currentCollection.update_one(
            {"name": body.group, "links.id": body.id},
            {"$set": {
                "links.$.name": body.name,
                "links.$.url": body.url,
                "links.$.avatar": body.avatar,
                "links.$.description": body.description,
                "links.$.color": body.color
            }}
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})

@app.delete("/deleteFlink")
async def deleteFlink(group: str, id: str, currentCollection=Depends(getDb), user=Depends(verify)):
    try:
        # 从指定分组删除指定id的友链
        result = await currentCollection.update_one(
            {"name": group},
            {"$pull": {"links": {"id": id}}}
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})

@app.post("/addFlink")
async def addFlink(body: addFlinkRequestBody, currentCollection=Depends(getDb), user=Depends(verify)):
    try:
        # 添加到指定分组
        await currentCollection.update_one(
            {"name": body.group},
            {"$push": {"links": body.model_dump()}},
            upsert=True
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})

@app.post("/moveFlinkGroup")
async def moveFlinkGroup(body: MoveFlinkGroupBody, currentCollection=Depends(getDb), user=Depends(verify)):
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
            {"name": body.from_group},
            {"$pull": {"links": {"id": body.link_id}}}
        )
        # 添加到目标分组
        await currentCollection.update_one(
            {"name": body.to_group},
            {"$push": {"links": link}},
            upsert=True
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})

@app.post("/addGroup")
async def addGroup(body: GroupBody, currentCollection=Depends(getDb), user=Depends(verify)):
    try:
        # 新增分组，links为空
        await currentCollection.insert_one({
            "name": body.name,
            "description": body.description or "",
            "links": []
        })
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})

@app.delete("/deleteGroup")
async def deleteGroup(name: str, currentCollection=Depends(getDb), user=Depends(verify)):
    try:
        await currentCollection.delete_one({"name": name})
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})

@app.put("/updateGroup")
async def updateGroup(body: UpdateGroupBody, currentCollection=Depends(getDb), user=Depends(verify)):
    try:
        await currentCollection.update_one(
            {"name": body.old_name},
            {"$set": {"name": body.name, "description": body.description}}
        )
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})