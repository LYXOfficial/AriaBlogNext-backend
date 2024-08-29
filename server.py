import uvicorn
from fastapi import FastAPI

from get.postInfo.server import app as appPostInfo

app = FastAPI()

app.include_router(appPostInfo,prefix='/get/postInfo',)

if __name__ == '__main__':
    uvicorn.run(app="server:app", host='0.0.0.0', port=2333, workers=2)