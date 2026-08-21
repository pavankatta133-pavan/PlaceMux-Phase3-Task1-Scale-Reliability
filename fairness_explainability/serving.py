"""
Task 14
Fairness & Explainability API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fairness_explainability.explainability import (
    load_data,
    explain_decision
)


app = FastAPI(
    title="Fairness & Explainability API",
    version="1.0"
)


class ExplanationRequest(BaseModel):

    candidate_id: str


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "fairness-explainability"
    }


@app.post("/explain")
def explain(request: ExplanationRequest):

    records = load_data()

    candidate = next(
        (
            record
            for record in records
            if record["candidate_id"]
            == request.candidate_id
        ),
        None
    )

    if candidate is None:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return explain_decision(
        candidate
    )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001
    )