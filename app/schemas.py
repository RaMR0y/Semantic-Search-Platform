from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Document schemas
class DocumentBase(BaseModel):
    filename: str
    content: str

class DocumentCreate(DocumentBase):
    pass

class DocumentOut(DocumentBase):
    id: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

# Embedding schemas
class EmbeddingBase(BaseModel):
    document_id: int
    chunk_index: int
    chunk_text: str
    vector: List[float]

class EmbeddingCreate(EmbeddingBase):
    pass

class EmbeddingOut(EmbeddingBase):
    id: int
    
    class Config:
        from_attributes = True

# Query schemas
class QueryBase(BaseModel):
    query_text: str

class QueryCreate(QueryBase):
    pass

class QueryOut(QueryBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Response schemas
class ResponseBase(BaseModel):
    query_id: int
    embedding_id: int
    score: float
    response_text: str

class ResponseCreate(ResponseBase):
    pass

class ResponseOut(ResponseBase):
    id: int
    
    class Config:
        from_attributes = True

# Search schemas
class SearchQuery(BaseModel):
    query: str = Field(..., description="Natural language query")
    top_k: int = Field(default=5, description="Number of top results to return")

class SearchResult(BaseModel):
    score: float
    chunk_text: str
    filename: str
    chunk_index: int
    document_id: int

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    response_time_ms: float

# Admin schemas
class QueryLog(BaseModel):
    id: int
    query_text: str
    timestamp: datetime
    response_count: int
    avg_score: float
    
    class Config:
        from_attributes = True

class SystemStats(BaseModel):
    total_documents: int
    total_embeddings: int
    total_queries: int
    avg_response_time_ms: float 