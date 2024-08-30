from fastapi import APIRouter, Depends
import motor.motor_asyncio as motor
import os
from datetime import datetime

app = APIRouter()

async def getDb():
    mongoClient = motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Posts"]

@app.get("/archiveInfo")
async def getArchiveInfo(year: int, month: int, startl: int = 0, endl: int = None, currentCollection=Depends(getDb)):
    try:
        # 设置查询的时间范围
        start_date = datetime(year, month, 1).timestamp()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).timestamp()
        else:
            end_date = datetime(year, month + 1, 1).timestamp()
        
        # 计算符合条件的文档总数
        totalCount = await currentCollection.count_documents({
            "publishTime": {"$gte": start_date, "$lt": end_date}
        })
        endl = endl or totalCount
        
        # 查询特定时间范围内的文章
        resl = await currentCollection.find(
            {"publishTime": {"$gte": start_date, "$lt": end_date}},
            {"_id": 0, "mdContent": 0, "plainContent": 0,"cachedHtml":0}
        ).sort("publishTime", -1).to_list(length=endl)
        
        if not resl:
            return {"message": "fail", "error": "No posts found for the specified date range"}
        
        data = resl[startl:endl]
        return {"message": "success", "data": data, "totalCount": totalCount}
    
    except Exception as e:
        return {"message": "fail", "error": str(e)}
@app.get("/archives")
async def getArchives(currentCollection=Depends(getDb)):
    try:
        pipeline = [
            {"$addFields": {"publishTime": {"$toDate": {"$multiply": ["$publishTime", 1000]}}}},
            {"$group": {"_id": {"year": {"$year": "$publishTime"}, "month": {"$month": "$publishTime"}}, "count": {"$sum": 1}}},
            {"$sort": {"_id.year": -1, "_id.month": -1}}
        ]
        results = await currentCollection.aggregate(pipeline).to_list(length=None)
        return {"message": "success", "data": [{"year": r["_id"]["year"], "month": r["_id"]["month"], "count": r["count"]} for r in results]}
    except Exception as e:
        return {"message": "fail", "error": str(e)}