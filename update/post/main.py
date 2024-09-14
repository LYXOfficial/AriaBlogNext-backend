from fastapi import APIRouter,Depends,HTTPException
import motor.motor_asyncio as motor
import os,jwt
from pydantic import BaseModel
from ..siteInfo.main import updateTime
SECRET_KEY=os.environ.get("SECRET")
ALGORITHM="HS256"

class PushRenderedHtmlCacheRequestBody(BaseModel):
    slug:str
    html:str
    secret:str

class DeletePostRequestBody(BaseModel):
    slug:str
    token:str

class UpdatePostRequestBody(BaseModel):
    token:str
    slug:str
    title:str
    description:str
    category:str
    tags:list[str]
    coverFit:str
    bannerImg:str
    publishTime:str
    lastUpdatedTime:str

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Posts"]

@app.post("/pushRenderedHtmlCache")
async def pushRenderedHtmlCache(body:PushRenderedHtmlCacheRequestBody,currentCollection=Depends(getDb)):
    try:
        if body.secret!=os.environ.get("SECRET"):
            return {"message": "fail", "error": "access failed"}
        await currentCollection.update_one({"slug":body.slug},{"$set":{"cachedHtml":body.html}})
        return {"message": "success"}
    except Exception as e:
        return {"message": "fail", "error": str(e)}
    
@app.delete("/deleteRenderedHtmlCache")
async def deleteRenderedHtmlCache(slug:str,currentCollection=Depends(getDb)):
    try:
        await currentCollection.update_one({"slug":slug},{"$unset":{"cachedHtml":""}})
        return {"message": "success"}
    except Exception as e:
        return {"message": "fail", "error": str(e)}
@app.delete("/deletePost")
async def deletePost(body:DeletePostRequestBody,currentCollection=Depends(getDb)):
    try:
        try:
            jwt.decode(body.token,SECRET_KEY,algorithms=[ALGORITHM])
        except Exception as e:
            raise HTTPException(status_code=401, detail="access failed")
        await currentCollection.delete_one({"slug":body.slug})
        return {"message": "success"}
    except Exception as e:
        return {"message": "fail", "error": str(e)}
@app.put("/updatePostInfo")
async def updatePostInfo(body:UpdatePostRequestBody,currentCollection=Depends(getDb)):
    try:
        try:
            jwt.decode(body.token,SECRET_KEY,algorithms=[ALGORITHM])
        except Exception as e:
            raise HTTPException(status_code=401, detail="access failed")
        await currentCollection.update_one({"slug":body.slug},{
            "$set":{
                "title":body.title,
                "category":body.category,
                "bannerImg":body.bannerImg,
                "description":body.description,
                "coverFit":body.coverFit,
                "tags":body.tags,
                "publishTime":body.publishTime,
                "lastUpdatedTime":body.lastUpdatedTime,
            }
        })
        return {"message": "success"}
    except Exception as e:
        return {"message": "fail", "error": str(e)}