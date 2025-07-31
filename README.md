# End-to-End Semantic Search & Q&A Platform

A complete semantic search and question-answering platform built with FastAPI, PostgreSQL with pgvector, and Sentence-BERT embeddings.

## Features

- **Document Upload & Processing**: Upload text documents and automatically generate embeddings
- **Semantic Search**: Find relevant document chunks using vector similarity search
- **Question Answering**: Ask natural language questions and get relevant answers with source metadata
- **Query Logging**: Track all queries and response times for monitoring
- **RESTful API**: Complete CRUD operations with comprehensive documentation
- **Vector Database**: PostgreSQL with pgvector extension for efficient similarity search

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │  Sentence-BERT  │
│                 │    │   with pgvector │    │   Embeddings    │
│  - Document API │◄──►│  - Documents    │    │                 │
│  - Search API   │    │  - Embeddings   │    │  - Text chunks  │
│  - Admin API    │    │  - Queries      │    │  - Query text   │
│                 │    │  - Responses    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd semantic-search-platform
```

### 2. Start Database

```bash
docker-compose up -d
```

This starts PostgreSQL with pgvector extension on port 5432.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Populate Sample Data

```bash
python populate.py
```

This adds sample documents about machine learning, Python programming, database design, API design, and cloud computing.

### 5. Start the API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Documents

- `POST /documents/upload` - Upload and process a document
- `GET /documents/` - List all documents
- `GET /documents/{id}` - Get specific document
- `DELETE /documents/{id}` - Delete document and embeddings

### Search

- `POST /search/query` - Perform semantic search
- `GET /search/logs` - Get query logs with performance metrics
- `GET /search/stats` - Get system statistics

## Usage Examples

### Upload a Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.txt"
```

### Search Documents

```bash
curl -X POST "http://localhost:8000/search/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 3
  }'
```

### Get Query Logs

```bash
curl -X GET "http://localhost:8000/search/logs?limit=10"
```

## Database Schema

### Tables

1. **documents** - Stores uploaded documents
   - `id` (PK), `filename`, `content`, `uploaded_at`

2. **embeddings** - Stores document chunks and their vectors
   - `id` (PK), `document_id` (FK), `chunk_index`, `chunk_text`, `vector`

3. **queries** - Logs all search queries
   - `id` (PK), `query_text`, `timestamp`

4. **responses** - Stores search results and scores
   - `id` (PK), `query_id` (FK), `embedding_id` (FK), `score`, `response_text`

### Indexes

- Vector similarity index on `embeddings.vector` using IVFFlat
- Performance indexes on `responses.score` and `queries.timestamp`

## Configuration

Copy `env.example` to `.env` and modify as needed:

```bash
cp env.example .env
```

Key configuration options:

- `DATABASE_URL` - PostgreSQL connection string
- `EMBEDDING_MODEL` - Sentence-BERT model name
- `CHUNK_SIZE` - Document chunking size
- `DEFAULT_TOP_K` - Default number of search results

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Tests cover:
- API endpoint functionality
- Document upload and retrieval
- Search functionality
- Error handling
- Database operations

## Development

### Project Structure

```
semantic-search-platform/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── db.py            # Database connection
│   ├── schemas.py       # Pydantic models
│   ├── services.py      # Business logic
│   └── routers/
│       ├── documents.py # Document endpoints
│       └── search.py    # Search endpoints
├── tests/
│   └── test_api.py      # API tests
├── ddl.sql              # Database schema
├── populate.py          # Sample data
├── docker-compose.yml   # Database setup
├── requirements.txt     # Dependencies
└── README.md           # This file
```

### Adding New Features

1. **New Endpoints**: Add to appropriate router in `app/routers/`
2. **New Models**: Add Pydantic schemas in `app/schemas.py`
3. **Business Logic**: Add services in `app/services.py`
4. **Database Changes**: Update `ddl.sql` and run migrations

## Performance Considerations

- **Vector Index**: Uses IVFFlat index for fast similarity search
- **Chunking**: Documents are split into overlapping chunks for better search granularity
- **Connection Pooling**: AsyncPG connection pool for efficient database connections
- **Batch Processing**: Embeddings generated in batches for efficiency

## Monitoring

- Query logs track all searches with timestamps
- System stats provide overview of documents, embeddings, and queries
- Response times are measured and logged
- Health check endpoint for service monitoring

## Production Deployment

1. **Environment Variables**: Set production database URL and secrets
2. **Security**: Configure CORS origins, add authentication
3. **Scaling**: Use multiple workers with Gunicorn
4. **Monitoring**: Add logging, metrics, and alerting
5. **Backup**: Regular database backups

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running and accessible
2. **Vector Extension**: Verify pgvector extension is installed
3. **Model Download**: First run may download Sentence-BERT model
4. **Memory**: Large documents may require more memory for processing

### Logs

Check application logs for detailed error information:

```bash
uvicorn app.main:app --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 