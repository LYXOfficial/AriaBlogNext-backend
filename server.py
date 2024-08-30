import uvicorn,os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
os.environ["TZ"]="Asia/Shanghai"
from get.post.main import app as appGetPost
from get.siteInfo.main import app as appGetSiteInfo
from get.tag.main import app as appGetTag
from get.category.main import app as appGetCategory
from get.archive.main import app as appGetArchive

from update.post.main import app as appUpdatePost


app = FastAPI()

app.include_router(appGetPost,prefix='/get/post')
app.include_router(appGetSiteInfo,prefix='/get/siteInfo')
app.include_router(appGetTag,prefix='/get/tag')
app.include_router(appGetCategory,prefix='/get/category')
app.include_router(appGetArchive,prefix='/get/archive')

app.include_router(appUpdatePost,prefix='/update/post')

if __name__ == '__main__':
    uvicorn.run(app="server:app", host='0.0.0.0', port=2333, reload=True)