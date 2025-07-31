import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
import asyncpg

# Test data
SAMPLE_DOCUMENT = {
    "filename": "test_document.txt",
    "content": "This is a test document about artificial intelligence and machine learning. It contains information about neural networks and deep learning algorithms."
}

SAMPLE_QUERY = {
    "query": "What is machine learning?",
    "top_k": 3
}

@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_pool():
    """Create test database pool"""
    pool = await asyncpg.create_pool(
        user="appuser",
        password="apppass",
        database="semsearch",
        host="localhost"
    )
    yield pool
    await pool.close()

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Semantic Search Q&A Platform"
    assert "endpoints" in data

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_upload_document(client):
    """Test document upload endpoint"""
    # Create a file-like object
    files = {"file": ("test_document.txt", SAMPLE_DOCUMENT["content"], "text/plain")}
    response = await client.post("/documents/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_document.txt"
    assert data["content"] == SAMPLE_DOCUMENT["content"]
    assert "id" in data

@pytest.mark.asyncio
async def test_list_documents(client):
    """Test list documents endpoint"""
    response = await client.get("/documents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_search_query(client):
    """Test search endpoint"""
    response = await client.post("/search/query", json=SAMPLE_QUERY)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == SAMPLE_QUERY["query"]
    assert "results" in data
    assert "total_results" in data
    assert "response_time_ms" in data

@pytest.mark.asyncio
async def test_query_logs(client):
    """Test query logs endpoint"""
    response = await client.get("/search/logs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_system_stats(client):
    """Test system stats endpoint"""
    response = await client.get("/search/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_embeddings" in data
    assert "total_queries" in data
    assert "avg_response_time_ms" in data

@pytest.mark.asyncio
async def test_get_document(client):
    """Test get specific document endpoint"""
    # First upload a document
    files = {"file": ("test_doc.txt", "Test content", "text/plain")}
    upload_response = await client.post("/documents/upload", files=files)
    doc_id = upload_response.json()["id"]
    
    # Then retrieve it
    response = await client.get(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["filename"] == "test_doc.txt"

@pytest.mark.asyncio
async def test_delete_document(client):
    """Test delete document endpoint"""
    # First upload a document
    files = {"file": ("test_doc_delete.txt", "Test content", "text/plain")}
    upload_response = await client.post("/documents/upload", files=files)
    doc_id = upload_response.json()["id"]
    
    # Then delete it
    response = await client.delete(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document deleted successfully"
    
    # Verify it's deleted
    get_response = await client.get(f"/documents/{doc_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_invalid_document_id(client):
    """Test getting non-existent document"""
    response = await client.get("/documents/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

@pytest.mark.asyncio
async def test_invalid_search_query(client):
    """Test search with invalid query"""
    response = await client.post("/search/query", json={"query": "", "top_k": 0})
    # This should still work but return empty results
    assert response.status_code == 200 