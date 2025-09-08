import os
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from neo4j import GraphDatabase
from app.rag.hybrid_search import hybrid_search
from app.db.sql import SessionLocal

class Router:
    def __init__(self):
        self.embedder = SentenceTransformer(os.getenv("MODEL_NAME"))
        self.neo = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))

    def search(self, query: str, k: int = 8):
        qv = self.embedder.encode([query])[0]
        return hybrid_search(qv, k)

    def indicators_by_type(self, type_: str, limit: int = 100):
        sess = SessionLocal()
        try:
            rows = sess.execute(text("SELECT * FROM indicators WHERE type=:t ORDER BY last_seen DESC LIMIT :l"), {"t": type_, "l": limit}).mappings().all()
            return rows
        finally:
            sess.close()

    def context_for_indicator(self, value_or_norm: str, limit: int = 10):
        sess = SessionLocal()
        try:
            rows = sess.execute(text("""
                SELECT im.*, c.text, d.title
                FROM indicators i
                JOIN indicator_mentions im ON im.indicator_id=i.id
                JOIN chunks c ON c.id=im.chunk_id
                JOIN documents d ON d.id=c.document_id
                WHERE i.normalized=:v OR i.value=:v
                ORDER BY im.score DESC
                LIMIT :l
            """), {"v": value_or_norm, "l": limit}).mappings().all()
            return rows
        finally:
            sess.close()

    def relationships(self, indicator: str, hops: int = 2):
        with self.neo.session() as s:
            q = """
            MATCH (i:Indicator {normalized:$norm})-[r*1..$hops]-(j)
            RETURN i, r, j LIMIT 200
            """
            res = s.run(q, norm=indicator, hops=hops)
            return [r.data() for r in res]

    def network(self, indicator: str):
        with self.neo.session() as s:
            q = """
            MATCH (i:Indicator {normalized:$norm})-[:RELATED_TO*1..2]-(j:Indicator)
            RETURN i, j LIMIT 200
            """
            res = s.run(q, norm=indicator)
            nodes, edges = {}, []
            for rec in res:
                i = rec["i"]; j = rec["j"]
                nodes[i["normalized"]] = {"id": i["normalized"], "type": i["type"]}
                nodes[j["normalized"]] = {"id": j["normalized"], "type": j["type"]}
                edges.append({"source": i["normalized"], "target": j["normalized"], "type": "RELATED_TO"})
            return {"nodes": list(nodes.values()), "edges": edges}
