from fastapi import APIRouter,Depends
import motor.motor_asyncio as motor
import os
from pydantic import BaseModel

class PushRenderedHtmlCacheRequestBody(BaseModel):
    slug:str
    html:str

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Posts"]

@app.post("/pushRenderedHtmlCache")
async def pushRenderedHtmlCache(body:PushRenderedHtmlCacheRequestBody,currentCollection=Depends(getDb)):
    try:
        await currentCollection.update_one({"slug":body.slug},{"$set":{"cachedHtml":body.html}})
        return {"message": "success"}
    except Exception as e:
        return {"message": "fail", "error": str(e)}