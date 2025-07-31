# Semantic Search & Q&A Platform - Design Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Goals & Scope](#goals--scope)
3. [Functional Requirements](#functional-requirements)
4. [Non-Functional Requirements](#non-functional-requirements)
5. [System Architecture](#system-architecture)
6. [Database Design](#database-design)
7. [Key Workflows & Sequence Diagrams](#key-workflows--sequence-diagrams)
8. [UI Wireframes](#ui-wireframes)
9. [Deployment & Operations](#deployment--operations)
10. [Limitations & Future Improvements](#limitations--future-improvements)

## Executive Summary

**Problem**: Organizations struggle to efficiently search through large document collections and extract relevant information using traditional keyword-based search methods, leading to time-consuming manual document review and missed insights.

**Users**: Knowledge workers, researchers, support teams, and content managers who need to quickly find relevant information across document repositories and answer questions based on document content.

**Solution**: A semantic search platform that uses AI-powered embeddings to understand document meaning and user intent, enabling natural language queries that return contextually relevant results with source metadata.

## Goals & Scope

### Objectives
1. Enable users to upload documents and perform semantic search with 95%+ relevance accuracy
2. Provide sub-second response times for search queries across 10,000+ document chunks
3. Support natural language questions and return answers with source attribution
4. Track and monitor search performance and user query patterns
5. Deliver a web-based interface accessible to non-technical users

### In-Scope
- Document upload and processing (text files)
- Automatic text chunking and embedding generation
- Semantic search with vector similarity
- Query logging and analytics
- RESTful API with comprehensive documentation
- Web-based user interface
- Performance monitoring and health checks

### Out-of-Scope
- User authentication and role-based access control
- PDF/DOCX file processing (text extraction)
- Real-time collaborative features
- Mobile application
- Advanced analytics and reporting dashboards
- Multi-language support beyond English

## Functional Requirements

| # | Requirement ID | Description | Priority |
|---|----------------|-------------|----------|
| FR1 | Document Upload | Users can upload text documents (.txt, .md, .json) via web interface or API | H |
| FR2 | Document Processing | System automatically chunks documents and generates embeddings | H |
| FR3 | Semantic Search | Users can search documents using natural language queries | H |
| FR4 | Result Ranking | System returns top-k most relevant results with similarity scores | H |
| FR5 | Source Attribution | Each result includes source document and chunk information | H |
| FR6 | Query Logging | All searches are logged with timestamps and performance metrics | M |
| FR7 | System Statistics | Admin can view system stats (documents, embeddings, queries) | M |
| FR8 | Document Management | Users can list, view, and delete uploaded documents | M |
| FR9 | Health Monitoring | System provides health check endpoints for monitoring | L |
| FR10 | API Documentation | Interactive API documentation with examples | L |

## Non-Functional Requirements

**Performance**: 
- Search response time ≤ 500ms for queries across 10,000+ embeddings
- Document processing ≤ 30 seconds for 10MB text files
- Support for 100+ concurrent users

**Security**: 
- Input validation and sanitization for all user inputs
- SQL injection prevention through parameterized queries
- CORS configuration for web interface integration

**Reliability**: 
- 99.5% uptime target
- Graceful error handling with meaningful error messages
- Database connection pooling for stability

**Scalability**: 
- Horizontal scaling capability through stateless API design
- Vector index optimization for large document collections
- Configurable chunk sizes and overlap for different use cases

**Usability**: 
- Intuitive web interface requiring no technical training
- Clear error messages and loading indicators
- Responsive design for desktop and tablet use

## System Architecture

### High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Web Interface<br/>HTML/CSS/JS]
    end
    
    subgraph "API Layer"
        API[FastAPI Backend<br/>REST API]
        Auth[Authentication<br/>Middleware]
        CORS[CORS<br/>Middleware]
    end
    
    subgraph "Business Logic Layer"
        DocSvc[Document Service<br/>Chunking & Processing]
        SearchSvc[Search Service<br/>Vector Search]
        EmbedSvc[Embedding Service<br/>Sentence-BERT]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>+ pgvector)]
        Cache[(Optional Cache<br/>Redis)]
    end
    
    subgraph "External Services"
        Model[AI Model<br/>Sentence-BERT]
    end
    
    UI --> API
    API --> Auth
    API --> CORS
    API --> DocSvc
    API --> SearchSvc
    DocSvc --> EmbedSvc
    SearchSvc --> EmbedSvc
    EmbedSvc --> Model
    DocSvc --> DB
    SearchSvc --> DB
    API --> Cache
```

### Technology Stack

**Backend**: FastAPI (Python) - High-performance async web framework
**Database**: PostgreSQL 14 with pgvector extension - Vector similarity search
**Embeddings**: Sentence-BERT (all-MiniLM-L6-v2) - 384-dimensional vectors
**Frontend**: HTML/CSS/JavaScript - Lightweight web interface
**Containerization**: Docker & Docker Compose - Easy deployment
**Testing**: pytest - Comprehensive test coverage

## Database Design

### ER Diagram

```mermaid
erDiagram
    documents ||--o{ embeddings : "has"
    queries ||--o{ responses : "generates"
    embeddings ||--o{ responses : "referenced_in"
    
    documents {
        int id PK
        text filename
        text content
        timestamptz uploaded_at
    }
    
    embeddings {
        int id PK
        int document_id FK
        int chunk_index
        text chunk_text
        vector vector
    }
    
    queries {
        int id PK
        text query_text
        timestamptz timestamp
    }
    
    responses {
        int id PK
        int query_id FK
        int embedding_id FK
        real score
        text response_text
    }
```

### Schema Definition

```sql
-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Embeddings table with vector support
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    vector vector(384),
    UNIQUE(document_id, chunk_index)
);

-- Queries table
CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Responses table
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    query_id INT NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    embedding_id INT NOT NULL REFERENCES embeddings(id),
    score REAL NOT NULL,
    response_text TEXT NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (vector vector_l2_ops) WITH (lists = 100);
CREATE INDEX idx_responses_score ON responses(score DESC);
CREATE INDEX idx_queries_timestamp ON queries(timestamp DESC);
```

### Data Dictionary

| Table | Column | Type | Description |
|-------|--------|------|-------------|
| documents | id | SERIAL PK | Unique document identifier |
| documents | filename | TEXT | Original filename of uploaded document |
| documents | content | TEXT | Full text content of the document |
| documents | uploaded_at | TIMESTAMPTZ | Timestamp when document was uploaded |
| embeddings | id | SERIAL PK | Unique embedding identifier |
| embeddings | document_id | INT FK | Reference to parent document |
| embeddings | chunk_index | INT | Position of chunk within document |
| embeddings | chunk_text | TEXT | Text content of this chunk |
| embeddings | vector | vector(384) | 384-dimensional embedding vector |
| queries | id | SERIAL PK | Unique query identifier |
| queries | query_text | TEXT | Natural language search query |
| queries | timestamp | TIMESTAMPTZ | When query was executed |
| responses | id | SERIAL PK | Unique response identifier |
| responses | query_id | INT FK | Reference to parent query |
| responses | embedding_id | INT FK | Reference to matching embedding |
| responses | score | REAL | Similarity score (0-1) |
| responses | response_text | TEXT | Text content of the response |

## Key Workflows & Sequence Diagrams

### 1. Document Upload and Processing

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Document Service
    participant E as Embedding Service
    participant DB as Database
    
    U->>F: Upload document file
    F->>A: POST /documents/upload
    A->>D: process_document(filename, content)
    D->>D: chunk_text(content)
    D->>E: generate_embeddings_batch(chunks)
    E->>E: Sentence-BERT encoding
    E-->>D: embeddings[]
    D->>DB: INSERT document
    D->>DB: INSERT embeddings[]
    D-->>A: document_id
    A-->>F: Document created response
    F-->>U: Upload success
```

### 2. Semantic Search

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant S as Search Service
    participant E as Embedding Service
    participant DB as Database
    
    U->>F: Enter search query
    F->>A: POST /search/query
    A->>S: search(query, top_k)
    S->>E: generate_embedding(query)
    E->>E: Sentence-BERT encoding
    E-->>S: query_embedding
    S->>DB: Vector similarity search
    DB-->>S: top_k results
    S->>DB: Log query and responses
    S-->>A: SearchResponse
    A-->>F: Search results
    F-->>U: Display results with scores
```

### 3. System Monitoring

```mermaid
sequenceDiagram
    participant A as Admin
    participant F as Frontend
    participant A as API
    participant DB as Database
    
    A->>F: Request system stats
    F->>A: GET /search/stats
    A->>DB: COUNT queries, documents, embeddings
    DB-->>A: Statistics
    A-->>F: System stats
    F-->>A: Display dashboard
    
    A->>F: Request query logs
    F->>A: GET /search/logs
    A->>DB: SELECT recent queries with metrics
    DB-->>A: Query logs
    A-->>F: Query history
    F-->>A: Display logs table
```

## UI Wireframes

### Main Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Semantic Search Q&A Platform                             
├─────────────────────────────────────────────────────────────┤
│ 📄 Upload Documents                                        
│ ┌─────────────────────────────────────────────────────────┐ 
│ │ Choose File: [Browse...] [Upload Document]              │ 
│ └─────────────────────────────────────────────────────────┘ 
├─────────────────────────────────────────────────────────────┤
│ 🔎 Search Documents                                        
│ ┌─────────────────────────────────────────────────────────┐
│ │ Enter your question:                                    │
│ │ ┌─────────────────────────────────────────────────────┐ │ 
│ │ │ What is machine learning?                           │ │ 
│ │ └─────────────────────────────────────────────────────┘ │ 
│ │ Results: [3] [5] [10] [Search]                          │
│ └─────────────────────────────────────────────────────────┘ 
├─────────────────────────────────────────────────────────────┤
│ 📊 System Statistics                                        
│ ┌─────────────┬─────────────┬─────────────┬─────────────┐   
│ │ Documents   │ Embeddings  │ Queries     │ Avg Time    │   
│ │     5       │     25      │     12      │   150ms     │   
│ └─────────────┴─────────────┴─────────────┴─────────────┘   
├─────────────────────────────────────────────────────────────┤
│ 📋 Recent Activity                                          
│ ┌─────────────────────────────────────────────────────────┐ 
│ │ Last upload: machine_learning_basics.txt (2 min ago)    │ 
│ │ Last search: "What is machine learning?" (1 min ago)    │ 
│ │ Total searches today: 15                                │ 
│ └─────────────────────────────────────────────────────────┘ 
└─────────────────────────────────────────────────────────────┘
```

### Search Results
```
┌─────────────────────────────────────────────────────────────┐
│ Search Results: "What is machine learning?" (3 results)     │
├─────────────────────────────────────────────────────────────┤
│ Score: 95.2%                                                │
│ Machine learning is a subset of artificial intelligence...  │
│ Source: machine_learning_basics.txt (Chunk 1)               │
├─────────────────────────────────────────────────────────────┤
│ Score: 87.1%                                                │
│ Supervised learning involves training a model on labeled... │
│ Source: machine_learning_basics.txt (Chunk 2)               │
├─────────────────────────────────────────────────────────────┤
│ Score: 82.3%                                                │
│ The machine learning workflow typically involves data...    │
│ Source: machine_learning_basics.txt (Chunk 5)               │
└─────────────────────────────────────────────────────────────┘
```

### Query Logs
```
┌─────────────────────────────────────────────────────────────┐
│ Recent Queries (Last 10)                                    │
├─────────────────────────────────────────────────────────────┤
│ Query: "What is machine learning?"                          │
│ Time: 2024-01-15 14:30:25 | Responses: 3 | Avg Score: 88.2% │
├─────────────────────────────────────────────────────────────┤
│ Query: "Python programming basics"                          │
│ Time: 2024-01-15 14:25:10 | Responses: 2 | Avg Score: 91.5% │
├─────────────────────────────────────────────────────────────┤
│ Query: "Database design principles"                         │
│ Time: 2024-01-15 14:20:45 | Responses: 4 | Avg Score: 85.7% │
└─────────────────────────────────────────────────────────────┘
```

## Deployment & Operations

### Setup Instructions

1. **Prerequisites Installation**:
   ```bash
   # Install Docker Desktop
   # Install Python 3.8+
   # Clone repository
   git clone <repository-url>
   cd semantic-search-platform
   ```

2. **Database Setup**:
   ```bash
   docker-compose up -d
   ```

3. **Dependencies Installation**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Data Population**:
   ```bash
   python populate.py
   ```

5. **Server Startup**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| DATABASE_URL | PostgreSQL connection string | postgresql://appuser:apppass@localhost:5432/semsearch | Yes |
| EMBEDDING_MODEL | Sentence-BERT model name | all-MiniLM-L6-v2 | No |
| CHUNK_SIZE | Document chunking size | 500 | No |
| CHUNK_OVERLAP | Overlap between chunks | 50 | No |
| DEFAULT_TOP_K | Default search results | 5 | No |

### Backup & Monitoring

**Backup Strategy**:
- Daily automated PostgreSQL backups using pg_dump
- Vector index recreation scripts for disaster recovery
- Configuration backup for environment variables

**Monitoring**:
- Health check endpoint: `GET /health`
- System statistics endpoint: `GET /search/stats`
- Query performance logging with response times
- Database connection pool monitoring

**Logging**:
- Application logs with structured JSON format
- Query logs with performance metrics
- Error logs with stack traces
- Access logs for API endpoints

## Limitations & Future Improvements

### Current Limitations

1. **File Format Support**: Limited to text files (.txt, .md, .json)
2. **Authentication**: No user authentication or access control
3. **Scalability**: Single-server deployment without load balancing
4. **Language Support**: English-only embeddings and processing
5. **Advanced Features**: No faceted search, filters, or advanced analytics

### Roadmap

1. **Enhanced File Support** (Q2 2024):
   - PDF text extraction with PyPDF2/pdfplumber
   - DOCX processing with python-docx
   - Image OCR with Tesseract
   - Audio transcription with Whisper

2. **User Management** (Q3 2024):
   - JWT-based authentication
   - Role-based access control (Admin, User, Read-only)
   - User-specific document collections
   - API key management

3. **Advanced Search** (Q4 2024):
   - Hybrid search (semantic + keyword)
   - Faceted search with filters
   - Date range filtering
   - Advanced reranking with cross-encoders

4. **Scalability & Performance** (Q1 2025):
   - Horizontal scaling with load balancers
   - Redis caching for query results
   - Database sharding for large datasets
   - CDN integration for static assets

### Technical Debt

1. **Code Quality**: Add comprehensive unit tests for all services
2. **Error Handling**: Implement retry mechanisms for external API calls
3. **Security**: Add input validation and rate limiting
4. **Documentation**: Generate API documentation with OpenAPI 3.0
5. **Monitoring**: Integrate with monitoring tools (Prometheus, Grafana)

---

*This design document serves as the blueprint for the Semantic Search & Q&A Platform, providing a comprehensive guide for development, deployment, and future enhancements.* 

                       ┌───────────────────────────────┐
                       │         DNS/Client            │
                       └─────────────┬─────────────────┘
                                     │
                             ┌───────▼───────┐
                             │ Load Balancer │
                             └───────┬───────┘
              ┌──────────────────────┼──────────────────────┐
     ┌────────▼────────┐   ┌─────────▼────────┐   ┌────────▼────────┐
     │   API Server    │   │   API Server     │   │   API Server    │
     │ (Stateless/REST)│   │ (Stateless/REST) │   │ (Stateless/REST)│
     └────────┬────────┘   └─────────┬────────┘   └────────┬────────┘
              │                      │                     │
       ┌──────▼─────┐         ┌──────▼─────┐        ┌──────▼─────┐
       │  Document  │         │  Semantic  │        │ Embedding  │
       │Processing  │         │   Search   │        │ Generation │
       └──────┬─────┘         └──────┬─────┘        └──────┬─────┘
              │                      │                     │
      ┌───────▼───────┐       ┌──────▼───────┐     ┌──────▼───────┐
      │ CDN/Static    │       │Vector DB     │     │Shard DB Node │
      │ File Hosting  │       │(Sharded)     │     │(pgvector,    │
      │ (S3/Cloud)    │       │[Shard 1..N]  │     │ Milvus, etc) │
      └───────────────┘       └──────────────┘     └──────────────┘

      (Replication & Failover handled in DB/Cache layers)
      ───────────────────────────────────────────────────────
                AWS / Azure / GCP Cloud (vertical line)

   +----------------+        +----------------+         +--------------+        +--------------+
   |   documents    |<-------|   embeddings   |<--------|  responses   |<-------|   queries    |
   +----------------+        +----------------+         +--------------+        +--------------+
   | id (PK)        | 1   *  | id (PK)        |     *   | id (PK)      |   *    | id (PK)      |
   | filename       |--------| document_idFK  |---------| embedding_id |--------| query_id FK  |
   | content        |        | chunk_index    |         | query_id FK  |        | query_text   |
   | uploaded_at    |        | chunk_text     |         | score        |        | timestamp    |
   +----------------+        | vector (384d)  |         | response_txt |        +--------------+
                             +----------------+         +--------------+

    ------------ Optimization ------------
    Index: ivfflat on embeddings.vector
    Params: lists=100, probes=10
    --------------------------------------
