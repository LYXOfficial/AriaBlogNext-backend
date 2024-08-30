from fastapi import APIRouter,Depends
import motor.motor_asyncio as motor
import os

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Posts"]

@app.get("/getPostCount")
async def getPostCount(currentCollection=Depends(getDb)):
    count=await currentCollection.count_documents({})
    return {"message":"success","count":count}

@app.get("/getPostsInfo")
async def getPostsInfo(startl:int=0,endl:int=None,currentCollection=Depends(getDb)):
    try:
        totalCount=await currentCollection.count_documents({})
        endl=endl or totalCount
        postsCursor=currentCollection.find({},{"_id":0}).sort("publishTime",-1)
        posts=await postsCursor.to_list(length=endl)
        data=[(i.pop("mdContent"),i)[1] for i in posts][startl:endl]
        return {"message":"success","data":data}
    except Exception as e:
        return {"message":"fail","error":str(e)}

@app.get("/getPostBySlug")
async def getPostBySlug(slug:str,currentCollection=Depends(getDb)):
    try:
        post=await currentCollection.find_one({"slug":slug},{"_id":0})
        if post is None:
            return {"message":"fail","error":"post not found"}
        return {"message":"success","data":post}
    except Exception as e:
        return {"message":"fail","error":str(e)}
