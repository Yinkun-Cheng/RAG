"""
AI Test Assistant Service - Main Entry Point

This is the main FastAPI application for the AI Test Assistant service.
It provides endpoints for test case generation using LangChain and Claude 4.5 Sonnet.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys

from app.config import settings
from app.api import router


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting AI Test Assistant Service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Service URL: http://{settings.HOST}:{settings.PORT}")
    
    # Startup
    yield
    
    # Shutdown
    logger.info("👋 Shutting down AI Test Assistant Service...")


# Create FastAPI application
app = FastAPI(
    title="AI Test Assistant Service",
    description="AI-powered test case generation service using LangChain and Claude 4.5 Sonnet",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/ai")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-test-assistant",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Test Assistant Service",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
