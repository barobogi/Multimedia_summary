# claude_service.py — Claude Code CLI subprocess로 요약 생성 (Anthropic API 크레딧 Zero)

import logging
import json
import asyncio
from typing import Dict, List, Optional

from ..models import VideoMetadata

logger = logging.getLogger(__name__)


async def summarize_and_analyze(
    transcript_text: str,
    metadata: VideoMetadata,
    language: str = "ko"
) -> Dict:
    """
    Claude Code CLI subprocess로 자막 요약/분석 (API 크레딧 소비 없음).

    Returns:
        {
            "summary": str,
            "key_insights": List[str],
            "categories": List[str],
            "stock_related": List[str],
            "ai_related": List[str],
            "learning_related": List[str]
        }
    """

    max_chars = 50000
    if len(transcript_text) > max_chars:
        logger.warning(f"Transcript too long ({len(transcript_text)} chars), truncating to {max_chars}")
        transcript_text = transcript_text[:max_chars] + "... [내용 이어짐]"

    prompt = build_prompt(transcript_text, metadata, language)

    logger.info("Calling Claude via CLI subprocess (API Zero mode)")

    try:
        proc = await asyncio.create_subprocess_exec(
            "claude", "--output-format", "json", "--print",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=prompt.encode("utf-8")),
            timeout=120,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Claude CLI error: {stderr.decode('utf-8', errors='replace')}")

        # --output-format json 구조: {"result": "...", "cost_usd": 0, ...}
        outer = json.loads(stdout.decode("utf-8"))
        response_text = outer.get("result", stdout.decode("utf-8"))

        return parse_claude_response(response_text)

    except asyncio.TimeoutError:
        logger.error("Claude CLI timeout (120s)")
        raise
    except Exception as e:
        logger.error(f"Claude CLI error: {str(e)}")
        raise


def build_prompt(transcript: str, metadata: VideoMetadata, language: str) -> str:
    """Build the prompt for Claude"""

    if language == "ko":
        prompt = f"""다음 동영상의 자막을 분석해주세요.

**동영상 정보:**
- 제목: {metadata.title}
- 채널: {metadata.channel or '미정'}
- 설명: {metadata.description or '없음'}

**자막 내용:**
{transcript}

---

다음 형식의 JSON으로 응답해주세요:

{{
  "summary": "3-5문장의 핵심 요약",
  "key_insights": ["인사이트1", "인사이트2", "인사이트3"],
  "categories": ["카테고리1", "카테고리2"],
  "stock_related": ["주식/자본 관련 내용1", "주식/자본 관련 내용2"],
  "ai_related": ["AI/ML 관련 내용1", "AI/ML 관련 내용2"],
  "learning_related": ["학습 관련 내용1", "학습 관련 내용2"]
}}

**주의:**
- stock_related: 주식, 투자, 자본, 재정, 경제 관련 내용만
- ai_related: 인공지능, 머신러닝, 딥러닝, 모델 관련 내용
- learning_related: 학습, 교육, 스킬 개발 관련 내용
- 해당 내용이 없으면 빈 배열로 반환
- 반드시 유효한 JSON 형식으로 응답"""

    else:
        prompt = f"""Analyze the following video transcript.

**Video Information:**
- Title: {metadata.title}
- Channel: {metadata.channel or 'Unknown'}
- Description: {metadata.description or 'None'}

**Transcript:**
{transcript}

---

Respond in JSON format:

{{
  "summary": "3-5 sentence summary",
  "key_insights": ["insight1", "insight2", "insight3"],
  "categories": ["category1", "category2"],
  "stock_related": ["stock-related content 1"],
  "ai_related": ["AI-related content 1"],
  "learning_related": ["learning-related content 1"]
}}"""

    return prompt


def parse_claude_response(response_text: str) -> Dict:
    """Parse Claude's JSON response"""

    # Try to extract JSON from the response
    try:
        # Look for JSON block
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)

            # Ensure required fields
            result.setdefault('summary', 'No summary available')
            result.setdefault('key_insights', [])
            result.setdefault('categories', [])
            result.setdefault('stock_related', [])
            result.setdefault('ai_related', [])
            result.setdefault('learning_related', [])

            return result
        else:
            raise ValueError("No JSON found in response")

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {str(e)}")
        # Return default response
        return {
            "summary": response_text[:200],
            "key_insights": [],
            "categories": [],
            "stock_related": [],
            "ai_related": [],
            "learning_related": []
        }
