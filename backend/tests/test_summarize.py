"""Tests for /api/summarize endpoint (external services mocked)"""

from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime


MOCK_METADATA = {
    "title": "테스트 영상",
    "url": "https://www.youtube.com/watch?v=test123",
    "channel": "Test Channel",
    "description": "테스트 설명",
    "duration": 600,
    "publish_date": "2026-06-20",
    "thumbnail_url": "https://img.youtube.com/vi/test123/0.jpg",
}

MOCK_SUMMARY_RESULT = {
    "summary": "이것은 테스트 요약입니다.",
    "key_insights": ["인사이트 1", "인사이트 2"],
    "categories": ["AI", "학습"],
    "stock_related": [],
    "ai_related": ["GPT", "Claude"],
    "learning_related": ["머신러닝"],
    "timestamp": datetime.now(),
    "processing_time_ms": 0.0,
}


def _make_mock_metadata():
    from app.models import VideoMetadata
    return VideoMetadata(**MOCK_METADATA)


def test_summarize_unsupported_platform(client):
    res = client.post("/api/summarize", json={
        "video_url": "https://vimeo.com/123",
        "platform": "vimeo",
        "language": "ko"
    })
    assert res.status_code == 400
    assert "Unsupported platform" in res.json()["detail"]


def test_summarize_youtube_success(client):
    mock_meta = _make_mock_metadata()

    with patch("app.routes.summarize_router.youtube_service.extract_video_data",
               new_callable=AsyncMock, return_value=(mock_meta, "자막 텍스트")), \
         patch("app.routes.summarize_router.claude_service.summarize_and_analyze",
               new_callable=AsyncMock, return_value=MOCK_SUMMARY_RESULT), \
         patch("app.routes.summarize_router.distribute_summary",
               new_callable=AsyncMock):

        res = client.post("/api/summarize", json={
            "video_url": "https://www.youtube.com/watch?v=test123",
            "platform": "youtube",
            "language": "ko"
        })

    assert res.status_code == 200
    body = res.json()
    assert "summary" in body
    assert body["summary"]["summary"] == "이것은 테스트 요약입니다."
    assert body["summary"]["metadata"]["title"] == "테스트 영상"
    assert "distribution" in body


def test_summarize_youtube_extraction_error(client):
    with patch("app.routes.summarize_router.youtube_service.extract_video_data",
               new_callable=AsyncMock, side_effect=Exception("자막 없음")):
        res = client.post("/api/summarize", json={
            "video_url": "https://www.youtube.com/watch?v=bad",
            "platform": "youtube",
            "language": "ko"
        })

    assert res.status_code == 500
    assert "자막 없음" in res.json()["detail"]
