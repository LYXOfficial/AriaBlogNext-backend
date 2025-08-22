from fastapi import APIRouter, Depends, HTTPException
import motor.motor_asyncio as motor
import os
from datetime import datetime

app = APIRouter()


async def getDb():
    mongoClient = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["Posts"]


@app.get("/archiveInfo")
async def getArchiveInfo(
    year: int,
    month: int,
    startl: int = 0,
    endl: int = None,
    currentCollection=Depends(getDb),
):
    try:
        start_date = datetime(year, month, 1).timestamp()
        end_date = (
            datetime(year + 1, 1, 1).timestamp()
            if month == 12
            else datetime(year, month + 1, 1).timestamp()
        )
        totalCount = await currentCollection.count_documents(
            {"publishTime": {"$gte": start_date, "$lt": end_date}}
        )
        endl = endl or totalCount
        resl = (
            await currentCollection.find(
                {"publishTime": {"$gte": start_date, "$lt": end_date}},
                {"_id": 0, "mdContent": 0, "plainContent": 0, "cachedHtml": 0},
            )
            .sort("publishTime", -1)
            .to_list(length=endl)
        )
        if not resl:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "fail",
                    "error": "No posts found for the specified date range",
                },
            )
        return {
            "message": "success",
            "data": resl[startl:endl],
            "totalCount": totalCount,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/archives")
async def getArchives(currentCollection=Depends(getDb)):
    try:
        pipeline = [
            {
                "$addFields": {
                    "publishTime": {"$toDate": {"$multiply": ["$publishTime", 1000]}}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$publishTime"},
                        "month": {"$month": "$publishTime"},
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id.year": -1, "_id.month": -1}},
        ]
        results = await currentCollection.aggregate(pipeline).to_list(length=None)
        return {
            "message": "success",
            "data": [
                {
                    "year": r["_id"]["year"],
                    "month": r["_id"]["month"],
                    "count": r["count"],
                }
                for r in results
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )
