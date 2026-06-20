from pydantic import BaseModel
from typing import Optional, List


class ProcessRequest(BaseModel):
    url: str
    secret_key: str


class StockInsight(BaseModel):
    ticker: Optional[str] = None
    company: Optional[str] = None
    content: str
    additional_info: Optional[str] = None


class ProcessResult(BaseModel):
    video_title: str
    video_url: str
    channel: Optional[str] = None
    duration: Optional[str] = None
    summary: str
    key_insights: List[str]
    stock_insights: List[StockInsight]
    ai_insights: List[str]
    learning_insights: List[str]
    obsidian_path: Optional[str] = None
    web_posted: bool = False
    email_sent: bool = False
    error: Optional[str] = None


class ProcessResponse(BaseModel):
    success: bool
    result: Optional[ProcessResult] = None
    message: str
