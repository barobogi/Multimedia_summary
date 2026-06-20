"""Obsidian vault synchronization service"""

import logging
import aiohttp
from datetime import datetime
from typing import Dict

from ..models import SummaryResponse
from ..config import settings

logger = logging.getLogger(__name__)


async def save_to_obsidian(summary: SummaryResponse) -> bool:
    """
    Save summary to Obsidian vault via OneDrive/GitHub

    For MVP, we'll create a markdown file that can be synced via:
    1. GitHub API (if vault is on GitHub)
    2. OneDrive API (if vault is synced via OneDrive)

    Args:
        summary: SummaryResponse object

    Returns:
        True if successful
    """

    try:
        # Create markdown content
        markdown_content = create_markdown_content(summary)

        # Determine filename
        timestamp = summary.timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Multimedia/{summary.timestamp.strftime('%Y/%m/%d')}/{timestamp}_{summary.metadata.title[:30]}.md"

        logger.info(f"Saving to Obsidian: {filename}")

        # Save via GitHub (preferred for MVP)
        if settings.github_token:
            from . import github_service
            await github_service.save_file_to_github(
                path=filename,
                content=markdown_content,
                message=f"Add multimedia summary: {summary.metadata.title}"
            )
        else:
            logger.warning("GitHub token not configured for Obsidian sync")
            return False

        logger.info(f"✅ Obsidian saved: {filename}")
        return True

    except Exception as e:
        logger.error(f"Obsidian error: {str(e)}")
        raise


def create_markdown_content(summary: SummaryResponse) -> str:
    """Create markdown file content for Obsidian"""

    tags = []
    if summary.stock_related:
        tags.append("stock")
    if summary.ai_related:
        tags.append("ai")
    if summary.learning_related:
        tags.append("learning")

    tags_str = " ".join([f"#{tag}" for tag in tags])

    categories_str = " | ".join(summary.categories) if summary.categories else "N/A"

    content = f"""---
title: {summary.metadata.title}
url: {summary.metadata.url}
channel: {summary.metadata.channel or "Unknown"}
date: {summary.timestamp.isoformat()}
categories: {categories_str}
processing_time: {summary.processing_time_ms:.0f}ms
tags: {tags_str}
---

## 📺 원본 정보

- **제목**: {summary.metadata.title}
- **채널**: {summary.metadata.channel or "Unknown"}
- **링크**: [{summary.metadata.title}]({summary.metadata.url})
- **설명**: {summary.metadata.description or "없음"}

## 📝 요약

{summary.summary}

## 💡 주요 인사이트

"""

    for insight in summary.key_insights:
        content += f"- {insight}\n"

    # Stock-related section
    if summary.stock_related:
        content += f"""
## 💰 자본/주식 관련 내용

"""
        for item in summary.stock_related:
            content += f"- {item}\n"

    # AI-related section
    if summary.ai_related:
        content += f"""
## 🤖 AI/ML 관련 내용

"""
        for item in summary.ai_related:
            content += f"- {item}\n"

    # Learning-related section
    if summary.learning_related:
        content += f"""
## 📚 학습 관련 내용

"""
        for item in summary.learning_related:
            content += f"- {item}\n"

    content += f"""
---

*자동 생성됨 - Multimedia Summary App*
*Generated: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return content
