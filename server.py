import uvicorn,os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
os.environ["TZ"]="Asia/Shanghai"
from get.post.main import app as appPost
from get.siteInfo.main import app as appSiteInfo
from get.tag.main import app as appTag
from get.category.main import app as appCategory
from get.archive.main import app as appArchive

app = FastAPI()

app.include_router(appPost,prefix='/get/post')
app.include_router(appSiteInfo,prefix='/get/siteInfo')
app.include_router(appTag,prefix='/get/tag')
app.include_router(appCategory,prefix='/get/category')
app.include_router(appArchive,prefix='/get/archive')

if __name__ == '__main__':
    uvicorn.run(app="server:app", host='0.0.0.0', port=2333, reload=True)