from fastapi import FastAPI
from app.rag.langgraph_router import Router
from app.api.schemas import SearchRequest, NetworkResponse

app = FastAPI(title="Threat Intel RAG API")
router = Router()

@app.post('/search')
async def search(req: SearchRequest):
    hits = router.search(req.query, req.k)
    return {"results": hits}

@app.get('/indicators/{type}')
async def indicators(type: str, limit: int = 100):
    rows = router.indicators_by_type(type, limit)
    return {"items": rows}

@app.get('/context/{indicator}')
async def context(indicator: str, limit: int = 10):
    rows = router.context_for_indicator(indicator, limit)
    return {"contexts": rows}

@app.get('/relationships/{indicator}')
async def rel(indicator: str, hops: int = 2):
    rels = router.relationships(indicator, hops)
    return {"graph_raw": rels}

@app.get('/network/{indicator}', response_model=NetworkResponse)
async def network(indicator: str):
    return router.network(indicator)
