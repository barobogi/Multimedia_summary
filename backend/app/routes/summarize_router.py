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
    # TODO: Implement caching/retrieval from database
    raise HTTPException(status_code=501, detail="Not implemented yet")
