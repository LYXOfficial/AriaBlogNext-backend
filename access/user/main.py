from fastapi import APIRouter, Depends, HTTPException, Header, Request
import motor.motor_asyncio as motor
import os, jwt, hashlib, time
from pydantic import BaseModel
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get("SECRET")
ALGORITHM = "HS256"

from db import get_database

app = APIRouter()

# ---- 进程内登录爆破防护 ----
# Vercel 无状态多实例下该计数按进程独立;能挡住大部分单点爆破,如需跨实例可换 Mongo/Redis。
_FAIL_LIMIT = 5             # 时间窗内允许的连续失败次数
_LOCK_SECONDS = 600         # 超限后的锁定时间(秒)
_failures: dict[str, tuple[int, float]] = {}  # ip -> (连续失败次数, 最近失败时间戳)


def _client_ip(request: Request) -> str:
    """反代/Vercel 场景取 X-Forwarded-For 第一跳,否则回退直连地址。"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _prune(now: float):
    """清理超窗记录,防止字典无限增长。"""
    expired = [ip for ip, (_, ts) in _failures.items() if now - ts >= _LOCK_SECONDS]
    for ip in expired:
        _failures.pop(ip, None)


def _is_locked(ip: str) -> bool:
    now = time.time()
    if len(_failures) > 10_000:  # 仅在膨胀时顺带清理
        _prune(now)
    entry = _failures.get(ip)
    if not entry:
        return False
    count, ts = entry
    if count >= _FAIL_LIMIT and now - ts < _LOCK_SECONDS:
        return True
    if now - ts >= _LOCK_SECONDS:
        _failures.pop(ip, None)
    return False


def _record_failure(ip: str):
    now = time.time()
    entry = _failures.get(ip)
    if not entry or now - entry[1] >= _LOCK_SECONDS:
        _failures[ip] = (1, now)
    else:
        _failures[ip] = (entry[0] + 1, now)


def _clear_failures(ip: str):
    _failures.pop(ip, None)


class LoginRequestBody(BaseModel):
    user: str
    password: str


async def getDb():
    return get_database()["Users"]


async def verify(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/login")
async def login(
    data: LoginRequestBody,
    request: Request,
    currentCollection=Depends(getDb),
):
    ip = _client_ip(request)
    # 锁定时返回与“凭证错误”一致的内容,避免暴露锁定状态 / 被探测
    if _is_locked(ip):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    try:
        user = await currentCollection.find_one(
            {
                "user": data.user,
                "password": hashlib.sha256(data.password.encode("utf-8")).hexdigest(),
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )

    if user is None:
        _record_failure(ip)
        raise HTTPException(status_code=403, detail="Invalid credentials")

    _clear_failures(ip)
    return {
        "message": "success",
        "jwt": jwt.encode(
            {
                "sub": data.user,
                "iat": int(datetime.utcnow().timestamp()),
                "exp": int((datetime.utcnow() + timedelta(days=7)).timestamp()),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        ),
    }


@app.get("/verify")
async def verifyToken(user=Depends(verify)):
    return {"message": "success"}
