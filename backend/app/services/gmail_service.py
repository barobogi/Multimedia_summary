"""Email distribution service via Daum SMTP"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..models import SummaryResponse
from ..config import settings

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.daum.net"
SMTP_PORT = 465


async def send_summary(summary: SummaryResponse) -> bool:
    """
    Send summary email via Daum SMTP.

    Args:
        summary: SummaryResponse object

    Returns:
        True if successful
    """
    if not settings.daum_id or not settings.daum_pw:
        logger.warning("DAUM_ID/DAUM_PW not set — skipping email")
        return False

    from_email = f"{settings.daum_id}@daum.net"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📺 {summary.metadata.title}"
    msg["From"] = from_email
    msg["To"] = settings.email_to
    msg.attach(MIMEText(_build_html(summary), "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(from_email, settings.daum_pw)
            s.sendmail(from_email, [settings.email_to], msg.as_string())
        logger.info(f"✉️  Email sent → {settings.email_to}")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        raise


def _build_html(summary: SummaryResponse) -> str:
    categories_html = "".join([
        f'<span style="display:inline-block;margin-right:8px;padding:4px 8px;'
        f'background:#e8f4f8;border-radius:4px;font-size:12px;">{cat}</span>'
        for cat in summary.categories
    ])

    insights_html = "".join(f"<li>{i}</li>" for i in summary.key_insights)

    stock_html = ""
    if summary.stock_related:
        items = "".join(f"<li>{i}</li>" for i in summary.stock_related)
        stock_html = f'<h3 style="color:#d4a574;margin-top:20px;">💰 자본/주식 관련</h3><ul>{items}</ul>'

    return f"""
<html><head><meta charset="utf-8">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.6;color:#333}}
  .wrap{{max-width:600px;margin:0 auto;padding:20px}}
  h2{{color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:10px}}
  h3{{color:#34495e;margin-top:15px}}
  .meta{{background:#f5f5f5;padding:12px;border-left:4px solid #3498db;margin:15px 0}}
  a{{color:#3498db;text-decoration:none}}
  .ts{{font-size:12px;color:#999;margin-top:30px;text-align:center}}
</style></head>
<body><div class="wrap">
  <h2>📺 {summary.metadata.title}</h2>
  <div class="meta">
    <strong>채널:</strong> {summary.metadata.channel or 'Unknown'}<br>
    <strong>링크:</strong> <a href="{summary.metadata.url}">{summary.metadata.url}</a>
  </div>
  <h3>📝 요약</h3><p>{summary.summary}</p>
  <h3>💡 주요 인사이트</h3><ul>{insights_html}</ul>
  <div>{categories_html}</div>
  {stock_html}
  <div class="ts">처리 시간: {summary.processing_time_ms:.0f}ms · {summary.timestamp.strftime('%Y-%m-%d %H:%M')}</div>
</div></body></html>"""
