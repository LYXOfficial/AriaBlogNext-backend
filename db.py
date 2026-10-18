"""共享 MongoDB 客户端。

原先后端每个请求依赖里都会 `AsyncIOMotorClient(...)` 新建一个客户端，
等于每次请求都重新建立连接池（Atlas 还要重新 TLS 握手），开销很大。
这里改用模块级单例：同一进程内复用同一个连接池。
"""

import os

from motor.motor_asyncio import AsyncIOMotorClient

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            os.environ.get("MONGODB_URI") or "mongodb://localhost:27017"
        )
    return _client


def get_database():
    return get_client()[os.getenv("DB_NAME") or "AriaBlogNext"]
