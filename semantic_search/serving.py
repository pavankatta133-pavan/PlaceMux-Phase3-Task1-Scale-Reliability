"""
Phase 3 Task 13
Semantic Search - FastAPI Serving
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from semantic_search.hybrid_search import HybridSearch


app = FastAPI(
    title="Semantic Search API",
    version="1.0.0"
)

search_engine = HybridSearch()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "semantic-search"
    }


@app.post("/search")
def search(request: SearchRequest):

    if not request.query.strip():

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    if request.top_k < 1:

        raise HTTPException(
            status_code=400,
            detail="top_k must be at least 1."
        )

    results = search_engine.search(
        request.query,
        top_k=request.top_k
    )

    return {
        "query": request.query,
        "count": len(results),
        "results": results
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )