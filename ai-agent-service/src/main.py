"""
AI Agent Service - FastAPI application
Provides AI-powered activity parsing and categorization
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent Service",
    description="AI-powered activity parsing and categorization",
    version="0.1.0"
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for container orchestration
    Returns 200 OK if service is healthy
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "ai-agent-service",
            "version": "0.1.0"
        }
    )


@app.get("/")
async def root():
    """
    Root endpoint with service information
    """
    return {
        "service": "ai-agent-service",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
