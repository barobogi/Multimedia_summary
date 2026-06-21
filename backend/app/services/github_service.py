"""GitHub API service for Pages update and file storage"""

import logging
import base64
import json
from datetime import datetime
from github import Github, GithubException

from ..models import SummaryResponse
from ..config import settings

logger = logging.getLogger(__name__)


def _gh():
    if not settings.github_token:
        raise RuntimeError("GITHUB_TOKEN이 설정되지 않았습니다")
    return Github(settings.github_token)


async def update_github_pages(summary: SummaryResponse) -> bool:
    """
    Update GitHub Pages with new summary

    Adds entry to _data/multimedia.json for the website to consume

    Args:
        summary: SummaryResponse object

    Returns:
        True if successful
    """

    try:
        repo = _gh().get_repo(settings.github_repo)

        # Create or update multimedia.json data file
        data_file_path = "_data/multimedia.json"

        # Get existing data
        try:
            contents = repo.get_contents(data_file_path)
            existing_data = json.loads(contents.decoded_content.decode())
        except GithubException:
            # File doesn't exist yet
            existing_data = []

        # Add new entry (newest first)
        new_entry = {
            "title": summary.metadata.title,
            "url": str(summary.metadata.url),
            "channel": summary.metadata.channel or "Unknown",
            "summary": summary.summary,
            "categories": summary.categories,
            "stock_related": summary.stock_related or [],
            "ai_related": summary.ai_related or [],
            "learning_related": summary.learning_related or [],
            "key_insights": summary.key_insights,
            "timestamp": summary.timestamp.isoformat(),
            "thumbnail": summary.metadata.thumbnail_url
        }

        # 동일 URL 중복 제거 후 최신 내용으로 교체
        video_url = str(summary.metadata.url)
        existing_data = [e for e in existing_data if e.get("url") != video_url]
        existing_data.insert(0, new_entry)  # Add to beginning
        existing_data = existing_data[:50]  # Keep only latest 50

        # Update file
        new_content = json.dumps(existing_data, ensure_ascii=False, indent=2)

        try:
            existing_file = repo.get_contents(data_file_path)
            repo.update_file(
                path=data_file_path,
                message=f"Update multimedia: {summary.metadata.title}",
                content=new_content,
                sha=existing_file.sha
            )
        except GithubException:
            # Create new file
            repo.create_file(
                path=data_file_path,
                message=f"Add multimedia: {summary.metadata.title}",
                content=new_content
            )

        logger.info(f"🌐 GitHub Pages updated: {data_file_path}")
        return True

    except Exception as e:
        logger.error(f"GitHub Pages error: {str(e)}")
        raise


async def save_file_to_github(
    path: str,
    content: str,
    message: str,
    branch: str = "main"
) -> bool:
    """
    Save a file to GitHub repository

    Used for saving Obsidian markdown files

    Args:
        path: File path in repo
        content: File content
        message: Commit message
        branch: Target branch

    Returns:
        True if successful
    """

    try:
        repo = _gh().get_repo(settings.github_repo)

        # Check if file exists
        try:
            existing_file = repo.get_contents(path, ref=branch)
            # Update existing file
            repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=existing_file.sha,
                branch=branch
            )
            logger.info(f"✅ Updated file in GitHub: {path}")
        except GithubException:
            # Create new file
            repo.create_file(
                path=path,
                message=message,
                content=content,
                branch=branch
            )
            logger.info(f"✅ Created file in GitHub: {path}")

        return True

    except Exception as e:
        logger.error(f"GitHub file save error: {str(e)}")
        raise


async def create_github_pages_post(summary: SummaryResponse) -> bool:
    """
    Create Jekyll-style blog post for GitHub Pages

    Args:
        summary: SummaryResponse object

    Returns:
        True if successful
    """

    try:
        # Create Jekyll frontmatter
        frontmatter = f"""---
layout: post
title: {summary.metadata.title}
date: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S %z')}
categories: {' '.join(summary.categories)}
tags: {' '.join(['stock' if summary.stock_related else '', 'ai' if summary.ai_related else '', 'learning' if summary.learning_related else ''])}
source: {summary.metadata.url}
---

"""

        # Create content
        content = frontmatter + f"""
## 📺 원본 정보

**제목**: {summary.metadata.title}
**채널**: {summary.metadata.channel or 'Unknown'}
**링크**: [{summary.metadata.title}]({summary.metadata.url})

## 📝 요약

{summary.summary}

## 💡 주요 인사이트

"""

        for insight in summary.key_insights:
            content += f"- {insight}\n"

        if summary.stock_related:
            content += f"""
## 💰 자본/주식 관련

"""
            for item in summary.stock_related:
                content += f"- {item}\n"

        # Save as post
        date_path = summary.timestamp.strftime("%Y/%m/%d")
        filename = f"_posts/{date_path}/{summary.timestamp.strftime('%Y-%m-%d')}-multimedia.md"

        await save_file_to_github(
            path=filename,
            content=content,
            message=f"Add multimedia summary: {summary.metadata.title}"
        )

        return True

    except Exception as e:
        logger.error(f"GitHub post creation error: {str(e)}")
        raise
