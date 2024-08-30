from fastapi import APIRouter,Depends
import motor.motor_asyncio as motor
import os

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Posts"]

@app.get("/postCount")
async def getPostCount(currentCollection=Depends(getDb)):
    count=await currentCollection.count_documents({})
    return {"message":"success","count":count}

@app.get("/postsInfo")
async def getPostsInfo(startl:int=0,endl:int=None,currentCollection=Depends(getDb)):
    try:
        totalCount=await currentCollection.count_documents({})
        endl=endl or totalCount
        postsCursor=currentCollection.find({},{"_id":0,"mdContent":0}).sort("publishTime",-1)
        posts=await postsCursor.to_list(length=endl)
        data=posts[startl:endl]
        return {"message":"success","data":data}
    except Exception as e:
        return {"message":"fail","error":str(e)}

@app.get("/postBySlug")
async def getPostBySlug(slug:str,currentCollection=Depends(getDb)):
    try:
        post=await currentCollection.find_one({"slug":slug},{"_id":0})
        if post is None:
            return {"message":"fail","error":"post not found"}
        return {"message":"success","data":post}
    except Exception as e:
        return {"message":"fail","error":str(e)}

@app.get("/postSlugs")
async def getPostSlugs(currentCollection=Depends(getDb)):
    try:
        postCursor=currentCollection.find({},{"_id":0,"slug":1})
        posts=await postCursor.to_list(length=await currentCollection.count_documents({}))
        return {"message":"success","data":[i["slug"] for i in posts]}
    except Exception as e:
        return {"message":"fail","error":str(e)}
    
@app.get("/totalWordCount")
async def getTotalWordCount(currentCollection=Depends(getDb)):
    try:
        pipeline = [
            {"$group": {"_id": None, "totalWordCount": {"$sum": "$wordCount"}}},
            {"$project": {"_id": 0, "totalWordCount": 1}}
        ]
        result = await currentCollection.aggregate(pipeline).to_list(length=1)
        total_word_count = result[0]["totalWordCount"] if result else 0
        return {"message": "success", "count": total_word_count}
    except Exception as e:
        return {"message": "fail", "error": str(e)}