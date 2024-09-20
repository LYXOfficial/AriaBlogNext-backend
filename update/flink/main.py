from fastapi import APIRouter,Depends,HTTPException
import motor.motor_asyncio as motor
import os
from pydantic import BaseModel
app=APIRouter()
SECRET_KEY=os.environ.get("SECRET")
class PushFlinkStatusRequestBody(BaseModel):
    data:dict
    secret:str
async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["FLinks"]
async def getStatusDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["FLinkStatus"]
@app.post("/pushFlinkStatus")
async def pushFlinkStatus(body:PushFlinkStatusRequestBody,currentCollection=Depends(getStatusDb)):
    try:
        if body.secret==SECRET_KEY:
            await currentCollection.delete_many({})
            await currentCollection.insert_one({"data":body.data})
            return {"message":"success"}
        else:
            raise HTTPException(status_code=403,detail={"message":"fail","error":"invalid secret key"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})