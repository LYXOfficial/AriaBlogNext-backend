from fastapi import APIRouter,Depends,Response,status
import motor.motor_asyncio as motor
import xml.etree.ElementTree as ET
import os,datetime

app=APIRouter()

async def getDb():
    mongoClient=motor.AsyncIOMotorClient(os.environ.get("MONGODB_URI") or "mongodb://localhost:27017")
    return mongoClient["AriaBlogNext"]["Posts"]

@app.get("/sitemapGen")
async def getPostsInfo(currentCollection=Depends(getDb),response=Response):
    try:
        root=ET.Element("urlset")
        root.set("xmlns","http://www.sitemaps.org/schemas/sitemap/0.9")
        for post in await currentCollection.find({},{"_id":0,"mdContent":0,"cachedHtml":0}).sort("publishTime",-1).to_list(length=None):
            url=ET.SubElement(root,"url")
            ET.SubElement(url,"loc").text=f"https://blog.yaria.top/posts/{post['slug']}"
            ET.SubElement(url,"lastmod").text=datetime.datetime.fromtimestamp(post["lastUpdatedTime"]).strftime("%Y-%m-%d")
            ET.SubElement(url,"changefreq").text="daily"
            ET.SubElement(url,"priority").text="0.8"
        url=ET.SubElement(root,"url")
        ET.SubElement(url,"loc").text="https://blog.yaria.top"
        ET.SubElement(url,"lastmod").text=datetime.datetime.now().strftime("%Y-%m-%d")
        ET.SubElement(url,"changefreq").text="daily"
        ET.SubElement(url,"priority").text="1.0"
        url=ET.SubElement(root,"url")
        ET.SubElement(url,"loc").text="https://blog.yaria.top/speaks"
        ET.SubElement(url,"lastmod").text=datetime.datetime.now().strftime("%Y-%m-%d")
        ET.SubElement(url,"changefreq").text="daily"
        ET.SubElement(url,"priority").text="0.6"
        url=ET.SubElement(root,"url")
        ET.SubElement(url,"loc").text="https://blog.yaria.top/links"
        ET.SubElement(url,"lastmod").text=datetime.datetime.now().strftime("%Y-%m-%d")
        ET.SubElement(url,"changefreq").text="daily"
        ET.SubElement(url,"priority").text="0.8"
        data=ET.tostring(root,encoding="utf-8",method="xml").decode("utf-8")
        return Response(content=data, media_type="application/xml")
    except Exception as e:
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"fail","error":str(e)}