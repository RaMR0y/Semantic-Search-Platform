from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import connect_db, close_db
from .routers import documents, search

app = FastAPI(
    title="Semantic Search Q&A Platform",
    description="An end-to-end semantic search and question-answering platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database event handlers
app.add_event_handler("startup", lambda: connect_db(app))
app.add_event_handler("shutdown", lambda: close_db(app))

# Include routers
app.include_router(documents.router)
app.include_router(search.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Semantic Search Q&A Platform",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "upload_document": "/documents/upload",
            "list_documents": "/documents/",
            "search": "/search/query",
            "query_logs": "/search/logs",
            "system_stats": "/search/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "semantic-search-platform"} 