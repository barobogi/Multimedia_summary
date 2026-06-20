"""Gmail email distribution service"""

import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

from ..models import SummaryResponse
from ..config import settings

logger = logging.getLogger(__name__)


async def send_summary(summary: SummaryResponse) -> bool:
    """
    Send summary to email (barobogi79@gmail.com)

    Args:
        summary: SummaryResponse object

    Returns:
        True if successful
    """

    try:
        # Create email content
        email_body = create_email_body(summary)

        # Send via Gmail API
        service = build('gmail', 'v1')

        # Create message
        message = MIMEMultipart('alternative')
        message['To'] = settings.gmail_user
        message['From'] = settings.gmail_user
        message['Subject'] = f"📺 {summary.metadata.title}"

        # Add body
        msg_html = MIMEText(email_body, 'html')
        message.attach(msg_html)

        # Send
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        logger.info(f"✉️  Email sent (message_id: {result.get('id')})")
        return True

    except Exception as e:
        logger.error(f"Email error: {str(e)}")
        raise


def create_email_body(summary: SummaryResponse) -> str:
    """Create HTML email body"""

    categories_html = "".join([
        f'<span style="display: inline-block; margin-right: 8px; padding: 4px 8px; background-color: #e8f4f8; border-radius: 4px; font-size: 12px;">{cat}</span>'
        for cat in summary.categories
    ])

    stock_html = ""
    if summary.stock_related:
        stock_html = f"""
        <h3 style="color: #d4a574; margin-top: 20px;">💰 자본/주식 관련</h3>
        <ul>
            {''.join([f'<li>{item}</li>' for item in summary.stock_related])}
        </ul>
        """

    insights_html = "".join([
        f"<li>{insight}</li>" for insight in summary.key_insights
    ])

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h3 {{ color: #34495e; margin-top: 15px; }}
            .metadata {{ background-color: #f5f5f5; padding: 12px; border-left: 4px solid #3498db; margin: 15px 0; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .categories {{ margin: 10px 0; }}
            .insight {{ background-color: #fff3cd; padding: 10px; border-radius: 4px; margin: 8px 0; }}
            .timestamp {{ font-size: 12px; color: #999; margin-top: 30px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📺 {summary.metadata.title}</h2>

            <div class="metadata">
                <strong>채널:</strong> {summary.metadata.channel or 'Unknown'}<br>
                <strong>링크:</strong> <a href="{summary.metadata.url}">{summary.metadata.url}</a>
            </div>

            <h3>📝 요약</h3>
            <p>{summary.summary}</p>

            <h3>💡 주요 인사이트</h3>
            <ul>
                {insights_html}
            </ul>

            <div class="categories">
                <strong>카테고리:</strong> {categories_html}
            </div>

            {stock_html}

            <div class="timestamp">
                <p>Processed: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (Processing time: {summary.processing_time_ms:.0f}ms)</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html
