"""
Phase 3 Task 7
Never-Empty Recommendation Fallback
"""


def fallback_recommendations(
    jobs,
    top_k=5
):
    """
    Return usable recommendations even when
    the intelligent recommender is unavailable.
    """

    if not isinstance(jobs, list):
        jobs = []

    active_jobs = [
        job
        for job in jobs
        if job.get("active", True)
    ]

    # First fallback: active jobs
    recommendations = active_jobs[:top_k]

    # Second fallback: any available jobs
    if not recommendations:
        recommendations = jobs[:top_k]

    return [
        {
            "job_id":
                job.get("job_id"),

            "title":
                job.get(
                    "title",
                    "Available Job"
                ),

            "score":
                0.0,

            "matched_skills":
                [],

            "reason":
                "Recommended using the fallback job pool.",

            "model_version":
                "fallback_v1"
        }
        for job in recommendations
    ]