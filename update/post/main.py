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

class DeletePostRequestBody(BaseModel):
    slug:str
    token:str

class UpdatePostRequestBody(BaseModel):
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

class UpdatePostMarkdownBody(BaseModel):
    token:str
    slug:str
    markdown:str
def clean_markdown(text):
    # 移除Markdown语法中的符号
    cleaned_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # 粗体 **text** 或 __text__
    cleaned_text = re.sub(r'(\*|_)(.*?)\1', r'\2', cleaned_text)  # 斜体 *text* 或 _text_
    cleaned_text = re.sub(r'(~~)(.*?)\1', r'\2', cleaned_text)  # 删除线 ~~text~~
    cleaned_text = re.sub(r'`{1,2}(.*?)`{1,2}', r'\1', cleaned_text)  # 行内代码 `code`
    cleaned_text = re.sub(r'```[\s\S]*?```', '', cleaned_text)  # 代码块 ```code```
    cleaned_text = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned_text)  # 图片 ![alt](url)
    cleaned_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', cleaned_text)  # 链接 [text](url)
    cleaned_text = re.sub(r'^\s{0,3}>\s?', '', cleaned_text, flags=re.M)  # 引用 >
    cleaned_text = re.sub(r'^\s{0,3}[-*+]\s', '', cleaned_text, flags=re.M)  # 无序列表 - * +
    cleaned_text = re.sub(r'^\s{0,3}\d+\.\s', '', cleaned_text, flags=re.M)  # 有序列表 1. 2. 3.
    cleaned_text = re.sub(r'^#{1,6}\s?', '', cleaned_text, flags=re.M)  # 标题 # ## ### 等
    cleaned_text = re.sub(r'^\s*\|.*?\|\s*$', '', cleaned_text, flags=re.M)  # 表格 | col1 | col2 |
    cleaned_text = re.sub(r'^-{3,}$', '', cleaned_text, flags=re.M)  # 分隔线 ---
    cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)  # 多余的换行

    # 去除文本开头和结尾的多余换行
    return cleaned_text.strip()
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
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})
    
@app.delete("/deleteRenderedHtmlCache")
async def deleteRenderedHtmlCache(slug:str,currentCollection=Depends(getDb)):
    try:
        await currentCollection.update_one({"slug":slug},{"$unset":{"cachedHtml":""}})
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})
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
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})
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
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})
@app.put("/updatePostMarkdown")
async def updatePostMarkdown(body:UpdatePostMarkdownBody,currentCollection=Depends(getDb)):
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
                "plainContent": clean_markdown(body.markdown).replace("\n"," "),
            }
        })
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "internal server error", "error": str(e)})
@app.post("/addPost")
async def addPost(body:UpdatePostRequestBody,currentCollection=Depends(getDb)):
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