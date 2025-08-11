from fastapi import APIRouter, Depends, HTTPException, Header
import motor.motor_asyncio as motor
import os
import jwt
from datetime import datetime
from pydantic import BaseModel
import httpx

SECRET_KEY = os.environ.get("SECRET")
ALGORITHM = "HS256"

app = APIRouter()

async def verify(authorization: str=Header(None)):
    if not authorization:
        raise HTTPException(status_code=401,detail="Authorization header missing")
    token=authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid token")
async def getDb():
    mongoClient = motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["webSiteInfo"]
async def updateTime(currentCollection):
    current_time=int(datetime.now().timestamp())
    await currentCollection.update_one(
        {"key":"latestUpdateTime"},
        {"$set":{"value":current_time}},
        upsert=True
    )
@app.post("/latestUpdateTime")
async def latestUpdateTime(currentCollection=Depends(getDb),user=Depends(verify)):
    try:
        await updateTime(currentCollection=currentCollection)
        try:
            httpx.get("https://blog.yaria.top/refreshCache/siteinfo")
        except:
            pass
        return {"message":"success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})
