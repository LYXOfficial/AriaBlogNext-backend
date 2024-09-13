from fastapi import APIRouter,Depends,HTTPException
import motor.motor_asyncio as motor
import os,jwt,hashlib
from pydantic import BaseModel
from datetime import datetime,timedelta

SECRET_KEY=os.environ.get("SECRET")
ALGORITHM="HS256"

app=APIRouter()

class LoginRequestBody(BaseModel):
    user:str
    password:str

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Users"]

@app.post("/login")
async def login(data:LoginRequestBody,currentCollection=Depends(getDb)):
    try:
        if await currentCollection.find_one({"user":data.user,
            "password":hashlib.sha256(data.password.encode("utf-8")).hexdigest()}): pass
        else: return {"message":"forbidden","error":"invalid username or password"}
        return {"message":"success","jwt":jwt.encode({
            "sub": data.user,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow()+timedelta(days=7)).timestamp()),
        },SECRET_KEY,algorithm=ALGORITHM)}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})
