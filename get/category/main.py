from fastapi import APIRouter,Depends
import motor.motor_asyncio as motor
import os

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Posts"]

@app.get("/categories")
async def getCategories(currentCollection=Depends(getDb)):
    try:
        pipeline=[
            {"$group":{"_id":"$category","count":{"$sum":1}}},
            {"$project":{"_id":0,"name":"$_id","count":1}}
        ]
        results=await currentCollection.aggregate(pipeline).to_list(length=None)
        return {"message":"success","data":results}
    except Exception as e:
        return {"message":"fail","error":str(e)}

@app.get("/categoryInfo")
async def getCategoryInfo(category:str,startl:int=0,endl:int=None,currentCollection=Depends(getDb)):
    try:
        totalCount=await currentCollection.count_documents({"category":category})
        endl=endl or totalCount
        resl=await currentCollection.find({"category":category},{"_id":0,"mdContent":0,"plainContent":0}).sort("date",-1).to_list(length=endl)
        if resl is None:
            return {"message":"fail","error":"category not found"}
        data=resl[startl:endl]
        return {"message":"success","data":data,"totalCount":totalCount}
    except Exception as e:
        return {"message":"fail","error":str(e)}
    
@app.get("/categoryCount")
async def getCategoryCount(currentCollection=Depends(getDb)):
    try:
        pipeline=[
            {"$unwind":"$category"},
            {"$group":{"_id":None,"uniqueTags":{"$addToSet":"$category"}}},
            {"$project":{"_id":0,"totalCount":{"$size":"$uniqueTags"}}}
        ]
        result=await currentCollection.aggregate(pipeline).to_list(length=None)
        total_count=result[0]["totalCount"] if result else 0
        return {"message":"success","count":total_count}
    except Exception as e:
        return {"message":"fail","error":str(e)}