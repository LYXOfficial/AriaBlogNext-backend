from fastapi import APIRouter,Depends,HTTPException
import motor.motor_asyncio as motor
import os
app=APIRouter()
async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["FLinks"]
async def getStatusDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["FLinkStatus"]
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
        pipeline=[
            {"$match":{"links":{"$exists":True}}},
            {"$project":{"linksCount":{"$size":"$links"}}},
            {"$group":{"_id":None,"totalLinks":{"$sum":"$linksCount"}}}
        ]
        result=await currentCollection.aggregate(pipeline).to_list(length=None)
        totalLinks=result[0]["totalLinks"] if result else 0
        return {"message":"success","count":totalLinks}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})
@app.get("/flinkStatus")
async def getFlinkStatus(currentCollection=Depends(getStatusDb)):
    try:
        result=(await currentCollection.find({},{}).to_list(length=1))[0]
        return {"message":"success","data":result} if result else {"message":"success","data":{}}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})