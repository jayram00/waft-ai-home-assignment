from neo4j import GraphDatabase

class GraphSync:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def upsert_indicator(self, ind: dict):
        q = '''
        MERGE (i:Indicator {normalized: $normalized, type: $type, platform: coalesce($platform, '')})
        ON CREATE SET i.value=$value, i.confidence=$confidence, i.first_seen=timestamp()
        ON MATCH  SET i.last_seen=timestamp(), i.value=$value, i.confidence=$confidence
        RETURN id(i) as id
        '''
        with self.driver.session() as s:
            s.run(q, **ind)

    def link_mention(self, ind_norm: str, doc_id: int, chunk_id: int):
        q = '''
        MERGE (i:Indicator {normalized: $ind_norm})
        MERGE (d:Document {id: $doc_id})
        MERGE (c:Chunk {id: $chunk_id})-[:OF_DOC]->(d)
        MERGE (i)-[:MENTIONED_IN {chunk_id:$chunk_id}]->(c)
        '''
        with self.driver.session() as s:
            s.run(q, ind_norm=ind_norm, doc_id=doc_id, chunk_id=chunk_id)

    def relate(self, a_norm: str, b_norm: str, rel: str, weight: float = 1.0):
        q = '''
        MATCH (a:Indicator {normalized:$a}), (b:Indicator {normalized:$b})
        MERGE (a)-[r:RELATED_TO {type:$rel}]->(b)
        ON CREATE SET r.weight=$weight, r.first_seen=timestamp()
        ON MATCH  SET r.weight=$weight, r.last_seen=timestamp()
        '''
        with self.driver.session() as s:
            s.run(q, a=a_norm, b=b_norm, rel=rel, weight=weight)
