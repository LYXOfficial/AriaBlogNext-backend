from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, Header, File
import os
import jwt
import boto3
import secrets
from datetime import datetime
import asyncio
from urllib.parse import urlparse
from typing import List
import re

# env
SECRET_KEY = os.environ.get("SECRET")
ALGORITHM = "HS256"

S3_ENDPOINT = os.environ.get(
    "S3_ENDPOINT"
)  # e.g. https://<account>.r2.cloudflarestorage.com
S3_ACCESSKEYID = os.environ.get("S3_ACCESSKEYID")
S3_SECRETACCESSKEY = os.environ.get("S3_SECRETACCESSKEY")
S3_REGION = os.environ.get("S3_REGION")  # optional
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PUBLIC_URL = os.environ.get("S3_PUBLIC_URL")

app = APIRouter()


# 删除文件
async def s3_delete_object(key: str):
    def _delete():
        client_kwargs = dict(
            aws_access_key_id=S3_ACCESSKEYID,
            aws_secret_access_key=S3_SECRETACCESSKEY,
        )
        if S3_REGION:
            client_kwargs["region_name"] = S3_REGION
        if S3_ENDPOINT:
            client_kwargs["endpoint_url"] = S3_ENDPOINT

        s3 = boto3.client("s3", **client_kwargs)
        return s3.delete_object(Bucket=S3_BUCKET, Key=key)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _delete)


async def verify(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.delete("/deleteImage")
async def delete_image(url: str, user=Depends(verify)):
    try:
        # 从 URL 提取 key
        parsed = urlparse(url)
        # public url 可能是 https://example.com/bucket/key，所以只取 path
        key = parsed.path.lstrip("/")
        # 如果 PUBLIC_URL 已经包含 bucket name，则 key 会是 yyyy/mm/dd/file.ext
        # 如果不是，则需要移除 bucket name 部分
        if key.startswith(f"{S3_BUCKET}/"):
            key = key[len(S3_BUCKET) + 1 :]

        await s3_delete_object(key)
        return {"message": "success", "data": {"deleted": url}}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


# 获取文件列表
async def s3_list_objects() -> List[str]:
    def _list():
        client_kwargs = dict(
            aws_access_key_id=S3_ACCESSKEYID,
            aws_secret_access_key=S3_SECRETACCESSKEY,
        )
        if S3_REGION:
            client_kwargs["region_name"] = S3_REGION
        if S3_ENDPOINT:
            client_kwargs["endpoint_url"] = S3_ENDPOINT

        s3 = boto3.client("s3", **client_kwargs)
        paginator = s3.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=S3_BUCKET)

        objects = []
        allowed_exts = tuple(CONTENT_TYPE_EXT.values())
        date_pattern = re.compile(r"^(\d{4})/(\d{2})/(\d{2})/")

        for page in page_iterator:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.lower().endswith(allowed_exts):
                    # 提取日期
                    m = date_pattern.match(key)
                    if m:
                        obj["_date"] = (
                            int(m.group(1)),
                            int(m.group(2)),
                            int(m.group(3)),
                        )
                    else:
                        obj["_date"] = None
                    objects.append(obj)

        def sort_key(obj):
            if obj["_date"]:
                # 有日期的，按日期+LastModified倒序
                date_dt = datetime(obj["_date"][0], obj["_date"][1], obj["_date"][2])
            else:
                # 没有日期的，用LastModified的日期
                lm = obj["LastModified"]
                date_dt = datetime(lm.year, lm.month, lm.day)
            # 排序键：日期时间戳 + LastModified时间戳
            return (date_dt.timestamp(), obj["LastModified"].timestamp())

        objects.sort(key=sort_key, reverse=True)
        results = [f"{S3_PUBLIC_URL.rstrip('/')}/{obj['Key']}" for obj in objects]
        return results

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _list)


@app.get("/listImages")
async def list_images(user=Depends(verify)):
    try:
        urls = await s3_list_objects()
        return {"message": "success", "data": {"images": urls}}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


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
        rand_hex = secrets.token_hex(7)[
            :13
        ]  # token_hex(7) => 14 hex chars, slice to 13
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
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.put("/reuploadImage")
async def reupload_image(
    url: str = Form(...), file: UploadFile = File(...), user=Depends(verify)
):
    try:
        # 校验文件类型
        content_type = (file.content_type or "").lower()
        ext = CONTENT_TYPE_EXT.get(content_type)
        if not ext:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # 提取 key
        parsed = urlparse(url)
        key = parsed.path.lstrip("/")
        if key.startswith(f"{S3_BUCKET}/"):
            key = key[len(S3_BUCKET) + 1 :]

        # 读取新文件内容
        body_bytes = await file.read()

        # 上传覆盖
        await s3_put_object(key=key, body=body_bytes, content_type=content_type)

        url = f"{S3_PUBLIC_URL.rstrip('/')}/{key}"
        return {"message": "success", "data": {"data": {"links": {"url": url}}}}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )
