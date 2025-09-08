from sqlalchemy import text
from app.db.sql import SessionLocal

def hybrid_search(query_embedding, k=8, keyword: str | None = None):
    sess = SessionLocal()
    try:
        base = """
        SELECT c.id, c.document_id, c.text, 1 - (c.embedding <#> :q) AS score
        FROM chunks c
        ORDER BY c.embedding <#> :q
        LIMIT :k
        """
        sql = text(base)
        rows = sess.execute(sql, {"q": list(query_embedding), "k": k}).mappings().all()
        if keyword:
            rows = [r for r in rows if keyword.lower() in r["text"].lower()]
        return rows
    finally:
        sess.close()
