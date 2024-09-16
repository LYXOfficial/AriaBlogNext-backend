from fastapi import APIRouter,Depends,HTTPException
import motor.motor_asyncio as motor
import os,jwt,re
from pydantic import BaseModel
from ..siteInfo.main import updateTime
SECRET_KEY=os.environ.get("SECRET")
ALGORITHM="HS256"

class PushRenderedHtmlCacheRequestBody(BaseModel):
    slug:str
    html:str
    secret:str

class DeleteDraftRequestBody(BaseModel):
    slug:str
    token:str

class UpdateDraftRequestBody(BaseModel):
    token:str
    slug:str
    title:str
    description:str|None
    category:str
    tags:list[str]
    coverFit:str|None
    bannerImg:str|None
    publishTime:int
    lastUpdatedTime:int

class UpdateDraftMarkdownBody(BaseModel):
    token:str
    slug:str
    markdown:str

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Drafts"]

@app.delete("/deleteDraft")
async def deleteDraft(body:DeleteDraftRequestBody,currentCollection=Depends(getDb)):
    try:
        try:
            jwt.decode(body.token,SECRET_KEY,algorithms=[ALGORITHM])
        except Exception as e:
            raise HTTPException(status_code=401, detail="access failed")
        await currentCollection.delete_one({"slug":body.slug})
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})
@app.put("/updateDraftInfo")
async def updateDraftInfo(body:UpdateDraftRequestBody,currentCollection=Depends(getDb)):
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
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})
@app.put("/updateDraftMarkdown")
async def updateDraftMarkdown(body:UpdateDraftMarkdownBody,currentCollection=Depends(getDb)):
    try:
        try:
            jwt.decode(body.token,SECRET_KEY,algorithms=[ALGORITHM])
        except Exception as e:
            raise HTTPException(status_code=401, detail="access failed")
        wordCount=len(re.findall(r'\b\w+\b',body.markdown)+re.findall(r'[\u4e00-\u9fff]',body.markdown))
        await currentCollection.update_one({"slug":body.slug},{
            "$set":{
                "mdContent":body.markdown,
                "cachedHtml":None,
                "wordCount":wordCount,
            }
        })
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})
@app.post("/addDraft")
async def addDraft(body:UpdateDraftRequestBody,currentCollection=Depends(getDb)):
    try:
        try:
            jwt.decode(body.token,SECRET_KEY,algorithms=[ALGORITHM])
        except Exception as e:
            raise HTTPException(status_code=401, detail="access failed")
        if await currentCollection.count_documents({"slug":body.slug})>0:
            raise HTTPException(status_code=409, detail="slug already exists")
        else:
            await currentCollection.insert_one({
                "title":body.title,
                "category":body.category,
                "bannerImg":body.bannerImg,
                "description":body.description,
                "coverFit":body.coverFit,
                "tags":body.tags,
                "publishTime":body.publishTime,
                "lastUpdatedTime":body.lastUpdatedTime,
                "slug":body.slug,
            })
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})