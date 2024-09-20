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
@app.post("/pushFlinkStatus")
async def pushFlinkStatus(body:PushFlinkStatusRequestBody,currentCollection=Depends(getDb)):
    try:
        if body.secret==SECRET_KEY:
            for item in body["data"]["linkStatus"]:
                await currentCollection.update_one({"id":item["id"]},{"$set":{"lantency":item["lantency"]}})
            return {"message":"success"}
        else:
            raise HTTPException(status_code=403,detail={"message":"fail","error":"invalid secret key"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})