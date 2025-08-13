from fastapi import APIRouter, Depends, HTTPException
import motor.motor_asyncio as motor
import os
from pydantic import BaseModel

app = APIRouter()
SECRET_KEY = os.environ.get("SECRET")

class ExportCollectionsRequestBody(BaseModel):
    secret: str

async def get_db():
    mongo_client = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongo_client[os.getenv("DB_NAME") or "AriaBlogNext"]

@app.post("/collections")
async def export_collections(body: ExportCollectionsRequestBody, db=Depends(get_db)):
    if body.secret != SECRET_KEY:
        raise HTTPException(status_code=403, detail={"message": "fail", "error": "invalid secret key"})

    try:
        collections_data = {}
        collection_names = await db.list_collection_names()

        for name in collection_names:
            docs = await db[name].find().to_list(length=None)
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            collections_data[name]=docs

        return {"message": "success", "collections": collections_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})
