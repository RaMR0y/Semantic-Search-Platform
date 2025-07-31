from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Request
from typing import List
import asyncpg
from ..schemas import DocumentOut
from ..services import DocumentService, EmbeddingService

router = APIRouter(prefix="/documents", tags=["documents"])

def get_document_service(request: Request) -> DocumentService:
    """Dependency to get document service"""
    db_pool = request.app.state.db
    embedding_service = EmbeddingService()
    return DocumentService(db_pool, embedding_service)

@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service)
):
    """Upload and process a document"""
    try:
        # Read file content
        content = (await file.read()).decode("utf-8")
        
        # Process document
        document_id = await document_service.process_document(file.filename, content)
        
        # Return document info
        return DocumentOut(
            id=document_id,
            filename=file.filename,
            content=content,
            uploaded_at=None  # Will be set by database
        )
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be text-based (UTF-8)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("/", response_model=List[DocumentOut])
async def list_documents(request: Request):
    """List all documents"""
    db_pool = request.app.state.db
    
    async with db_pool.acquire() as conn:
        records = await conn.fetch("SELECT * FROM documents ORDER BY uploaded_at DESC")
        
        return [
            DocumentOut(
                id=record['id'],
                filename=record['filename'],
                content=record['content'],
                uploaded_at=record['uploaded_at']
            )
            for record in records
        ]

@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(document_id: int, request: Request):
    """Get a specific document"""
    db_pool = request.app.state.db
    
    async with db_pool.acquire() as conn:
        record = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", document_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentOut(
            id=record['id'],
            filename=record['filename'],
            content=record['content'],
            uploaded_at=record['uploaded_at']
        )

@router.delete("/{document_id}")
async def delete_document(document_id: int, request: Request):
    """Delete a document and its embeddings"""
    db_pool = request.app.state.db
    
    async with db_pool.acquire() as conn:
        result = await conn.execute("DELETE FROM documents WHERE id = $1", document_id)
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"} 