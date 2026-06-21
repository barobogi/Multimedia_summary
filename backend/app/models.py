"""Data models for the application"""

from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime


class VideoMetadata(BaseModel):
    """Video metadata from platform"""
    title: str
    url: HttpUrl
    channel: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    publish_date: Optional[str] = None
    thumbnail_url: Optional[str] = None


class TranscriptSegment(BaseModel):
    """Transcript segment"""
    text: str
    start_time: float
    end_time: float


class SummaryRequest(BaseModel):
    """Request model for summarization"""
    video_url: str
    platform: str = "youtube"
    language: str = "ko"
    transcript: Optional[str] = None  # 클라이언트에서 직접 추출해 전달 (클라우드 IP 차단 우회)


class SummaryResponse(BaseModel):
    """Response model for summarization"""
    metadata: VideoMetadata
    summary: str
    key_insights: List[str]
    categories: List[str]  # e.g., ["AI", "Stock", "Learning"]
    stock_related: Optional[List[str]] = None
    ai_related: Optional[List[str]] = None
    learning_related: Optional[List[str]] = None
    timestamp: datetime = datetime.now()
    processing_time_ms: float


class DistributionResult(BaseModel):
    """Distribution result tracking"""
    email_sent: bool = False
    obsidian_saved: bool = False
    github_pages_updated: bool = False
    errors: List[str] = []


class FullResult(BaseModel):
    """Complete result with distribution"""
    summary: SummaryResponse
    distribution: DistributionResult
