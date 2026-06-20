"""YouTube video extraction service"""

import logging
import re
from typing import Tuple

import httpx
from youtube_transcript_api import YouTubeTranscriptApi

from ..models import VideoMetadata

logger = logging.getLogger(__name__)

OEMBED_URL = "https://www.youtube.com/oembed"


async def extract_video_data(video_url: str, language: str = "ko") -> Tuple[VideoMetadata, str]:
    """
    Extract video metadata and transcript from YouTube.

    Returns:
        Tuple of (VideoMetadata, transcript_text)
    """
    video_id = extract_youtube_id(video_url)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {video_url}")

    logger.info(f"Extracting metadata for: {video_id}")
    metadata = await extract_metadata(video_id)

    logger.info(f"Extracting transcript for: {video_id}")
    transcript = await extract_transcript(video_id, language)

    return metadata, transcript


def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


async def extract_metadata(video_id: str) -> VideoMetadata:
    """
    Extract video metadata via YouTube oEmbed API.
    No API key or format selection needed — works from any server IP.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(OEMBED_URL, params={"url": video_url, "format": "json"})
            res.raise_for_status()
            info = res.json()

        return VideoMetadata(
            title=info.get("title", "Unknown"),
            url=video_url,
            channel=info.get("author_name"),
            thumbnail_url=info.get("thumbnail_url"),
        )
    except Exception as e:
        logger.error(f"oEmbed metadata error: {e}")
        # 메타데이터 실패해도 최소 정보로 계속 진행
        return VideoMetadata(title="Unknown", url=video_url)


async def extract_transcript(video_id: str, language: str = "ko") -> str:
    """
    Extract transcript using youtube_transcript_api v1.x.
    Priority: requested language > English > any available
    """
    api = YouTubeTranscriptApi()

    try:
        snippets = api.fetch(video_id, languages=[language, "en"])
        logger.info(f"Got transcript (lang={language})")
    except Exception:
        try:
            transcript_list = api.list(video_id)
            first = next(iter(transcript_list))
            snippets = first.fetch()
            logger.info(f"Fallback transcript: {first.language}")
        except Exception as e:
            logger.error(f"Could not extract transcript: {e}")
            raise ValueError(f"Cannot extract transcript: {e}")

    transcript_text = " ".join(s.text for s in snippets)
    return clean_transcript(transcript_text)


def clean_transcript(text: str) -> str:
    """Clean and normalize transcript text"""
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove common YouTube artifacts
    text = text.replace("[Music]", "")
    text = text.replace("[Applause]", "")
    return text.strip()
