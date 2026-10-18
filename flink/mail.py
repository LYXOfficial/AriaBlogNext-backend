"""友链申请的邮件通知（标准库 smtplib，不引入新依赖）。

邮件为「纯文本 + HTML」双版本，HTML 版尽量贴合博客本身的设计：
粉色渐变头部、白色圆角卡片、友链卡片式信息块、胶囊按钮。

环境变量（SMTP 部分命名与 twikoo 的邮件配置一致，方便直接照抄）：
  SMTP_HOST         SMTP 服务器，如 smtp.qq.com
  SMTP_PORT         端口，默认 465
  SMTP_SECURE       true/ssl -> SSL(465)；starttls -> STARTTLS(587)；false -> 明文(仅本地调试)
                    不填时按端口推断：465 用 SSL，其余用 STARTTLS
  SMTP_USER         登录账号（通常就是发件邮箱）
  SMTP_PASS         授权码/密码
  SMTP_FROM         发件邮箱，默认取 SMTP_USER
  SMTP_FROM_NAME    发件人显示名，默认「友链」
  FLINK_ADMIN_EMAIL 可选，博主邮箱：有新申请时抄送一份
  SITE_NAME         站点名称（邮件里的品牌名）
  SITE_URL          站点地址，用于「前往友链页」按钮
  SITE_LOGO         站点图标
  FLINK_ADMIN_PANEL_URL 可选，后台地址（博主邮件里的「去后台处理」按钮）

未配置 SMTP_HOST/SMTP_USER/SMTP_PASS 时所有发送都静默跳过，接口照常返回成功。
"""

import os
import ssl
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from html import escape

TIMEOUT_SECONDS = 12

# 与博客主题一致的配色
COLOR_THEME = "#ef859d"
COLOR_THEME_LIGHT = "#f79dbc"
COLOR_TITLE = "#c5343e"
COLOR_TEXT = "#4c4948"
COLOR_MUTED = "#8a8a8a"
COLOR_BG = "#f7f9fe"
COLOR_CARD_BORDER = "#f2e4e9"
FONT_STACK = (
    '-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",'
    '"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif'
)


def _setting(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _site() -> dict:
    return {
        "name": _setting("SITE_NAME", "Ariasakaの小窝"),
        "url": _setting("SITE_URL", "https://blog.yaria.top").rstrip("/"),
        "logo": _setting(
            "SITE_LOGO", "https://img.0v0.my/2025/10/12/6dd5eec4823f8.webp"
        ),
        "admin": _setting("FLINK_ADMIN_PANEL_URL").rstrip("/"),
    }


def _links_url() -> str:
    return _site()["url"] + "/links"


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


def send_mail(to: str, subject: str, text: str, html: str = "") -> bool:
    """发送一封邮件（有 html 时同时提供 HTML 版本），成功返回 True。

    失败只记录日志，不抛异常，不影响主流程。
    """
    to = (to or "").strip()
    if not to or not mail_configured():
        return False

    cfg = _mail_identity()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((cfg["sender_name"], cfg["sender"]))
    message["To"] = to
    message.set_content(text)
    if html:
        message.add_alternative(html, subtype="html")

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


# ---------- HTML 模板 ----------


def _paragraph(html_text: str) -> str:
    return (
        f'<p style="margin:0 0 14px;font-size:14px;line-height:1.9;'
        f'color:{COLOR_TEXT};">{html_text}</p>'
    )


def _site_card(name: str, url: str, avatar: str, descr: str = "", extra: str = "") -> str:
    """仿博客友链卡片：头像 + 站名 + 网址 + 描述"""
    safe_name = escape(name or "")
    safe_url = escape(url or "")
    safe_descr = escape(descr or "")
    avatar_html = ""
    if avatar:
        avatar_html = (
            f'<img src="{escape(avatar)}" width="42" height="42" alt="" '
            f'style="display:block;width:42px;height:42px;border-radius:50%;'
            f'object-fit:cover;background:#f1f1f1;" />'
        )
    descr_html = (
        f'<div style="margin-top:5px;font-size:12.5px;line-height:1.6;'
        f'color:{COLOR_MUTED};">{safe_descr}</div>'
        if safe_descr
        else ""
    )
    return f"""
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="border-collapse:separate;margin:4px 0 20px;">
    <tr>
      <td style="background:{COLOR_BG};border-radius:14px;padding:14px 16px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="54" valign="top">{avatar_html}</td>
            <td valign="top" style="padding-left:12px;">
              <div style="font-size:15px;font-weight:600;color:{COLOR_TEXT};">
                {safe_name}
              </div>
              <div style="margin-top:5px;font-size:12.5px;word-break:break-all;">
                <a href="{safe_url}" style="color:{COLOR_THEME};text-decoration:none;">{safe_url}</a>
              </div>
              {descr_html}
              {extra}
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>"""


def _note_block(html_text: str) -> str:
    return f"""
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="border-collapse:separate;margin:4px 0 20px;">
    <tr>
      <td style="background:#fff5f7;border-left:4px solid {COLOR_THEME};
                 border-radius:10px;padding:12px 14px;font-size:13.5px;
                 line-height:1.8;color:{COLOR_TEXT};">
        {html_text}
      </td>
    </tr>
  </table>"""


def _button(text: str, url: str) -> str:
    if not url:
        return ""
    return f"""
  <div style="margin:22px 0 6px;">
    <a href="{escape(url)}"
       style="display:inline-block;padding:11px 26px;background:{COLOR_THEME};
              color:#ffffff;font-size:14px;border-radius:22px;
              text-decoration:none;font-weight:600;">{escape(text)}</a>
  </div>"""


def _render_html(
    title: str,
    paragraphs: list[str],
    blocks: list[str] | None = None,
    cta_text: str = "",
    cta_url: str = "",
) -> str:
    site = _site()
    body = "".join(paragraphs) + "".join(blocks or []) + _button(cta_text, cta_url)
    logoSrc = escape(site["logo"])
    site_name = escape(site["name"])
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <meta name="color-scheme" content="light" />
  <title>{escape(title)}</title>
</head>
<body style="margin:0;padding:0;background:{COLOR_BG};font-family:{FONT_STACK};">
  <div style="padding:28px 14px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="border-collapse:separate;max-width:560px;margin:0 auto;">
      <tr>
        <td style="background:#ffffff;border:1px solid {COLOR_CARD_BORDER};
                   border-radius:18px;overflow:hidden;">
          <!-- 头部：粉色渐变，呼应博客主题 -->
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="background:{COLOR_THEME_LIGHT};
                         background-image:linear-gradient(135deg,{COLOR_THEME_LIGHT},{COLOR_THEME});
                         padding:20px 24px;">
                <table role="presentation" cellpadding="0" cellspacing="0">
                  <tr>
                    <td width="46" valign="middle">
                      <img src="{logoSrc}" width="38" height="38" alt=""
                           style="display:block;width:38px;height:38px;
                                  border-radius:50%;background:#ffffff55;" />
                    </td>
                    <td valign="middle" style="padding-left:12px;">
                      <div style="font-size:17px;font-weight:700;color:#ffffff;">
                        {site_name}
                      </div>
                      <div style="margin-top:3px;font-size:12px;color:#ffffffd0;">
                        友链申请通知
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <!-- 正文 -->
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding:24px 24px 18px;">
                <div style="font-size:16.5px;font-weight:700;color:{COLOR_TITLE};
                            margin-bottom:16px;">{escape(title)}</div>
                {body}
              </td>
            </tr>
          </table>

          <!-- 页脚 -->
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding:14px 24px 18px;border-top:1px dashed {COLOR_CARD_BORDER};">
                <div style="font-size:11.5px;line-height:1.7;color:{COLOR_MUTED};">
                  本邮件由 <a href="{escape(site['url'])}"
                    style="color:{COLOR_THEME};text-decoration:none;">{site_name}</a>
                  自动发送，请勿直接回复。
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </div>
</body>
</html>"""


def _signature() -> str:
    site = _site()
    return f"\n\n—— 本邮件由 {site['name']} 自动发送，请勿直接回复。\n{site['url']}/links"


def application_received(
    name: str, link: str, is_modify: bool, avatar: str = "", descr: str = ""
) -> tuple[str, str, str]:
    """申请人：提交成功回执"""
    kind = "修改" if is_modify else "友链"
    subject = f"已收到你的{kind}申请 - {name}"
    text = (
        f"你好，{name}：\n\n"
        f"我们已收到你对 {link} 的{kind}申请，博主会尽快审核。\n\n"
        f"审核结果会发送到这个邮箱；你也可以在友链页面用该邮箱自助查询进度。\n"
        f"如果审核未通过，不会单独通知，也不会保留申请记录，可以修改后重新提交。"
        + _signature()
    )
    html = _render_html(
        f"已收到你的{kind}申请",
        [
            _paragraph(f"你好，<b>{escape(name)}</b>："),
            _paragraph(f"我们已收到你的{kind}申请，博主会尽快审核。"),
        ],
        [
            _site_card(name, link, avatar, descr),
            _note_block("审核结果会发送到这个邮箱，也可以在友链页面用该邮箱自助查询进度。"),
        ],
        cta_text="前往友链页面",
        cta_url=_links_url(),
    )
    return subject, text, html


def application_approved(
    name: str, link: str, group: str, is_modify: bool, avatar: str = "", descr: str = ""
) -> tuple[str, str, str]:
    """申请人：审核通过通知"""
    if is_modify:
        subject = f"友链修改已生效 - {name}"
        text = (
            f"你好，{name}：\n\n"
            f"你对 {link} 的友链修改申请已通过，新的信息已经生效。\n\n"
            f"若显示有延迟，刷新友链页面即可。感谢你的支持！"
            + _signature()
        )
        title = "友链修改已生效"
        intro = "你的友链修改申请已通过，新的信息已经生效。"
    else:
        subject = f"友链申请已通过 - {name}"
        text = (
            f"你好，{name}：\n\n"
            f"你的友链申请已通过，{link} 已添加到「{group}」分组。\n\n"
            f"若显示有延迟，刷新友链页面即可。感谢你的支持！"
            + _signature()
        )
        title = "友链申请已通过"
        intro = f"你的友链申请已通过，已添加到「{escape(group)}」分组。"

    html = _render_html(
        title,
        [_paragraph(f"你好，<b>{escape(name)}</b>："), _paragraph(intro)],
        [_site_card(name, link, avatar, descr)],
        cta_text="前往友链页面",
        cta_url=_links_url(),
    )
    return subject, text, html


def application_rejected(
    name: str, link: str, reason: str, avatar: str = ""
) -> tuple[str, str, str]:
    """申请人：审核未通过（仅当博主填写了理由时才发送）"""
    subject = f"友链申请未通过 - {name}"
    text = (
        f"你好，{name}：\n\n"
        f"很抱歉，你对 {link} 的友链申请未能通过审核。\n\n"
        f"原因：{reason}\n\n"
        f"你可以按上述说明调整后重新提交申请。"
        + _signature()
    )
    html = _render_html(
        "友链申请未通过",
        [
            _paragraph(f"你好，<b>{escape(name)}</b>："),
            _paragraph("很抱歉，你的友链申请未能通过审核。"),
        ],
        [
            _site_card(name, link, avatar, ""),
            _note_block(f"<b>原因：</b>{escape(reason)}"),
            _paragraph("你可以按上述说明调整后重新提交申请。"),
        ],
        cta_text="重新提交申请",
        cta_url=_links_url(),
    )
    return subject, text, html


def admin_new_application(
    name: str, link: str, email: str, is_modify: bool, avatar: str = "", descr: str = ""
) -> tuple[str, str, str]:
    """博主：新申请提醒"""
    kind = "修改申请" if is_modify else "新增申请"
    subject = f"[友链] 新的{kind}：{name}"
    text = (
        f"收到一条{kind}：\n\n"
        f"  站点名称：{name}\n"
        f"  网址：{link}\n"
        f"  申请人邮箱：{email}\n\n"
        f"请到后台「友链 → 待审核申请」处理。"
        + _signature()
    )
    site = _site()
    html = _render_html(
        f"新的{kind}",
        [_paragraph(f"收到一条{kind}，请到后台处理。")],
        [
            _site_card(
                name,
                link,
                avatar,
                descr,
                extra=(
                    f'<div style="margin-top:5px;font-size:12.5px;color:{COLOR_MUTED};">'
                    f"申请人邮箱：{escape(email)}</div>"
                ),
            ),
        ],
        cta_text="去后台处理" if site["admin"] else "前往友链页面",
        cta_url=site["admin"] or _links_url(),
    )
    return subject, text, html
