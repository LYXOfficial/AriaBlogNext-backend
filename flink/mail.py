"""友链申请的邮件通知（标准库 smtplib，不引入新依赖）。

环境变量（命名与 twikoo 的邮件配置一致，方便直接照抄）：
  SMTP_HOST         SMTP 服务器，如 smtp.qq.com
  SMTP_PORT         端口，默认 465
  SMTP_SECURE       true/ssl -> SSL(465)；starttls -> STARTTLS(587)；false -> 明文(仅本地调试)
                    不填时按端口推断：465 用 SSL，其余用 STARTTLS
  SMTP_USER         登录账号（通常就是发件邮箱）
  SMTP_PASS         授权码/密码
  SMTP_FROM         发件邮箱，默认取 SMTP_USER
  SMTP_FROM_NAME    发件人显示名，默认「友链」
  FLINK_ADMIN_EMAIL 可选，博主邮箱：有新申请时抄送一份

未配置 SMTP_HOST/SMTP_USER/SMTP_PASS 时所有发送都静默跳过，接口照常返回成功。
"""

import os
import ssl
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

TIMEOUT_SECONDS = 12


def _setting(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _mail_identity() -> dict:
    return {
        "host": _setting("SMTP_HOST"),
        "port": int(_setting("SMTP_PORT", "465") or 465),
        "secure": _setting("SMTP_SECURE").lower(),
        "user": _setting("SMTP_USER"),
        "password": _setting("SMTP_PASS"),
        "sender": _setting("SMTP_FROM") or _setting("SMTP_USER"),
        "sender_name": _setting("SMTP_FROM_NAME", "友链"),
    }


def mail_configured() -> bool:
    cfg = _mail_identity()
    return bool(cfg["host"] and cfg["user"] and cfg["password"])


def _use_ssl(cfg: dict) -> bool:
    if cfg["secure"] in ("true", "ssl", "1", "yes"):
        return True
    if cfg["secure"] in ("starttls", "tls"):
        return False
    return cfg["port"] == 465


def _use_starttls(cfg: dict) -> bool:
    if cfg["secure"] in ("true", "ssl", "1", "yes"):
        return False
    if cfg["secure"] in ("starttls", "tls"):
        return True
    return cfg["port"] != 465


def send_mail(to: str, subject: str, body: str) -> bool:
    """发送一封纯文本邮件，成功返回 True。失败只记录日志，不抛异常。"""
    to = (to or "").strip()
    if not to or not mail_configured():
        return False

    cfg = _mail_identity()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((cfg["sender_name"], cfg["sender"]))
    message["To"] = to
    message.set_content(body)

    try:
        if _use_ssl(cfg):
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                cfg["host"], cfg["port"], timeout=TIMEOUT_SECONDS, context=context
            ) as server:
                server.login(cfg["user"], cfg["password"])
                server.send_message(message)
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=TIMEOUT_SECONDS) as server:
                server.ehlo()
                if _use_starttls(cfg):
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                server.login(cfg["user"], cfg["password"])
                server.send_message(message)
        return True
    except Exception as error:  # 网络/认证/被拦截都不应影响主流程
        print(f"[flink-mail] 发送到 {to} 失败: {error}")
        return False


def _signature() -> str:
    return "\n\n—— 本邮件由友链申请系统自动发送，请勿直接回复。"


def application_received(name: str, link: str, is_modify: bool) -> tuple[str, str]:
    """申请人：提交成功回执"""
    kind = "修改" if is_modify else "友链"
    subject = f"已收到你的{kind}申请 - {name}"
    body = (
        f"你好，{name}：\n\n"
        f"我们已收到你对 {link} 的{kind}申请，博主会尽快审核。\n\n"
        f"审核结果会发送到这个邮箱；你也可以在友链页面用该邮箱自助查询进度。\n"
        f"如果审核未通过，不会单独通知，也不会保留申请记录，可以修改后重新提交。"
        + _signature()
    )
    return subject, body


def application_approved(name: str, link: str, group: str, is_modify: bool) -> tuple[str, str]:
    """申请人：审核通过通知"""
    if is_modify:
        subject = f"友链修改已生效 - {name}"
        body = (
            f"你好，{name}：\n\n"
            f"你对 {link} 的友链修改申请已通过，新的信息已经生效。\n\n"
            f"若显示有延迟，刷新友链页面即可。感谢你的支持！"
            + _signature()
        )
    else:
        subject = f"友链申请已通过 - {name}"
        body = (
            f"你好，{name}：\n\n"
            f"你的友链申请已通过，{link} 已添加到「{group}」分组。\n\n"
            f"若显示有延迟，刷新友链页面即可。感谢你的支持！"
            + _signature()
        )
    return subject, body


def application_rejected(name: str, link: str, reason: str) -> tuple[str, str]:
    """申请人：审核未通过（仅当博主填写了理由时才发送）"""
    subject = f"友链申请未通过 - {name}"
    body = (
        f"你好，{name}：\n\n"
        f"很抱歉，你对 {link} 的友链申请未能通过审核。\n\n"
        f"原因：{reason}\n\n"
        f"你可以按上述说明调整后重新提交申请。"
        + _signature()
    )
    return subject, body


def admin_new_application(name: str, link: str, email: str, is_modify: bool) -> tuple[str, str]:
    """博主：新申请提醒"""
    kind = "修改申请" if is_modify else "新增申请"
    subject = f"[友链] 新的{kind}：{name}"
    body = (
        f"收到一条{kind}：\n\n"
        f"  站点名称：{name}\n"
        f"  网址：{link}\n"
        f"  申请人邮箱：{email}\n\n"
        f"请到后台「友链 → 待审核申请」处理。"
        + _signature()
    )
    return subject, body
