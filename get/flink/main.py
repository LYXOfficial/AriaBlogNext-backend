from fastapi import APIRouter,Depends
import motor.motor_asyncio as motor
import os

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["FLinks"]

@app.get("/flinks")
async def getFlinks(currentCollection=Depends(getDb)):
    try:
        results=await currentCollection.find({},{"_id":0}).to_list(length=None)
        return {"message":"success","data":results}
    except Exception as e:
        return {"message":"fail","error":str(e)}