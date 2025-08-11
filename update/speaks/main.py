from fastapi import APIRouter,Depends,HTTPException,Header
import motor.motor_asyncio as motor
import os,jwt,re
from pydantic import BaseModel
SECRET_KEY=os.environ.get("SECRET")
ALGORITHM="HS256"
app=APIRouter()
class DeleteSpeaksRequestBody(BaseModel):
    time:int
class UpdateSpeaksRequestBody(BaseModel):
    time:int
    content:str
def replace_and_remove_tags(text):
    text=re.sub(r'<a\s+[^>]*>.*?<\/a>','[链接]',text)
    text=re.sub(r'<img\s+[^>]*>','[图片]',text)
    text=re.sub('<.*?>','',text)
    return text
async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["Speaks"]
async def verify(authorization: str=Header(None)):
    if not authorization:
        raise HTTPException(status_code=401,detail="Authorization header missing")
    token=authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid token")
@app.delete("/deleteSpeaks")
async def deleteSpeaks(body:DeleteSpeaksRequestBody,currentCollection=Depends(getDb),user=Depends(verify)):
    try:
        await currentCollection.delete_one({"time":body.time})
        return {"message":"success"}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})
@app.put("/updateSpeaks")
async def updateSpeaks(body:UpdateSpeaksRequestBody,currentCollection=Depends(getDb),user=Depends(verify)):
    try:
        await currentCollection.update_one({"time":body.time},{"$set":{"content":body.content,"plainContent":replace_and_remove_tags(body.content)}})
        return {"message":"success"}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})
@app.post("/newSpeaks")
async def newSpeaks(body:UpdateSpeaksRequestBody,currentCollection=Depends(getDb),user=Depends(verify)):
    try:
        await currentCollection.insert_one({"content":body.content,"plainContent":replace_and_remove_tags(body.content),"time":body.time})
        return {"message":"success"}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})