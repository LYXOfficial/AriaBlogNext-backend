from fastapi import APIRouter,Depends
import motor.motor_asyncio as motor
import os

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Speaks"]
@app.get("/speaks")
async def getSpeaks(startl:int=0,endl:int=None,currentCollection=Depends(getDb)):
    try:
        totalCount=await currentCollection.count_documents({})
        endl=endl or totalCount
        postsCursor=currentCollection.find({},{"_id":0}).sort("time",-1)
        posts=await postsCursor.to_list(length=endl)
        data=posts[startl:endl]
        return {"message":"success","data":data}
    except Exception as e:
        return {"message":"fail","error":str(e)}