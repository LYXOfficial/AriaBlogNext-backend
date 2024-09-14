from fastapi import APIRouter,Depends,HTTPException
import motor.motor_asyncio as motor
import os,random,re

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Drafts"]

@app.get("/draftCount")
async def getDraftCount(currentCollection=Depends(getDb)):
    count=await currentCollection.count_documents({})
    return {"message":"success","count":count}

@app.get("/draftsInfo")
async def getDraftsInfo(startl:int=0,endl:int=None,currentCollection=Depends(getDb)):
    try:
        totalCount=await currentCollection.count_documents({})
        endl=endl or totalCount
        draftsCursor=currentCollection.find({},{"_id":0,"mdContent":0,"cachedHtml":0}).sort("publishTime",-1)
        drafts=await draftsCursor.to_list(length=endl)
        data=drafts[startl:endl]
        return {"message":"success","data":data}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})

@app.get("/draftBySlug")
async def getDraftBySlug(slug:str,currentCollection=Depends(getDb)):
    try:
        draft=await currentCollection.find_one({"slug":slug},{"_id":0})
        if draft is None: raise HTTPException(status_code=404,detail={"message":"fail","error":"draft not found"})
        return {"message":"success","data":draft}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})

@app.get("/draftSlugs")
async def getDraftSlugs(currentCollection=Depends(getDb)):
    try:
        draftCursor=currentCollection.find({},{"_id":0,"slug":1})
        drafts=await draftCursor.to_list(length=await currentCollection.count_documents({}))
        return {"message":"success","data":[i["slug"] for i in drafts]}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})

@app.get("/searchDraftsByTitleCount")
async def searchDraftsByTitleCount(title:str,currentCollection=Depends(getDb)):
    try:
        searchQuery={
            "title": {"$regex": title, "$options": "i"}
        }
        count=await currentCollection.count_documents(searchQuery)
        return {"message": "success", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})
        
@app.get("/searchDraftsByTitle")
async def searchDraftsByTitle(title:str,startl:int=0,endl:int=None,currentCollection=Depends(getDb)):
    try:
        searchQuery={
            "title": {"$regex": title, "$options": "i"}
        }
        draftsCursor=currentCollection.find(
            searchQuery,
            {
                "_id": 0,
                "mdContent": 0,
                "cachedHtml": 0,
                "plainContent": 0,
            }
        ).sort("publishTime",-1)
        cursor=draftsCursor.skip(startl)
        if endl is not None:
            cursor=cursor.limit(endl-startl)
        drafts=await cursor.to_list(length=None)
        return {"message": "success", "data": drafts}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})