from fastapi import APIRouter,Depends,HTTPException
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
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})
@app.get("/flinkCount")
async def getFlinkCount(currentCollection=Depends(getDb)):
    try:
        count=await currentCollection.count_documents({})
        return {"message":"success","data":count}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})