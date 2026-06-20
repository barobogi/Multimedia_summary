"""Claude API service for summarization and analysis"""

import logging
import json
from typing import Dict, List, Optional
import anthropic

from ..models import VideoMetadata
from ..config import settings

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def summarize_and_analyze(
    transcript_text: str,
    metadata: VideoMetadata,
    language: str = "ko"
) -> Dict:
    """
    Use Claude to summarize and analyze transcript

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

    # Truncate if too long
    max_chars = 50000  # Reasonable limit for context
    if len(transcript_text) > max_chars:
        logger.warning(f"Transcript too long ({len(transcript_text)} chars), truncating to {max_chars}")
        transcript_text = transcript_text[:max_chars] + "... [내용 이어짐]"

    prompt = build_prompt(transcript_text, metadata, language)

    logger.info(f"Calling Claude API ({settings.claude_model})")

    try:
        message = client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.max_tokens_summary,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse response
        response_text = message.content[0].text

        # Try to extract JSON from response
        result = parse_claude_response(response_text)

        return result

    except Exception as e:
        logger.error(f"Claude API error: {str(e)}")
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
