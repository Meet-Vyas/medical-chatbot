"""
FastAPI Backend Application
Wraps the existing QueryPipeline with a REST API
"""

import sys
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path to import existing modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.query_pipeline import QueryPipeline
from backend.api.routes import router, set_pipeline
from core import config

# Setup logging
# Resolve log file path relative to project root
log_file_path = os.path.join(project_root, config.LOG_FILE)
log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Medical Knowledge Graph Chatbot API",
    description="REST API for the Medical Knowledge Graph Chatbot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["api"])

# Initialize pipeline on startup
pipeline_instance = None


@app.on_event("startup")
async def startup_event():
    """Initialize the query pipeline on startup"""
    global pipeline_instance
    logger.info("="*80)
    logger.info("INITIALIZING BACKEND API")
    logger.info("="*80)
    
    try:
        logger.info("Initializing QueryPipeline...")
        pipeline_instance = QueryPipeline()
        set_pipeline(pipeline_instance)
        logger.info("✓ Backend API ready!")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global pipeline_instance
    if pipeline_instance:
        logger.info("Closing pipeline connections...")
        try:
            pipeline_instance.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        logger.info("✓ Cleanup complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical Knowledge Graph Chatbot API",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "query": "/api/query"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

