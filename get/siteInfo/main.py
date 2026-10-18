from fastapi import APIRouter, Depends, HTTPException
import motor.motor_asyncio as motor
import os

from db import get_database

app = APIRouter()


async def getDb():
    return get_database()["webSiteInfo"]


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
