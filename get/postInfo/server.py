from fastapi import APIRouter
app = APIRouter()
@app.get("/getPostInfos")
async def getPostInfos():
    return {"message": "Hello World"}