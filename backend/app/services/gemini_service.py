"""Gemini API service — YouTube 영상 직접 요약"""

import os
import asyncio
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

GEMINI_MODEL = "models/gemini-2.5-flash"


def _sync_extract(video_url: str, prompt: str) -> str:
    """동기 Gemini 호출 — run_in_executor에서 실행"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 없습니다.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content([
        {"file_data": {"file_uri": video_url, "mime_type": "video/mp4"}},
        prompt
    ])
    return response.text.strip()


async def extract_transcript_via_gemini(video_url: str, language: str = "ko") -> str:
    """
    Gemini로 YouTube 영상 내용을 텍스트로 추출.
    클라우드 IP 차단 우회 — Gemini는 YouTube 직접 접근 가능.
    """
    lang_name = "한국어" if language == "ko" else "English"
    prompt = (
        f"이 YouTube 영상의 내용을 {lang_name}로 상세하게 텍스트로 작성해주세요. "
        "영상에서 말하는 내용을 최대한 완전하게 옮겨주세요. "
        "타임스탬프나 설명 없이 순수하게 내용만 작성해주세요."
    )

    logger.info(f"Gemini transcript extraction: {video_url}")

    loop = asyncio.get_event_loop()
    transcript = await loop.run_in_executor(None, _sync_extract, video_url, prompt)

    logger.info(f"Gemini transcript: {len(transcript)} chars")
    return transcript
