"""Summarization endpoint router"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
from datetime import datetime

from ..models import SummaryRequest, SummaryResponse, FullResult
from ..services import (
    youtube_service,
    claude_service,
    gmail_service,
    obsidian_service,
    github_service
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/summarize", response_model=FullResult)
async def summarize_video(request: SummaryRequest, background_tasks: BackgroundTasks):
    """
    Summarize a video and distribute across channels

    1. Extract metadata and transcript
    2. Generate summary using Claude
    3. Identify key insights and categories
    4. Distribute to: email, Obsidian, GitHub Pages
    """

    try:
        start_time = datetime.now()

        # Step 1: Extract video metadata and transcript
        logger.info(f"Processing: {request.video_url}")

        if request.platform.lower() == "youtube":
            if request.transcript:
                # 클라이언트(앱)가 자막을 직접 추출해 전달 → 서버는 메타데이터만 가져옴
                metadata = await youtube_service.extract_metadata_only(request.video_url)
                transcript = request.transcript
                logger.info("Using client-provided transcript (bypassing cloud IP ban)")
            else:
                metadata, transcript = await youtube_service.extract_video_data(request.video_url)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported platform: {request.platform}"
            )

        # Step 2: Generate summary using Claude
        logger.info(f"Summarizing: {metadata.title}")
        summary_result = await claude_service.summarize_and_analyze(
            transcript_text=transcript,
            metadata=metadata,
            language=request.language
        )

        # Step 3: Create full response
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        full_response = SummaryResponse(
            **summary_result,
            metadata=metadata,
            processing_time_ms=processing_time
        )

        # Step 4: Background distribution tasks
        background_tasks.add_task(
            distribute_summary,
            full_response
        )

        return FullResult(
            summary=full_response,
            distribution={
                "email_sent": False,
                "obsidian_saved": False,
                "github_pages_updated": False,
                "errors": []
            }
        )

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def distribute_summary(summary: SummaryResponse):
    """
    Background task: Distribute summary to all channels
    """
    distribution_errors = []

    # Gmail
    try:
        await gmail_service.send_summary(summary)
        logger.info(f"✉️  Email sent for: {summary.metadata.title}")
    except Exception as e:
        logger.error(f"Gmail error: {str(e)}")
        distribution_errors.append(f"Gmail: {str(e)}")

    # Obsidian (OneDrive)
    try:
        await obsidian_service.save_to_obsidian(summary)
        logger.info(f"📝 Obsidian saved for: {summary.metadata.title}")
    except Exception as e:
        logger.error(f"Obsidian error: {str(e)}")
        distribution_errors.append(f"Obsidian: {str(e)}")

    # GitHub Pages
    try:
        await github_service.update_github_pages(summary)
        logger.info(f"🌐 GitHub Pages updated for: {summary.metadata.title}")
    except Exception as e:
        logger.error(f"GitHub Pages error: {str(e)}")
        distribution_errors.append(f"GitHub: {str(e)}")

    if distribution_errors:
        logger.warning(f"Distribution errors: {distribution_errors}")


@router.get("/summarize/{video_id}")
async def get_summary(video_id: str):
    """Get a previously generated summary (if cached)"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ─── Gemini 테스트 엔드포인트 ────────────────────────────────────────────────
from pydantic import BaseModel
import os

class GeminiTestRequest(BaseModel):
    youtube_url: str
    prompt: str = "이 YouTube 영상을 한국어로 요약해주세요."

@router.get("/gemini-models")
async def gemini_list_models():
    """사용 가능한 Gemini 모델 목록 확인"""
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY 없음")
    genai.configure(api_key=api_key)
    models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    return {"models": models}

@router.post("/gemini-test")
async def gemini_test(request: GeminiTestRequest):
    """
    Gemini API로 YouTube URL 직접 요약 테스트.
    GEMINI_API_KEY 환경변수 필요.
    """
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY 환경변수가 없습니다.")

    try:
        genai.configure(api_key=api_key)
        # 사용 가능한 모델 순서대로 시도
        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro-latest"]
        last_error = None

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([
                    {"file_data": {"file_uri": request.youtube_url, "mime_type": "video/mp4"}},
                    request.prompt
                ])
                return {
                    "success": True,
                    "youtube_url": request.youtube_url,
                    "summary": response.text,
                    "model": model_name
                }
            except Exception as e:
                last_error = f"{model_name}: {str(e)}"
                logger.warning(f"Model {model_name} failed: {e}")
                continue

        raise Exception(f"모든 모델 실패. 마지막 오류: {last_error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini 오류: {str(e)}")
