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

class UpdateDraftRequestBody(BaseModel):
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
    slug:str
    markdown:str
def clean_markdown(text):
    cleaned_text=re.sub(r'(\*\*|__)(.*?)\1',r'\2',text)
    cleaned_text=re.sub(r'(\*|_)(.*?)\1',r'\2',cleaned_text)
    cleaned_text=re.sub(r'(~~)(.*?)\1',r'\2',cleaned_text)
    cleaned_text=re.sub(r'`{1,2}(.*?)`{1,2}',r'\1',cleaned_text)
    cleaned_text=re.sub(r'```[\s\S]*?```','',cleaned_text)
    cleaned_text=re.sub(r'!\[.*?\]\(.*?\)','',cleaned_text)
    cleaned_text=re.sub(r'\[(.*?)\]\(.*?\)',r'\1',cleaned_text)
    cleaned_text=re.sub(r'^\s{0,3}>\s?','',cleaned_text,flags=re.M)
    cleaned_text=re.sub(r'^\s{0,3}[-*+]\s','',cleaned_text,flags=re.M)
    cleaned_text=re.sub(r'^\s{0,3}\d+\.\s','',cleaned_text,flags=re.M)
    cleaned_text=re.sub(r'^#{1,6}\s?','',cleaned_text,flags=re.M)
    cleaned_text=re.sub(r'^\s*\|.*?\|\s*$','',cleaned_text,flags=re.M)
    cleaned_text=re.sub(r'^-{3,}$','',cleaned_text,flags=re.M)
    cleaned_text=re.sub(r'\n{2,}','\n',cleaned_text)

    return cleaned_text.strip()
app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Drafts"]
from fastapi import Header,HTTPException,Depends

async def verify(authorization: str=Header(None)):
    if not authorization:
        raise HTTPException(status_code=401,detail="Authorization header missing")
    token=authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid token")
@app.post("/pushRenderedHtmlCache")
async def pushRenderedHtmlCache(body:PushRenderedHtmlCacheRequestBody,currentCollection=Depends(getDb)):
    try:
        if body.secret!=os.environ.get("SECRET"):
            return {"message": "fail","error": "access failed"}
        await currentCollection.update_one({"slug":body.slug},{"$set":{"cachedHtml":body.html}})
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message": "internal server error","error": str(e)})
    
@app.delete("/deleteRenderedHtmlCache")
async def deleteRenderedHtmlCache(slug:str,currentCollection=Depends(getDb)):
    try:
        await currentCollection.update_one({"slug":slug},{"$unset":{"cachedHtml":""}})
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message": "internal server error","error": str(e)})
@app.delete("/deleteDraft")
async def deleteDraft(body:DeleteDraftRequestBody,currentCollection=Depends(getDb)):
    try:
        await currentCollection.delete_one({"slug":body.slug})
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message": "internal server error","error": str(e)})
@app.put("/updateDraftInfo")
async def updateDraftInfo(body:UpdateDraftRequestBody,currentCollection=Depends(getDb),user=Depends(verify)):
    try:
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
        raise HTTPException(status_code=500,detail={"message": "internal server error","error": str(e)})
@app.put("/updateDraftMarkdown")
async def updateDraftMarkdown(body:UpdateDraftMarkdownBody,currentCollection=Depends(getDb),user=Depends(verify)):
    try:
        wordCount=len(re.findall(r'\b\w+\b',body.markdown)+re.findall(r'[\u4e00-\u9fff]',body.markdown))
        await currentCollection.update_one({"slug":body.slug},{
            "$set":{
                "mdContent":body.markdown,
                "cachedHtml":None,
                "wordCount":wordCount,
                "plainContent": clean_markdown(body.markdown).replace("\n"," "),
            }
        })
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message": "internal server error","error": str(e)})
@app.post("/addDraft")
async def addDraft(body:UpdateDraftRequestBody,currentCollection=Depends(getDb),user=Depends(verify)):
    try:
        if await currentCollection.count_documents({"slug":body.slug})>0:
            raise HTTPException(status_code=409,detail="slug already exists")
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
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message": "internal server error","error": str(e)})