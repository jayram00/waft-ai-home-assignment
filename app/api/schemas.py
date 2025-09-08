from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    k: int = 8
    keyword: Optional[str] = None

class IndicatorTypeResponse(BaseModel):
    id: int
    type: str
    value: str
    normalized: str
    platform: str | None
    confidence: float

class NetworkResponse(BaseModel):
    nodes: list
    edges: list
