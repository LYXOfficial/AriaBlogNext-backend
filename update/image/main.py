from fastapi import APIRouter,Depends,HTTPException,UploadFile,Header,File
import os,jwt,httpx
SECRET_KEY=os.environ.get("SECRET")
ALGORITHM="HS256"
QBU_TOKEN=os.environ.get("QBU_TOKEN")
app=APIRouter()
async def verify(authorization: str=Header(None)):
    if not authorization:
        raise HTTPException(status_code=401,detail="Authorization header missing")
    token=authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid token")
async def upload(url,body,headers):
    async with httpx.AsyncClient() as client:
        response=await client.post(url,files=body,headers=headers)
        return response.json()
@app.post("/uploadImage")
async def uploadImage(file:UploadFile=File(...),user=Depends(verify)):
    try:
        headers={
            "Content-Type":"multipart/form-data",
            "Authorization":QBU_TOKEN,
            "Accept":"application/json",
        }
        body={"file":(file.filename,await file.read(),file.content_type)}
        return {"message":"success","data":await upload("https://7bu.top/api/v1/upload",body,headers)}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail={"message":"fail","error":str(e)})