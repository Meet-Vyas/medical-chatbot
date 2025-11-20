"""
API Routes
"""

import sys
import os
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict

# Add parent directory to path to import existing modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import from backend package
from backend.api.models import QueryRequest, QueryResponse, SourceResponse, TimingResponse, HealthResponse
# Import from core package
from core.query_pipeline import QueryPipeline

logger = logging.getLogger(__name__)

router = APIRouter()

# Global pipeline instance (initialized in app.py)
pipeline: QueryPipeline = None


def set_pipeline(p: QueryPipeline):
    """Set the query pipeline instance"""
    global pipeline
    pipeline = p


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Basic check - if pipeline is initialized, we're ready
        if pipeline is None:
            return HealthResponse(
                status="initializing",
                message="Pipeline is being initialized"
            )
        
        return HealthResponse(
            status="healthy",
            message="Backend is ready"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query through the pipeline"""
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline is not initialized. Please wait a moment and try again."
        )
    
    try:
        # Process query using existing pipeline
        result = pipeline.process_query(request.query, verbose=request.verbose)
        
        # Convert sources to response model
        sources = [
            SourceResponse(
                substance_name=src.get('substance_name', ''),
                section_name=src.get('section_name', ''),
                similarity_score=src.get('similarity_score'),
                cross_encoder_score=src.get('cross_encoder_score')
            )
            for src in result.get('sources', [])
        ]
        
        # Convert timing to response model
        timing_data = result.get('timing', {})
        timing = TimingResponse(
            total=timing_data.get('total', 0.0),
            vector_search=timing_data.get('vector_search'),
            reranking=timing_data.get('reranking'),
            llm_generation=timing_data.get('llm_generation')
        )
        
        # Build response
        response = QueryResponse(
            answer=result.get('answer', ''),
            sources=sources,
            timing=timing,
            error=result.get('error')
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

