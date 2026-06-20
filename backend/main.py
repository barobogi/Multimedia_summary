"""
Multimedia Summary Backend - FastAPI Application
Handles video summarization and multi-channel distribution
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.routes import summarize_router, health_router
from app.config import settings

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Multimedia Summary API starting...")
    yield
    logger.info("🛑 Multimedia Summary API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Multimedia Summary API",
    description="Video summarization with AI-powered analysis and multi-channel distribution",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health_router.router, prefix="/api/health", tags=["health"])
app.include_router(summarize_router.router, prefix="/api", tags=["summarize"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Multimedia Summary API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug
    )
