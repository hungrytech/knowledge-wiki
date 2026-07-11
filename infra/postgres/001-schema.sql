CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  tags TEXT[] NOT NULL DEFAULT '{}',
  resource TEXT,
  timestamp TIMESTAMPTZ,
  body TEXT NOT NULL,
  embedding vector(384),
  indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS documents_tags_idx ON documents USING GIN (tags);
CREATE INDEX IF NOT EXISTS documents_fts_idx ON documents USING GIN (to_tsvector('simple', title || ' ' || coalesce(description, '') || ' ' || body));
CREATE INDEX IF NOT EXISTS documents_embedding_hnsw_idx ON documents USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS links (
  source_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  target_id TEXT NOT NULL,
  PRIMARY KEY (source_id, target_id)
);
CREATE INDEX IF NOT EXISTS links_source_idx ON links (source_id);
