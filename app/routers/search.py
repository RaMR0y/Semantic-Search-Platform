from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from ..schemas import SearchQuery, SearchResponse, QueryLog
from ..services import SearchService, EmbeddingService

router = APIRouter(prefix="/search", tags=["search"])

def get_search_service(request: Request) -> SearchService:
    """Dependency to get search service"""
    db_pool = request.app.state.db
    embedding_service = EmbeddingService()
    return SearchService(db_pool, embedding_service)

@router.post("/query", response_model=SearchResponse)
async def search_documents(
    search_query: SearchQuery,
    search_service: SearchService = Depends(get_search_service)
):
    """Perform semantic search on documents"""
    try:
        # Perform search
        search_response = await search_service.search(search_query.query, search_query.top_k)
        
        # Log query and responses
        await search_service.log_query_and_responses(search_query.query, search_response)
        
        return search_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/logs", response_model=List[QueryLog])
async def get_query_logs(request: Request, limit: int = 50):
    """Get query logs with performance metrics"""
    db_pool = request.app.state.db
    
    async with db_pool.acquire() as conn:
        records = await conn.fetch("""
            SELECT 
                q.id,
                q.query_text,
                q.timestamp,
                COUNT(r.id) as response_count,
                AVG(r.score) as avg_score
            FROM queries q
            LEFT JOIN responses r ON q.id = r.query_id
            GROUP BY q.id, q.query_text, q.timestamp
            ORDER BY q.timestamp DESC
            LIMIT $1
        """, limit)
        
        return [
            QueryLog(
                id=record['id'],
                query_text=record['query_text'],
                timestamp=record['timestamp'],
                response_count=record['response_count'],
                avg_score=float(record['avg_score']) if record['avg_score'] else 0.0
            )
            for record in records
        ]

@router.get("/stats")
async def get_system_stats(request: Request):
    """Get system statistics"""
    db_pool = request.app.state.db
    
    async with db_pool.acquire() as conn:
        # Get counts
        doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
        embedding_count = await conn.fetchval("SELECT COUNT(*) FROM embeddings")
        query_count = await conn.fetchval("SELECT COUNT(*) FROM queries")
        
        # Get average response time (simplified - in real app you'd track this)
        avg_response_time = 150.0  # Placeholder
        
        return {
            "total_documents": doc_count,
            "total_embeddings": embedding_count,
            "total_queries": query_count,
            "avg_response_time_ms": avg_response_time
        } 