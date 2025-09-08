import argparse, os
import json
from pathlib import Path
from sqlalchemy import text
from app.ingest.pdf_processor import extract_text_blocks
from app.ingest.chunker import chunk_blocks
from app.ingest.embedder import Embedder
from app.extract.indicators import extract_indicators
from app.db.sql import SessionLocal, upsert_document, insert_chunks, upsert_indicator, insert_mention
from app.db.sql import engine

MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/distiluse-base-multilingual-cased-v2")

def ensure_schema():
    with engine.begin() as conn:
        ddl = Path("app/db/ddl.sql").read_text()
        conn.execute(text(ddl))

def process_pdf(pdf_path: Path):
    sess = SessionLocal()
    try:
        title = pdf_path.stem
        doc_id = upsert_document(sess, title=title, external_id=title)
        blocks = extract_text_blocks(pdf_path)
        chunks = chunk_blocks(blocks)
        embedder = Embedder(MODEL_NAME)
        embs = embedder.encode([c["text"] for c in chunks])
        insert_chunks(sess, doc_id, chunks, embs)
        sess.commit()

        rows = sess.execute(text("SELECT id, text FROM chunks WHERE document_id=:d ORDER BY chunk_index"), {"d": doc_id}).mappings().all()
        for row in rows:
            inds = extract_indicators(row["text"])  # list of dicts
            for ind in inds:
                if ind.get('meta') is None:
                    meta_json = "{}"
                elif isinstance(ind.get('meta'), dict):
                    meta_json = json.dumps(ind.get('meta'))
                elif isinstance(ind.get('meta'), str):
                    # already JSON text, use as-is
                    meta_json = ind.get('meta')
                else:
                    # fallback: wrap unknown type
                    meta_json = json.dumps(ind.get('meta'))
                ind_id = upsert_indicator(sess, ind)
                snippet = row["text"][:500]
                insert_mention(sess, ind_id, doc_id, row["id"], 0, snippet, ind.get("confidence", 0.8),meta_json)
        sess.commit()
        print(f"Processed {pdf_path} -> doc_id={doc_id}, chunks={len(chunks)}")
    finally:
        sess.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ingest', type=str, required=True)
    args = parser.parse_args()
    ensure_schema()
    input_dir = Path(args.ingest)
    pdfs = list(input_dir.glob('*.pdf'))
    for p in pdfs:
        process_pdf(p)

if __name__ == '__main__':
    main()
