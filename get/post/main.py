from fastapi import APIRouter, Depends, HTTPException
import motor.motor_asyncio as motor
import os, random, re, httpx
from datetime import datetime, timedelta

app = APIRouter()
SF_TOKEN = os.environ.get("SF_TOKEN")

async def getDb():
    mongoClient = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["Posts"]


async def getSummaryDb():
    mongoClient = motor.AsyncIOMotorClient(
        os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
    )
    return mongoClient[os.getenv("DB_NAME") or "AriaBlogNext"]["PostSummary"]


@app.get("/postCount")
async def getPostCount(currentCollection=Depends(getDb)):
    count = await currentCollection.count_documents({})
    return {"message": "success", "count": count}


@app.get("/postsInfo")
async def getPostsInfo(
    startl: int = 0, endl: int = None, type="part", currentCollection=Depends(getDb)
):
    try:
        totalCount = await currentCollection.count_documents({})
        endl = endl or totalCount
        if type == "full":
            postsCursor = currentCollection.find({}, {"_id": 0}).sort("publishTime", -1)
        else:
            postsCursor = currentCollection.find(
                {}, {"_id": 0, "mdContent": 0, "cachedHtml": 0}
            ).sort("publishTime", -1)
        posts = await postsCursor.to_list(length=endl)
        data = [
            (
                {**post, "plainContent": post["plainContent"][:201]}
                if "plainContent" in post
                else post
            )
            for post in posts[startl:endl]
        ]
        return {"message": "success", "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/postBySlug")
async def getPostBySlug(slug: str, currentCollection=Depends(getDb)):
    try:
        post = await currentCollection.find_one({"slug": slug}, {"_id": 0})
        if post is None:
            raise HTTPException(
                status_code=404, detail={"message": "fail", "error": "post not found"}
            )
        return {"message": "success", "data": post}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/postSlugs")
async def getPostSlugs(currentCollection=Depends(getDb)):
    try:
        postCursor = currentCollection.find({}, {"_id": 0, "slug": 1})
        posts = await postCursor.to_list(
            length=await currentCollection.count_documents({})
        )
        return {"message": "success", "data": [i["slug"] for i in posts]}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/totalWordCount")
async def getTotalWordCount(currentCollection=Depends(getDb)):
    try:
        pipeline = [
            {"$group": {"_id": None, "totalWordCount": {"$sum": "$wordCount"}}},
            {"$project": {"_id": 0, "totalWordCount": 1}},
        ]
        result = await currentCollection.aggregate(pipeline).to_list(length=1)
        total_word_count = result[0]["totalWordCount"] if result else 0
        return {"message": "success", "count": total_word_count}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/postNavigation")
async def getPostNavigation(slug: str, currentCollection=Depends(getDb)):
    try:
        post = await currentCollection.find_one(
            {"slug": slug}, {"_id": 0, "publishTime": 1}
        )
        if not post:
            raise HTTPException(
                status_code=404, detail={"message": "fail", "error": "post not found"}
            )
        publishTime = post["publishTime"]
        nextPost = await currentCollection.find_one(
            {"publishTime": {"$lt": publishTime}},
            {"_id": 0, "slug": 1, "bannerImg": 1, "publishTime": 1, "title": 1},
            sort=[("publishTime", -1)],
        )
        previousPost = await currentCollection.find_one(
            {"publishTime": {"$gt": publishTime}},
            {"_id": 0, "slug": 1, "bannerImg": 1, "publishTime": 1, "title": 1},
            sort=[("publishTime", 1)],
        )
        return {
            "message": "success",
            "previous": previousPost if previousPost else None,
            "next": nextPost if nextPost else None,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/relatedPosts")
async def getRelatedPosts(slug: str, currentCollection=Depends(getDb)):
    try:
        post = await currentCollection.find_one({"slug": slug}, {"_id": 0, "tags": 1})
        if not post:
            raise HTTPException(
                status_code=404, detail={"message": "fail", "error": "post not found"}
            )
        tags = post["tags"]
        if not tags:
            raise HTTPException(
                status_code=404,
                detail={"message": "fail", "error": "no tags found for post"},
            )
        postsCursor = (
            currentCollection.find(
                {"tags": {"$in": tags}, "slug": {"$ne": slug}},
                {"_id": 0, "slug": 1, "bannerImg": 1, "publishTime": 1, "title": 1},
            )
            .sort("publishTime", -1)
            .limit(20)
        )
        posts = await postsCursor.to_list(length=20)
        random.shuffle(posts)
        return {"message": "success", "data": posts[:6]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/searchPosts")
async def searchPosts(query: str, currentCollection=Depends(getDb)):
    try:
        searchQuery = {
            "$or": [
                {"mdContent": {"$regex": query, "$options": "i"}},
                {"title": {"$regex": query, "$options": "i"}},
            ]
        }
        posts = (
            await currentCollection.find(
                searchQuery,
                {
                    "_id": 0,
                    "slug": 1,
                    "title": 1,
                    "publishTime": 1,
                    "bannerImg": 1,
                    "mdContent": 1,
                },
            )
            .sort("publishTime", -1)
            .to_list(length=None)
        )
        results = []
        for post in posts:
            mdContent = post.get("mdContent", "")
            title = post.get("title", "")
            textContent = re.sub(
                r"\*\*(.*?)\*\*|\*(.*?)\*|`(.*?)`|#|!\[.*?\]\(.*?\)|\[(.*?)\]\(.*?\)|$(.*?)$|{%(.*?)%}|<(.*?)>|~(.*?)~",
                lambda m: m.group(1)
                or m.group(2)
                or m.group(3)
                or m.group(4)
                or m.group(6)
                or "",
                mdContent,
            )
            contextIndex = textContent.lower().find(query.lower())
            context = ""
            if contextIndex != -1:
                start = max(contextIndex - 50, 0)
                end = min(contextIndex + 50, len(textContent))
                context = textContent[start:end]
            elif title.lower().find(query.lower()) != -1:
                context = title

            results.append(
                {
                    "slug": post["slug"],
                    "title": post["title"],
                    "publishTime": post["publishTime"],
                    "context": "..." + context + "...",
                }
            )
        return {"message": "success", "data": results}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/searchPostsByTitleCount")
async def searchPostsByTitleCount(title: str, currentCollection=Depends(getDb)):
    try:
        searchQuery = {"title": {"$regex": title, "$options": "i"}}
        count = await currentCollection.count_documents(searchQuery)
        return {"message": "success", "count": count}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/searchPostsByTitle")
async def searchPostsByTitle(
    title: str, startl: int = 0, endl: int = None, currentCollection=Depends(getDb)
):
    try:
        searchQuery = {"title": {"$regex": title, "$options": "i"}}
        postsCursor = currentCollection.find(
            searchQuery,
            {
                "_id": 0,
                "mdContent": 0,
                "cachedHtml": 0,
                "plainContent": 0,
            },
        ).sort("publishTime", -1)
        cursor = postsCursor.skip(startl)
        if endl is not None:
            cursor = cursor.limit(endl - startl)
        posts = await cursor.to_list(length=None)
        return {"message": "success", "data": posts}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/postSummary")
async def postSummary(
    slug: str,
    refresh: bool = False,
    currentCollection=Depends(getDb),
    currentSummaryCollection=Depends(getSummaryDb),
):
    try:
        if not refresh:
            cachedSummary = await currentSummaryCollection.find_one({"slug": slug})
            if cachedSummary is not None:
                return {"message": "success", "data": cachedSummary["summary"]}

        # 检查刷新限制
        cachedSummary = await currentSummaryCollection.find_one({"slug": slug})
        if cachedSummary and "lastRefreshTime" in cachedSummary:
            last_refresh = cachedSummary["lastRefreshTime"]
            if datetime.now() - last_refresh < timedelta(minutes=10):
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "fail",
                        "error": "请等待10分钟后再刷新摘要",
                        "nextRefreshTime": (
                            last_refresh + timedelta(minutes=10)
                        ).timestamp(),
                    },
                )

        post = await currentCollection.find_one({"slug": slug})
        if post is None:
            raise HTTPException(
                status_code=404,
                detail={"message": "fail", "error": "post not found"},
            )

        payload = {
            "model": "Qwen/Qwen3-8B",
            "messages": [
                {
                    "role": "user",
                    "content": "你是一位专业的作家，接下来请用精炼并平易近人而并不高深的语言，尽可能更可爱且女性化一些，不要做作，可以使用一些口语化的语气词，写一份一百字左右的文章总结，态度要与作者表达的所保持一致，尽可能不要有幻觉，遇到你所不确定的部分和敏感的（政治或是较负面情绪等内容）请略过而不要回答，而遇到一些晦涩的东西可以尝试解释，接下来给你的文章是markdown格式的，请输出纯文本并使用中文回答我，不要输出多余的内容，只输出文章摘要的正文，不要输出换行符和在编程语言中的非法文字。接下来是文章的正文内容：\n"
                    + post["mdContent"],
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {SF_TOKEN}",
            "Content-Type": "application/json",
        }
        response = httpx.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "fail",
                    "error": "api error:" + str(response.text),
                },
            )
        summary = response.json()["choices"][0]["message"]["content"]
        # 更新或插入摘要时包含刷新时间
        await currentSummaryCollection.update_one(
            {"slug": post["slug"]},
            {"$set": {"summary": summary, "lastRefreshTime": datetime.now()}},
            upsert=True,
        )
        return {"message": "success", "data": summary}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )
