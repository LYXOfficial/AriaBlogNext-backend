from fastapi import APIRouter, Depends, HTTPException, Header
import motor.motor_asyncio as motor
import os
import jwt
from datetime import datetime
from pydantic import BaseModel
import httpx

SECRET_KEY = os.environ.get("SECRET")
ALGORITHM = "HS256"

class UpdateTimeRequestBody(BaseModel):
    token:str

app = APIRouter()

async def getDb():
    mongoClient = motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["webSiteInfo"]
async def updateTime(currentCollection):
    current_time=int(datetime.now().timestamp())
    await currentCollection.update_one(
        {"key":"latestUpdateTime"},
        {"$set":{"value":current_time}},
        upsert=True
    )
@app.post("/latestUpdateTime")
async def latestUpdateTime(body:UpdateTimeRequestBody,currentCollection=Depends(getDb)):
    try:
        try:
            jwt.decode(body.token,SECRET_KEY,algorithms=[ALGORITHM])
        except Exception as e:
            raise HTTPException(status_code=401,detail="access failed")
        await updateTime(currentCollection=currentCollection)
        try:
            httpx.get("https://blog.yaria.top/refreshCache/siteinfo")
        except:
            pass
        return {"message":"success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})
