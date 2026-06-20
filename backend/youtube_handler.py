import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import yt_dlp


def extract_video_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/watch\?.*v=)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_metadata(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration_secs = info.get("duration", 0)
            hours = duration_secs // 3600
            minutes = (duration_secs % 3600) // 60
            seconds = duration_secs % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
            return {
                "title": info.get("title", "제목 없음"),
                "channel": info.get("uploader", ""),
                "duration": duration_str,
                "description": info.get("description", "")[:2000],
                "upload_date": info.get("upload_date", ""),
                "view_count": info.get("view_count", 0),
                "url": url,
            }
    except Exception as e:
        return {
            "title": "제목 없음",
            "channel": "",
            "duration": "",
            "description": "",
            "upload_date": "",
            "view_count": 0,
            "url": url,
            "error": str(e),
        }


def get_transcript(video_id: str) -> Optional[str]:
    # 한국어 우선, 없으면 영어, 없으면 자동생성 자막
    language_priority = ["ko", "en", "ko-KR", "en-US"]
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # 수동 자막 우선 시도
        for lang in language_priority:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
                entries = transcript.fetch()
                return " ".join(e["text"] for e in entries)
            except Exception:
                continue

        # 자동 생성 자막 시도
        for lang in language_priority:
            try:
                transcript = transcript_list.find_generated_transcript([lang])
                entries = transcript.fetch()
                return " ".join(e["text"] for e in entries)
            except Exception:
                continue

        # 아무 자막이나 가져오기
        try:
            transcripts = transcript_list._manually_created_transcripts
            if not transcripts:
                transcripts = transcript_list._generated_transcripts
            if transcripts:
                lang_code = list(transcripts.keys())[0]
                entries = transcripts[lang_code].fetch()
                return " ".join(e["text"] for e in entries)
        except Exception:
            pass

        return None
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception:
        return None


def get_youtube_content(url: str) -> dict:
    metadata = get_video_metadata(url)
    video_id = extract_video_id(url)
    transcript = None
    if video_id:
        transcript = get_transcript(video_id)

    # 자막이 없으면 설명(description)을 대체 텍스트로 사용
    content_text = transcript or metadata.get("description", "")

    return {
        "title": metadata["title"],
        "channel": metadata["channel"],
        "duration": metadata["duration"],
        "url": url,
        "transcript": transcript,
        "content_text": content_text,
        "has_transcript": transcript is not None,
    }
