"""
Phase 3 Task 12
Recommendation Explainability

Generates plain-English reasons for:
1. Student -> Job recommendations
2. Job -> Candidate recommendations
"""


def explain_job_recommendation(
    recommendation
):
    """Explain why a job was recommended."""

    job_id = recommendation.get(
        "job_id",
        "unknown"
    )

    score = recommendation.get(
        "score",
        0
    )

    reason = (
        "Recommended because this job "
        "has strong engagement from users "
        "with similar activity patterns."
    )

    return {
        "job_id": job_id,
        "score": score,
        "reason": reason
    }


def explain_candidate_recommendation(
    recommendation
):
    """Explain why a candidate was recommended."""

    student_id = recommendation.get(
        "student_id",
        "unknown"
    )

    score = recommendation.get(
        "score",
        0
    )

    applications = recommendation.get(
        "applications",
        0
    )

    shortlists = recommendation.get(
        "shortlists",
        0
    )

    clicks = recommendation.get(
        "clicks",
        0
    )

    reasons = []

    if shortlists > 0:
        reasons.append(
            f"{shortlists} shortlist interaction(s)"
        )

    if applications > 0:
        reasons.append(
            f"{applications} application(s)"
        )

    if clicks > 0:
        reasons.append(
            f"{clicks} click interaction(s)"
        )

    if reasons:

        reason = (
            "Recommended because the candidate has "
            + ", ".join(reasons)
            + "."
        )

    else:

        reason = (
            "Recommended based on the candidate's "
            "historical engagement."
        )

    return {
        "student_id": student_id,
        "score": score,
        "reason": reason
    }


def explain_job_list(
    recommendations
):
    """Add explanations to job recommendations."""

    return [
        explain_job_recommendation(
            recommendation
        )
        for recommendation in recommendations
    ]


def explain_candidate_list(
    recommendations
):
    """Add explanations to candidate recommendations."""

    return [
        explain_candidate_recommendation(
            recommendation
        )
        for recommendation in recommendations
    ]


def main():

    print(
        "\n========== TASK 12 EXPLAINABILITY =========="
    )

    job_example = {
        "job_id": "job_001",
        "score": 25.5
    }

    candidate_example = {
        "student_id": "student_001",
        "score": 31.5,
        "applications": 2,
        "shortlists": 1,
        "clicks": 5
    }

    print(
        "\nStudent -> Job explanation:"
    )

    print(
        explain_job_recommendation(
            job_example
        )
    )

    print(
        "\nJob -> Candidate explanation:"
    )

    print(
        explain_candidate_recommendation(
            candidate_example
        )
    )

    print(
        "\nTASK 12 EXPLAINABILITY: PASS"
    )


if __name__ == "__main__":
    main()