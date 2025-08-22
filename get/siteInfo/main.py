from fastapi import APIRouter, Depends, HTTPException
import motor.motor_asyncio as motor
import os

app = APIRouter()


async def getDb():
    mongoClient = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["webSiteInfo"]


@app.get("/lastUpdateTime")
async def getLatestUpdateTime(currentCollection=Depends(getDb)):
    try:
        time = int(
            (await currentCollection.find_one({"key": "latestUpdateTime"}, {"_id": 0}))[
                "value"
            ]
        )
        return {"message": "success", "time": time}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )
