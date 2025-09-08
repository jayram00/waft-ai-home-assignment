import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def upsert_document(sess, title, external_id=None, source_url=None, language=None):
    r = sess.execute(text("""
        INSERT INTO documents(title, external_id, source_url, language)
        VALUES (:title, :external_id, :source_url, :language)
        ON CONFLICT (external_id) DO UPDATE SET title=EXCLUDED.title
        RETURNING id
    """), dict(title=title, external_id=external_id, source_url=source_url, language=language)).fetchone()
    return r[0]

def insert_chunks(sess, doc_id, chunks, embeddings):
    for idx, (c, emb) in enumerate(zip(chunks, embeddings)):
        sess.execute(text("""
            INSERT INTO chunks(document_id, chunk_index, text, tokens, embedding, meta)
            VALUES (:d, :i, :t, :tok, :e, :m)
            ON CONFLICT (document_id, chunk_index) DO NOTHING
        """), dict(d=doc_id, i=idx, t=c["text"], tok=len(c["text"].split()), e=list(emb), m=json.dumps(c.get("meta", {}))))

def upsert_indicator(sess, ind):
    if ind.get("platform") is None:
        ind["platform"] = ''
    if  not ind.get("platform"):
        ind["platform"] = ''
    r = sess.execute(text("""
        INSERT INTO indicators(type, value, normalized, platform, confidence)
        VALUES (:type, :value, :normalized, :platform, :confidence)
        ON CONFLICT (type, normalized, platform) DO UPDATE SET value=EXCLUDED.value, confidence=EXCLUDED.confidence
        RETURNING id
    """), ind).fetchone()
    return r[0]

def insert_mention(sess, indicator_id, document_id, chunk_id, position, context, score, meta={}):
    sess.execute(text("""
        INSERT INTO indicator_mentions(indicator_id, document_id, chunk_id, position, context, score, meta)
        VALUES (:iid, :did, :cid, :pos, :ctx, :s, :m)
    """), dict(iid=indicator_id, did=document_id, cid=chunk_id, pos=position, ctx=context, s=score, m=meta))
