-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  content TEXT NOT NULL,
  uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create embeddings table
CREATE TABLE embeddings (
  id SERIAL PRIMARY KEY,
  document_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INT NOT NULL,
  chunk_text TEXT NOT NULL,
  vector vector(384),
  UNIQUE(document_id, chunk_index)
);

-- Create index for vector similarity search
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (vector vector_l2_ops) WITH (lists = 100);

-- Create queries table
CREATE TABLE queries (
  id SERIAL PRIMARY KEY,
  query_text TEXT NOT NULL,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create responses table
CREATE TABLE responses (
  id SERIAL PRIMARY KEY,
  query_id INT NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
  embedding_id INT NOT NULL REFERENCES embeddings(id),
  score REAL NOT NULL,
  response_text TEXT NOT NULL
);

-- Create index for response scoring
CREATE INDEX idx_responses_score ON responses(score DESC);

-- Create index for query timestamps
CREATE INDEX idx_queries_timestamp ON queries(timestamp DESC); 