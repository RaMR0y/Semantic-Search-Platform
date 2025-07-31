import asyncio
import time
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import asyncpg
from .schemas import SearchResult, SearchResponse

class EmbeddingService:
    def __init__(self):
        # Initialize Sentence-BERT model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

class DocumentService:
    def __init__(self, db_pool: asyncpg.Pool, embedding_service: EmbeddingService):
        self.db_pool = db_pool
        self.embedding_service = embedding_service
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    async def process_document(self, filename: str, content: str) -> int:
        """Process document: store content and generate embeddings"""
        async with self.db_pool.acquire() as conn:
            # Insert document
            document_record = await conn.fetchrow(
                "INSERT INTO documents (filename, content) VALUES ($1, $2) RETURNING id",
                filename, content
            )
            document_id = document_record['id']
            
            # Chunk the content
            chunks = self.chunk_text(content)
            
            # Generate embeddings for chunks
            embeddings = self.embedding_service.generate_embeddings_batch(chunks)
            
            # Store embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                await conn.execute(
                    "INSERT INTO embeddings (document_id, chunk_index, chunk_text, vector) VALUES ($1, $2, $3, $4)",
                    document_id, i, chunk, embedding
                )
            
            return document_id

class SearchService:
    def __init__(self, db_pool: asyncpg.Pool, embedding_service: EmbeddingService):
        self.db_pool = db_pool
        self.embedding_service = embedding_service
    
    async def search(self, query: str, top_k: int = 5) -> SearchResponse:
        """Perform semantic search"""
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        async with self.db_pool.acquire() as conn:
            # Perform vector similarity search
            results = await conn.fetch("""
                SELECT 
                    e.id as embedding_id,
                    e.chunk_text,
                    e.chunk_index,
                    d.filename,
                    d.id as document_id,
                    1 - (e.vector <=> $1) as score
                FROM embeddings e
                JOIN documents d ON e.document_id = d.id
                ORDER BY e.vector <=> $1
                LIMIT $2
            """, query_embedding, top_k)
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    score=float(row['score']),
                    chunk_text=row['chunk_text'],
                    filename=row['filename'],
                    chunk_index=row['chunk_index'],
                    document_id=row['document_id']
                )
                for row in results
            ]
        
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return SearchResponse(
            query=query,
            results=search_results,
            total_results=len(search_results),
            response_time_ms=response_time
        )
    
    async def log_query_and_responses(self, query: str, search_response: SearchResponse) -> int:
        """Log query and responses to database"""
        async with self.db_pool.acquire() as conn:
            # Insert query
            query_record = await conn.fetchrow(
                "INSERT INTO queries (query_text) VALUES ($1) RETURNING id",
                query
            )
            query_id = query_record['id']
            
            # Insert responses
            for result in search_response.results:
                await conn.execute(
                    "INSERT INTO responses (query_id, embedding_id, score, response_text) VALUES ($1, $2, $3, $4)",
                    query_id, result.embedding_id, result.score, result.chunk_text
                )
            
            return query_id 