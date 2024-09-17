from fastapi import APIRouter,Depends,HTTPException,Header
import motor.motor_asyncio as motor
import os,jwt
SECRET_KEY=os.environ.get("SECRET")
ALGORITHM="HS256"
app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["webSiteInfo"]

@app.get("/lastUpdateTime")
async def getLatestUpdateTime(currentCollection=Depends(getDb)):
    try:
        time=int((await currentCollection.find_one({"key":"latestUpdateTime"},{"_id":0}))["value"])
        return {"message":"success","time":time}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})

async def verify(authorization: str=Header(None)):
    if not authorization:
        raise HTTPException(status_code=401,detail="Authorization header missing")
    token=authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid token")
@app.get("/imageUploadToken")
async def imageUploadToken(user=Depends(verify)):
    try:
        return {"message":"success","token":os.environ.get("QBU_TOKEN")}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})