"""
API Request/Response Models
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str
    verbose: bool = False


class SourceResponse(BaseModel):
    """Source information in response"""
    substance_name: str
    section_name: str
    similarity_score: Optional[float] = None
    cross_encoder_score: Optional[float] = None


class TimingResponse(BaseModel):
    """Timing information in response"""
    total: float
    vector_search: Optional[float] = None
    reranking: Optional[float] = None
    llm_generation: Optional[float] = None


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    answer: str
    sources: List[SourceResponse]
    timing: TimingResponse
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str

