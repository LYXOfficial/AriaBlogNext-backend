"""友链申请 AI 初筛。

流程：申请提交后触发 GitHub Actions 工作流 → runner 抓取对方站点文本、
交给 Ollama（qwen3.5）按规则初筛 → 结论通过受密钥保护的回写接口写进
申请记录（aiScreening 字段），dashboard 据此显示绿/红标签。

设计取舍：
- runner 不直连 MongoDB（数据库不一定公网可达），统一走回写接口；
- 触发失败（未配置 GITHUB_REPO、token 失效、网络抖动）一律静默降级，
  初筛只是辅助手段，人工审核才是最终把关，不能因为初筛挂掉影响申请提交。
"""

import os
import secrets
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

from db import get_database

DISPATCH_TIMEOUT = 8.0  # 触发 dispatch 只是入队，超时不值得久等
SUMMARY_LIMIT = 200  # 站点摘要回写上限（字符）
REASON_LIMIT = 300  # 违规理由回写上限
MODEL_LIMIT = 50

app = APIRouter()


async def trigger_screening(
    app_id: str, url: str, name: str = "", descr: str = ""
) -> bool:
    """触发 GitHub Actions 初筛工作流（repository_dispatch）。

    未配置 GITHUB_REPO / GH_TOKEN 时视为功能关闭，直接跳过。
    """
    repo = os.environ.get("GITHUB_REPO", "").strip()
    token = os.environ.get("GH_TOKEN", "").strip()
    if not repo or not token:
        return False
    try:
        async with httpx.AsyncClient(timeout=DISPATCH_TIMEOUT) as client:
            resp = await client.post(
                f"https://api.github.com/repos/{repo}/dispatches",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json={
                    "event_type": "flink-screening",
                    # 名称和描述一起带给模型：申请文本本身也要过一遍审核
                    "client_payload": {
                        "id": app_id,
                        "url": url,
                        "name": (name or "")[:100],
                        "descr": (descr or "")[:300],
                    },
                },
            )
            # 204 = 已接受入队；401/404（token 失效、远端还没有这个工作流）
            # 都只代表初筛这次没跑，不影响申请
            return resp.status_code == 204
    except Exception:
        return False


async def getApplicationsDb():
    return get_database()["FLinkApplications"]


class ScreeningBody(BaseModel):
    id: str
    verdict: str  # pass=初筛通过；review=疑似违规，建议人工核实
    backlink: Optional[str] = ""  # found=已检测到本站回链；not_found=未见回链
    summary: str = ""
    reason: str = ""
    model: Optional[str] = ""


@app.post("/screening")
async def receive_screening(
    body: ScreeningBody,
    request: Request,
    applicationsDb=Depends(getApplicationsDb),
):
    """初筛结论回写（GitHub Actions runner 调用）。

    用独立的 SCREENING_SECRET 鉴权而不是后台登录态：runner 没有管理员
    账号，也不该拿到；密钥只授予「写 aiScreening 字段」这一件事。
    """
    expected = os.environ.get("SCREENING_SECRET", "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail={"message": "fail", "error": "初筛功能未配置，请先设置 SCREENING_SECRET"},
        )
    provided = request.headers.get("x-screening-secret", "")
    if not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=401,
            detail={"message": "fail", "error": "回写密钥不正确"},
        )

    if body.verdict not in ("pass", "review"):
        raise HTTPException(
            status_code=400,
            detail={"message": "fail", "error": "verdict 只能是 pass 或 review"},
        )
    if not ObjectId.is_valid(body.id):
        raise HTTPException(
            status_code=400,
            detail={"message": "fail", "error": "申请 ID 格式不正确"},
        )

    # 只更新还在待审的申请：已经人工出结果的记录不该被迟到的初筛覆盖
    result = await applicationsDb.update_one(
        {"_id": ObjectId(body.id), "status": "pending"},
        {
            "$set": {
                "aiScreening": {
                    "verdict": body.verdict,
                    "backlink": body.backlink.strip()[:20],
                    "summary": body.summary.strip()[:SUMMARY_LIMIT],
                    "reason": body.reason.strip()[:REASON_LIMIT],
                    "model": (body.model or "").strip()[:MODEL_LIMIT],
                    "screenedAt": datetime.now(timezone.utc),
                }
            }
        },
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail={"message": "fail", "error": "申请不存在或已不在待审状态"},
        )
    return {"message": "success"}
