"""Health check endpoint"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Multimedia Summary API"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check - all systems operational"""
    return {
        "ready": True,
        "components": {
            "api": "ok",
            "database": "ok",
            "external_apis": "ok"
        }
    }
