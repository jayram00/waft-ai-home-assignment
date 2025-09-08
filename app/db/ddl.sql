CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id SERIAL PRIMARY KEY,
  external_id TEXT UNIQUE,
  title TEXT,
  source_url TEXT,
  language TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
  id BIGSERIAL PRIMARY KEY,
  document_id INT REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INT,
  text TEXT,
  tokens INT,
  embedding VECTOR(512),
  meta JSONB,
  UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_l2_ops) WITH (lists=100);

CREATE TABLE IF NOT EXISTS indicators (
  id BIGSERIAL PRIMARY KEY,
  type TEXT CHECK (type IN ('domain','url','ip','phone','email','social','ga','adsense')),
  value TEXT,
  normalized TEXT,
  platform TEXT DEFAULT '' NOT NULL,
  confidence REAL,
  first_seen TIMESTAMP DEFAULT now(),
  last_seen TIMESTAMP DEFAULT now(),
UNIQUE(type, normalized, platform)
);


CREATE TABLE IF NOT EXISTS indicator_mentions (
  id BIGSERIAL PRIMARY KEY,
  indicator_id BIGINT REFERENCES indicators(id) ON DELETE CASCADE,
  document_id INT REFERENCES documents(id) ON DELETE CASCADE,
  chunk_id BIGINT REFERENCES chunks(id) ON DELETE CASCADE,
  position INT,
  context TEXT,
  score REAL,
  meta JSONB,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS relationships (
  id BIGSERIAL PRIMARY KEY,
  source_indicator BIGINT REFERENCES indicators(id) ON DELETE CASCADE,
  target_indicator BIGINT REFERENCES indicators(id) ON DELETE CASCADE,
  relation TEXT,
  weight REAL,
  dedup_key TEXT UNIQUE,
  meta JSONB
);

CREATE TABLE IF NOT EXISTS campaigns (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE,
  description TEXT
);

CREATE TABLE IF NOT EXISTS doc_campaign (
  document_id INT REFERENCES documents(id) ON DELETE CASCADE,
  campaign_id INT REFERENCES campaigns(id) ON DELETE CASCADE,
  PRIMARY KEY (document_id, campaign_id)
);
