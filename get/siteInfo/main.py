from fastapi import APIRouter,Depends
import motor.motor_asyncio as motor
import os

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["webSiteInfo"]

@app.get("/lastUpdateTime")
async def getLatestUpdateTime(currentCollection=Depends(getDb)):
    time=int((await currentCollection.find_one({"key":"latestUpdateTime"},{"_id":0}))["value"])
    return {"message":"success","time":time}
