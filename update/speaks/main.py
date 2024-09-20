from fastapi import APIRouter,Depends,HTTPException,Header
import motor.motor_asyncio as motor
import os,jwt
from pydantic import BaseModel
SECRET_KEY=os.environ.get("SECRET")
ALGORITHM="HS256"
app=APIRouter()
class DeleteSpeaksRequestBody(BaseModel):
    time:str
async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Speaks"]
async def verify(authorization: str=Header(None)):
    if not authorization:
        raise HTTPException(status_code=401,detail="Authorization header missing")
    token=authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid token")
@app.delete("/deleteSpeaks")
async def deleteSpeaks(body:DeleteSpeaksRequestBody,currentCollection=Depends(getDb)):
    try:
        await currentCollection.delete_one({"time":body.time})
        return {"message":"success"}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})