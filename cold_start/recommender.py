"""
Phase 3 Task 7
Cold-Start Recommendation Strategy
"""

import os


MODEL_VERSION = "cold_start_ranker_v1"


def normalize_skills(skills):
    """Normalize skill names for reliable matching."""
    if not isinstance(skills, list):
        return set()

    return {
        str(skill).strip().lower()
        for skill in skills
        if str(skill).strip()
    }


def calculate_relevance(candidate_skills, job_skills):
    """
    Calculate percentage of job skills matched
    by the candidate.
    """

    candidate_set = normalize_skills(candidate_skills)
    job_set = normalize_skills(job_skills)

    if not job_set:
        return 0.0, []

    matched = sorted(
        candidate_set.intersection(job_set)
    )

    score = (
        len(matched) / len(job_set)
    ) * 100

    return round(score, 2), matched


def recommend_jobs(
    candidate_skills,
    jobs,
    preferred_roles=None,
    top_k=5
):
    """
    Generate recommendations for a cold-start candidate.

    No historical user activity is required.
    """

    if os.getenv(
        "TASK7_FORCE_COLD_START_FAILURE",
        "false"
    ).lower() == "true":

        raise RuntimeError(
            "Synthetic cold-start model failure."
        )

    preferred_roles = {
        str(role).strip().lower()
        for role in (preferred_roles or [])
        if str(role).strip()
    }

    recommendations = []

    for job in jobs:

        job_skills = job.get(
            "skills",
            []
        )

        score, matched_skills = calculate_relevance(
            candidate_skills,
            job_skills
        )

        title = str(
            job.get("title", "")
        ).strip()

        role_bonus = 0

        if (
            title.lower()
            in preferred_roles
        ):
            role_bonus = 10

        final_score = min(
            100,
            round(score + role_bonus, 2)
        )

        recommendations.append({

            "job_id":
                job.get("job_id"),

            "title":
                title,

            "score":
                final_score,

            "matched_skills":
                matched_skills,

            "reason":
                (
                    f"Matches {len(matched_skills)} "
                    f"required job skills."
                ),

            "model_version":
                MODEL_VERSION
        })

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations[:top_k]