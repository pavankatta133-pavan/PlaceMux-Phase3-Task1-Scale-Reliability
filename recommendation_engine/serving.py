"""
Phase 3 Task 12
Recommendation Serving Layer

Features:
1. Student recommendation endpoint
2. Personalized recommendation
3. Popularity fallback
4. Latency measurement
5. Health check
"""

import os
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from recommendation_engine.recommender import (
    RecommendationEngine
)

from recommendation_engine.baseline import (
    PopularityBaseline
)


app = FastAPI(
    title="Recommendation Engine",
    version="1.0.0"
)


# =========================================================
# INITIALIZE MODELS
# =========================================================

try:

    recommender = RecommendationEngine()

    baseline = PopularityBaseline()

    ENGINE_READY = True

    ENGINE_ERROR = None

except Exception as exc:

    recommender = None
    baseline = None

    ENGINE_READY = False

    ENGINE_ERROR = str(exc)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get(
    "/health"
)
def health():

    return {
        "status":
            "healthy"
            if ENGINE_READY
            else "degraded",

        "recommendation_engine":
            ENGINE_READY
    }


# =========================================================
# STUDENT RECOMMENDATIONS
# =========================================================

@app.get(
    "/recommendations/{student_id}"
)
def get_recommendations(
    student_id: str,
    k: int = 5
):

    start_time = time.perf_counter()

    # -----------------------------------------
    # Validate K
    # -----------------------------------------

    if k < 1:
        k = 1

    if k > 20:
        k = 20

    # -----------------------------------------
    # Personalized recommendation
    # -----------------------------------------

    if ENGINE_READY:

        try:

            recommendations = (
                recommender.recommend_jobs(
                    student_id,
                    k=k,
                    exclude_interacted=True
                )
            )

            latency_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            return {

                "student_id":
                    student_id,

                "model":
                    "personalized",

                "recommendations":
                    recommendations,

                "count":
                    len(recommendations),

                "latency_ms":
                    round(
                        latency_ms,
                        3
                    ),

                "fallback":
                    False
            }

        except Exception as exc:

            engine_error = str(exc)

    else:

        engine_error = ENGINE_ERROR

    # -----------------------------------------
    # FALLBACK
    # -----------------------------------------

    fallback_start = time.perf_counter()

    try:

        recommendations = (
            baseline.recommend_jobs(
                k=k
            )
        )

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        return {

            "student_id":
                student_id,

            "model":
                "popularity_baseline",

            "recommendations":
                recommendations,

            "count":
                len(recommendations),

            "latency_ms":
                round(
                    latency_ms,
                    3
                ),

            "fallback":
                True,

            "fallback_reason":
                engine_error,

            "fallback_latency_ms":
                round(
                    (
                        time.perf_counter()
                        - fallback_start
                    ) * 1000,
                    3
                )
        }

    except Exception as exc:

        return JSONResponse(

            status_code=500,

            content={

                "student_id":
                    student_id,

                "model":
                    None,

                "recommendations":
                    [],

                "count":
                    0,

                "fallback":
                    True,

                "error":
                    str(exc)
            }
        )


# =========================================================
# SIMPLE TEST ENDPOINT
# =========================================================

@app.get(
    "/"
)
def root():

    return {

        "service":
            "Recommendation Engine",

        "version":
            "1.0.0",

        "status":
            "running",

        "endpoints":
            [
                "/health",
                "/recommendations/{student_id}"
            ]
    }


# =========================================================
# LOCAL RUN
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )