from fastapi import APIRouter,Depends,HTTPException
import motor.motor_asyncio as motor
import os
from pydantic import BaseModel
app=APIRouter()
SECRET_KEY=os.environ.get("SECRET")
class ExportMongoRequestBody(BaseModel):
    secret: str

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]

@app.get("/")
async def exportMongo(body:ExportMongoRequestBody,currentCollection=Depends(getDb)):
    try:
        if body.secret==SECRET_KEY:
            db=[{i:list(currentCollection[i].find())} for i in list(currentCollection.list_collection_names())]
            return {"message":"success","db":db}
        else:
            raise HTTPException(status_code=403,detail={"message":"fail","error":"invalid secret key"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})