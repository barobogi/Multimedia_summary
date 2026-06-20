"""YouTube video extraction service"""

import logging
from typing import Tuple
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import re

from ..models import VideoMetadata
from ..config import settings

logger = logging.getLogger(__name__)


async def extract_video_data(video_url: str, language: str = "ko") -> Tuple[VideoMetadata, str]:
    """
    Extract video metadata and transcript from YouTube

    Args:
        video_url: YouTube video URL
        language: Transcript language (default: Korean)

    Returns:
        Tuple of (VideoMetadata, transcript_text)
    """

    # Extract video ID
    video_id = extract_youtube_id(video_url)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {video_url}")

    # Extract metadata using yt-dlp
    logger.info(f"Extracting metadata for: {video_id}")
    metadata = await extract_metadata(video_id)

    # Extract transcript
    logger.info(f"Extracting transcript for: {video_id}")
    transcript = await extract_transcript(video_id, language)

    return metadata, transcript


def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return ""


async def extract_metadata(video_id: str) -> VideoMetadata:
    """Extract video metadata using yt-dlp"""

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)

            return VideoMetadata(
                title=info.get('title', 'Unknown'),
                url=f'https://www.youtube.com/watch?v={video_id}',
                channel=info.get('channel', None),
                description=info.get('description', None),
                duration=info.get('duration', None),
                publish_date=info.get('upload_date', None),
                thumbnail_url=info.get('thumbnail', None)
            )
    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        raise


async def extract_transcript(video_id: str, language: str = "ko") -> str:
    """
    Extract transcript from YouTube video

    Priority: Korean > English > any available
    """

    try:
        # Try to get transcript in requested language
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        logger.info(f"Got transcript in {language}")
    except:
        try:
            # Fallback to English
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            logger.info("Fallback to English transcript")
        except:
            try:
                # Get available transcripts
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                # Use first available
                transcript = transcript_list.primary.fetch()
                logger.info("Using available transcript")
            except Exception as e:
                logger.error(f"Could not extract transcript: {str(e)}")
                raise ValueError(f"Cannot extract transcript: {str(e)}")

    # Combine transcript segments
    transcript_text = " ".join([item['text'] for item in transcript])

    # Clean up text
    transcript_text = clean_transcript(transcript_text)

    return transcript_text


def clean_transcript(text: str) -> str:
    """Clean and normalize transcript text"""
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove common YouTube artifacts
    text = text.replace("[Music]", "")
    text = text.replace("[Applause]", "")
    return text.strip()
