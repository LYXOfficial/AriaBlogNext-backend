import uvicorn,os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
os.environ["TZ"]="Asia/Shanghai"
from get.post.main import app as appGetPost
from get.siteInfo.main import app as appGetSiteInfo
from get.tag.main import app as appGetTag
from get.category.main import app as appGetCategory
from get.archive.main import app as appGetArchive
from get.flink.main import app as appGetFlink
from get.speaks.main import app as appGetSpeaks
from get.sitemap.main import app as appGetSitemap
from get.draft.main import app as appGetDraft

from update.post.main import app as appUpdatePost
from update.draft.main import app as appUpdateDraft
from update.siteInfo.main import app as appUpdateSiteInfo

from access.user.main import app as appUserLogin

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(appGetPost,prefix='/get/post')
app.include_router(appGetSiteInfo,prefix='/get/siteInfo')
app.include_router(appGetTag,prefix='/get/tag')
app.include_router(appGetCategory,prefix='/get/category')
app.include_router(appGetArchive,prefix='/get/archive')
app.include_router(appGetFlink,prefix='/get/flink')
app.include_router(appGetSpeaks,prefix='/get/speaks')
app.include_router(appGetSitemap,prefix='/get/sitemap')
app.include_router(appGetDraft,prefix='/get/draft')

app.include_router(appUpdatePost,prefix='/update/post')
app.include_router(appUpdateSiteInfo,prefix='/update/siteInfo')
app.include_router(appUpdateDraft,prefix='/update/draft')

app.include_router(appUserLogin,prefix='/access/user')

if __name__ == '__main__':
    uvicorn.run(app="server:app", host='0.0.0.0', port=2333, reload=True)