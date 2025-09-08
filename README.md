# Threat Intel RAG (Hybrid Graph + SQL)

## Quickstart
1. Place PDFs in `data/input/`.
2. `make up`
3. `make ingest`
4. Swagger: http://localhost:8000/docs

## Design
- Multilingual embeddings: `distiluse-base-multilingual-cased-v2`
- PDF extraction: PyMuPDF blocks + heuristics
- Indicators: regex + libraries (phones, domains)
- Storage: Postgres (pgvector) + Neo4j (relationships)
- API: FastAPI with hybrid search and graph traversal

See inline code for details.
