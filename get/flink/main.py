from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import motor.motor_asyncio as motor
import os

import httpx
import io
import ipaddress
import math
import socket
import time
from urllib.parse import urljoin, urlparse
from PIL import Image

from db import get_database

app = APIRouter()


async def getDb():
    return get_database()["FLinks"]


@app.get("/flinks")
async def getFlinks(currentCollection=Depends(getDb)):
    try:
        results = await currentCollection.find({}, {"_id": 0}).to_list(length=None)
        results.sort(key=lambda x: x.get("order") or 0)
        return {"message": "success", "data": results}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


@app.get("/flinkCount")
async def getFlinkCount(currentCollection=Depends(getDb)):
    try:
        pipeline = [
            {"$match": {"links": {"$exists": True}}},
            {"$project": {"linksCount": {"$size": "$links"}}},
            {"$group": {"_id": None, "totalLinks": {"$sum": "$linksCount"}}},
        ]
        result = await currentCollection.aggregate(pipeline).to_list(length=None)
        totalLinks = result[0]["totalLinks"] if result else 0
        return {"message": "success", "count": totalLinks}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": "fail", "error": str(e)}
        )


# ---------- 头像主题色提取（/themeColor） ----------
#
# 为什么公开：友链申请表单的「从头像取色」要用。原来的纯前端 canvas 方案要求
# 图床返回 CORS 头，QQ 头像（qlogo.cn）等国内常用源不带，浏览器里必然加载
# 失败；跨域限制浏览器侧绕不开，只能在服务端下载图片后提取。接口只返回一个
# 十六进制颜色字符串，不回显任何图片内容。
#
# 限流：与 flink 申请同款的进程内限流（Vercel 多实例下按实例独立，能挡住
# 单点刷，与登录爆破防护同样的取舍）。正常用户填一次表远用不到这个额度；
# 命中同 URL 时 Vercel CDN 会按响应的 Cache-Control 直接回缓存，不再进函数。

COLOR_RATE_COUNT = 60     # 时间窗内同一 IP 允许的取色次数
COLOR_RATE_WINDOW = 3600  # 秒
_color_rate: dict[str, list[float]] = {}

MAX_IMAGE_BYTES = 512 * 1024   # 64x64 取色用不到大图，同时给出口流量封顶
MAX_IMAGE_PIXELS = 16_000_000  # 解码内存上限（约 4000x4000），防解压炸弹
FETCH_DEADLINE = 8.0           # 总时限，与原前端 loadImage 的 8s 超时对齐
MAX_REDIRECTS = 3              # 手动跟重定向，每一跳都过内网校验
_FETCH_HEADERS = {
    # 部分图床的 WAF 拒绝空 UA；不带 Referer 可以过大部分防盗链
    "User-Agent": "Mozilla/5.0 (compatible; AriablogNext/1.0; +https://blog.yaria.top)"
}


def _color_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _check_color_rate(ip: str) -> bool:
    now = time.time()
    hits = [t for t in _color_rate.get(ip, []) if now - t < COLOR_RATE_WINDOW]
    if len(hits) >= COLOR_RATE_COUNT:
        _color_rate[ip] = hits
        return False
    hits.append(now)
    _color_rate[ip] = hits
    if len(_color_rate) > 5000:  # 防止字典无限增长
        for key in [
            k
            for k, v in _color_rate.items()
            if not any(now - t < COLOR_RATE_WINDOW for t in v)
        ]:
            _color_rate.pop(key, None)
    return True


def _assert_public_host(url: str) -> None:
    """SSRF 防护：只允许 http/https，且解析出的地址不得指向内网。
    存在 DNS rebinding 的理论窗口（校验与连接两次解析可能不同），但本接口
    只返回颜色、不回显响应内容，属于盲 SSRF，风险可接受。"""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise HTTPException(
            status_code=400,
            detail={"message": "fail", "error": "头像链接不合法，必须以 http(s):// 开头"},
        )
    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        raise HTTPException(
            status_code=502,
            detail={"message": "fail", "error": "头像域名无法解析（检查链接或对方站点是否下线）"},
        )
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise HTTPException(
                status_code=400,
                detail={"message": "fail", "error": "头像链接指向内网地址，已拒绝"},
            )


async def _fetch_image_bytes(url: str) -> bytes:
    """下载图片。httpx 默认不跟随重定向，这里手动逐跳跟随并重新校验目标，
    防止用 302 跳进内网；全程受 8s 总时限和 512KB 体积约束。"""
    deadline = time.monotonic() + FETCH_DEADLINE
    current = url
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(3.0),
            follow_redirects=False,
            headers=_FETCH_HEADERS,
            trust_env=False,  # 服务端抓图不理会 HTTP(S)_PROXY 等环境变量
        ) as client:
            for _ in range(MAX_REDIRECTS + 1):
                if time.monotonic() > deadline:
                    break
                _assert_public_host(current)
                async with client.stream("GET", current) as resp:
                    if 300 <= resp.status_code < 400 and resp.headers.get("location"):
                        current = urljoin(current, resp.headers["location"])
                        continue
                    if resp.status_code != 200:
                        raise HTTPException(
                            status_code=502,
                            detail={
                                "message": "fail",
                                "error": f"头像图片下载失败（对方返回 HTTP {resp.status_code}，可检查链接）",
                            },
                        )
                    ctype = resp.headers.get("content-type", "")
                    if not ctype.lower().startswith("image/"):
                        raise HTTPException(
                            status_code=415,
                            detail={"message": "fail", "error": "该链接返回的不是图片，无法取色"},
                        )
                    buf = bytearray()
                    async for chunk in resp.aiter_bytes():
                        buf.extend(chunk)
                        if len(buf) > MAX_IMAGE_BYTES:
                            raise HTTPException(
                                status_code=413,
                                detail={
                                    "message": "fail",
                                    "error": "头像图片过大（超过 512KB），无法取色",
                                },
                            )
                        if time.monotonic() > deadline:
                            raise HTTPException(
                                status_code=504,
                                detail={"message": "fail", "error": "头像图片下载超时，可稍后重试"},
                            )
                    return bytes(buf)
    except HTTPException:
        raise
    except httpx.HTTPError:
        # 连接超时/被重置等网络异常：转成带 CORS 头的 502，否则会变成
        # 无 CORS 头的裸 500，浏览器侧只看到 "Failed to fetch"
        raise HTTPException(
            status_code=502,
            detail={
                "message": "fail",
                "error": "头像图片下载失败（连不上对方站点或响应超时，可稍后重试）",
            },
        )
    raise HTTPException(
        status_code=502,
        detail={"message": "fail", "error": "头像图片下载失败（重定向次数过多或超时）"},
    )


def _js_round(x: float) -> int:
    # 对齐 JS 的 Math.round：.5 一律向上。Python 内置 round 是银行家舍入，
    # 分桶键和均值取整时会得到不同结果
    return math.floor(x + 0.5)


def _rgb_to_hsl(r: int, g: int, b: int):
    rn, gn, bn = r / 255, g / 255, b / 255
    mx, mn = max(rn, gn, bn), min(rn, gn, bn)
    l = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == rn:
        h = ((gn - bn) / d + (6 if gn < bn else 0)) * 60
    elif mx == gn:
        h = ((bn - rn) / d + 2) * 60
    else:
        h = ((rn - gn) / d + 4) * 60
    return h, s, l


def _hsl_to_rgb(h: float, s: float, l: float):
    c = (1 - abs(2 * l - 1)) * s
    hp = (((h % 360) + 360) % 360) / 60
    x = c * (1 - abs(hp % 2 - 1))
    if hp < 1:
        rgb = (c, x, 0.0)
    elif hp < 2:
        rgb = (x, c, 0.0)
    elif hp < 3:
        rgb = (0.0, c, x)
    elif hp < 4:
        rgb = (0.0, x, c)
    elif hp < 5:
        rgb = (x, 0.0, c)
    else:
        rgb = (c, 0.0, x)
    m = l - c / 2
    return tuple(min(255, max(0, _js_round((v + m) * 255))) for v in rgb)


def _to_hex(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, v)):02x}" for v in rgb)


def _normalize_for_card(hsl):
    """压到适合白字卡片的明度/饱和度区间，与前端原 normalizeForCard 一致"""
    h, s, l = hsl
    if l > 0.58:
        l = 0.58
    if l < 0.28:
        l = 0.28 + (l - 0.28) * 0.3
    if s < 0.22:
        s = 0.22
    if s > 0.75:
        s = 0.75
    return h, s, l


def _extract_color_from_pixels(pixels) -> str:
    """分桶提取主色，算法与前端 themeColor.ts 原版逐行对应：
    跳过透明/极浅/极深像素，按色相+明度分桶、彩度加权，取最重的一桶平均。
    全部被跳过时退化成不透明像素的平均色（原版的 fallback 逻辑）。"""
    buckets: dict[str, list] = {}
    fb_r = fb_g = fb_b = n = 0
    for r, g, b, a in pixels:
        if a < 128:
            continue
        fb_r += r
        fb_g += g
        fb_b += b
        n += 1
        h, s, l = _rgb_to_hsl(r, g, b)
        if l > 0.92 or l < 0.06:
            continue
        key = f"{_js_round(h / 16)}-{_js_round(l * 8)}"
        weight = 1 + s * 3
        cur = buckets.get(key)
        if cur:
            cur[0] += weight
            cur[1] += r
            cur[2] += g
            cur[3] += b
            cur[4] += 1
        else:
            buckets[key] = [weight, r, g, b, 1]

    if not buckets:
        if not n:
            return ""
        avg = _rgb_to_hsl(
            _js_round(fb_r / n), _js_round(fb_g / n), _js_round(fb_b / n)
        )
        return _to_hex(_hsl_to_rgb(*_normalize_for_card(avg)))

    # 并列时 max 取先插入的桶，与 JS 稳定排序后的第一个一致
    best = max(buckets.values(), key=lambda v: v[0])
    avg = _rgb_to_hsl(
        _js_round(best[1] / best[4]),
        _js_round(best[2] / best[4]),
        _js_round(best[3] / best[4]),
    )
    return _to_hex(_hsl_to_rgb(*_normalize_for_card(avg)))


def _decode_pixels(data: bytes):
    """解码成 RGBA 像素列表并缩到 64x64（与原 canvas drawImage 的拉伸行为一致）。
    缩放用 BOX 面积平均：实测与浏览器 canvas 的取色结果一致（个别照片可能
    有 ±1 的通道差，可接受），且比 NEAREST/BICUBIC 更能代表原图主色。"""
    try:
        img = Image.open(io.BytesIO(data))
        if img.width * img.height > MAX_IMAGE_PIXELS:
            raise HTTPException(
                status_code=413,
                detail={"message": "fail", "error": "头像图片尺寸过大，无法取色"},
            )
        img = img.convert("RGBA").resize((64, 64), Image.Resampling.BOX)
        return list(img.getdata())
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=415,
            detail={"message": "fail", "error": "图片解析失败，无法取色"},
        )


@app.get("/themeColor")
async def getThemeColor(url: str, request: Request):
    if not _check_color_rate(_color_client_ip(request)):
        raise HTTPException(
            status_code=429,
            detail={"message": "fail", "error": "取色太频繁了，请一小时后再试"},
        )
    data = await _fetch_image_bytes((url or "").strip())
    color = _extract_color_from_pixels(_decode_pixels(data))
    return JSONResponse(
        {"message": "success", "data": color},
        # 同一头像 URL 的重复请求由 CDN 直接回缓存，不再触发函数执行
        headers={"Cache-Control": "public, max-age=86400"},
    )
