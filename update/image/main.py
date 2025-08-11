from fastapi import APIRouter, Depends, HTTPException, UploadFile, Header, File
import os
import jwt
import boto3
import secrets
from datetime import datetime
import asyncio

# env
SECRET_KEY = os.environ.get("SECRET")
ALGORITHM = "HS256"

S3_ENDPOINT = os.environ.get("S3_ENDPOINT")  # e.g. https://<account>.r2.cloudflarestorage.com
S3_ACCESSKEYID = os.environ.get("S3_ACCESSKEYID")
S3_SECRETACCESSKEY = os.environ.get("S3_SECRETACCESSKEY")
S3_REGION = os.environ.get("S3_REGION")  # optional
S3_BUCKET = os.environ.get("S3_BUCKET")

# derived public base url used in response (you can override this to a CDN domain if you have one)
if S3_ENDPOINT:
    S3_PUBLIC_URL = f"{S3_ENDPOINT.rstrip('/')}/{S3_BUCKET}"
else:
    S3_PUBLIC_URL = f"https://{S3_BUCKET}.s3.amazonaws.com"

app = APIRouter()

async def verify(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# helper to upload to s3 (blocking boto3 put_object run in threadpool)
async def s3_put_object(key: str, body: bytes, content_type: str):
    # create client inside worker to avoid issues with pickling / event loop
    def _put():
        kwargs = dict(
            Bucket=S3_BUCKET,
            Key=key,
            Body=body,
            ContentType=content_type,
            ACL="public-read",  # attempt to make object publicly readable
        )
        client_kwargs = dict(
            aws_access_key_id=S3_ACCESSKEYID,
            aws_secret_access_key=S3_SECRETACCESSKEY,
        )
        if S3_REGION:
            client_kwargs["region_name"] = S3_REGION
        if S3_ENDPOINT:
            client_kwargs["endpoint_url"] = S3_ENDPOINT

        s3 = boto3.client("s3", **client_kwargs)
        # use put_object to upload bytes
        return s3.put_object(**kwargs)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _put)

# map content-type to extension (allowed types)
CONTENT_TYPE_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

@app.post("/uploadImage")
async def uploadImage(file: UploadFile = File(...), user=Depends(verify)):
    try:
        # validate content type
        content_type = (file.content_type or "").lower()
        ext = CONTENT_TYPE_EXT.get(content_type)
        if not ext:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # generate path: yyyy/mm/dd/13hex.ext
        now = datetime.utcnow()
        yyyy = now.strftime("%Y")
        mm = now.strftime("%m")
        dd = now.strftime("%d")

        # generate 13 hex chars
        rand_hex = secrets.token_hex(7)[:13]  # token_hex(7) => 14 hex chars, slice to 13
        key = f"{yyyy}/{mm}/{dd}/{rand_hex}.{ext}"

        # read bytes
        body = await file.read()

        # upload to S3 (in threadpool)
        await s3_put_object(key=key, body=body, content_type=content_type)

        # construct public url
        # S3_PUBLIC_URL was computed as endpoint + /bucket; final url is {S3_PUBLIC_URL}/{key}
        url = f"{S3_PUBLIC_URL.rstrip('/')}/{key}"

        # return the strict structure you requested
        return {"message": "success", "data": {"data": {"links": {"url": url}}}}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "fail", "error": str(e)})
