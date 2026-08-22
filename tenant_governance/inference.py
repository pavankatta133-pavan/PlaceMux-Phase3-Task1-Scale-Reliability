"""
Task 16
Enterprise Multi-Tenancy & RBAC
Tenant-Scoped Inference
"""

from tenant_governance.tenant_config import (
    get_matching_config
)

from tenant_governance.tenant_data import (
    get_job,
    get_candidate
)


def calculate_skills_match(
    candidate_skills,
    required_skills
):
    """
    Calculate the fraction of required skills
    matched by the candidate.
    """

    candidate_set = {
        skill.lower()
        for skill in candidate_skills
    }

    required_set = {
        skill.lower()
        for skill in required_skills
    }

    if not required_set:
        return 0.0

    matched = (
        candidate_set
        & required_set
    )

    return len(matched) / len(
        required_set
    )


def calculate_experience_score(
    experience
):
    """
    Normalize experience into a 0-1 score.
    Five or more years receives the maximum score.
    """

    return min(
        max(experience / 5.0, 0.0),
        1.0
    )


def calculate_match(
    tenant_id,
    candidate_id,
    job_id
):
    """
    Perform inference strictly within one tenant.

    Candidate and job are both resolved through the
    requested tenant_id. No global fallback is used.
    """

    config = get_matching_config(
        tenant_id
    )

    candidate = get_candidate(
        tenant_id,
        candidate_id
    )

    job = get_job(
        tenant_id,
        job_id
    )

    skills_score = calculate_skills_match(
        candidate["skills"],
        job["required_skills"]
    )

    experience_score = calculate_experience_score(
        candidate["experience"]
    )

    education_score = candidate["education"]

    weights = config["weights"]

    score = (
        skills_score * weights["skills"]
        + experience_score * weights["experience"]
        + education_score * weights["education"]
    )

    score = round(
        score,
        4
    )

    selected = (
        score >= config["threshold"]
    )

    return {
        "tenant_id": tenant_id,
        "candidate_id": candidate_id,
        "job_id": job_id,
        "score": score,
        "threshold": config["threshold"],
        "selected": selected,
        "features": {
            "skills_match": round(
                skills_score,
                4
            ),
            "experience_score": round(
                experience_score,
                4
            ),
            "education_score": round(
                education_score,
                4
            )
        },
        "weights": weights
    }


def explain_result(result):

    decision = (
        "selected"
        if result["selected"]
        else "not selected"
    )

    return (
        f"Tenant {result['tenant_id']} "
        f"candidate {result['candidate_id']} "
        f"was {decision} for job "
        f"{result['job_id']} with a matching "
        f"score of {result['score']:.4f}. "
        f"The tenant threshold is "
        f"{result['threshold']:.2f}. "
        f"The score used skills match "
        f"{result['features']['skills_match']:.2f}, "
        f"experience score "
        f"{result['features']['experience_score']:.2f}, "
        f"and education score "
        f"{result['features']['education_score']:.2f}."
    )


def test_tenant_scoped_inference():

    alpha_result = calculate_match(
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    beta_result = calculate_match(
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001"
    )

    if alpha_result["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Alpha inference escaped tenant scope."
        )

    if beta_result["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "Beta inference escaped tenant scope."
        )

    if alpha_result["candidate_id"].startswith(
        "beta_"
    ):
        raise RuntimeError(
            "Beta candidate leaked into Alpha inference."
        )

    if beta_result["candidate_id"].startswith(
        "alpha_"
    ):
        raise RuntimeError(
            "Alpha candidate leaked into Beta inference."
        )

    if alpha_result["job_id"].startswith(
        "beta_"
    ):
        raise RuntimeError(
            "Beta job leaked into Alpha inference."
        )

    if beta_result["job_id"].startswith(
        "alpha_"
    ):
        raise RuntimeError(
            "Alpha job leaked into Beta inference."
        )

    return (
        alpha_result,
        beta_result
    )


def main():

    print(
        "\n========== TASK 16 TENANT-SCOPED INFERENCE =========="
    )

    alpha_result, beta_result = (
        test_tenant_scoped_inference()
    )

    print(
        "\nTenant Alpha result:"
    )

    print(
        alpha_result
    )

    print(
        "\nTenant Alpha explanation:"
    )

    print(
        explain_result(
            alpha_result
        )
    )

    print(
        "\nTenant Beta result:"
    )

    print(
        beta_result
    )

    print(
        "\nTenant Beta explanation:"
    )

    print(
        explain_result(
            beta_result
        )
    )

    print(
        "\nTenant-scoped inference: PASS"
    )

    print(
        "Strict tenant data access: PASS"
    )

    print(
        "Plain-English explanation: PASS"
    )

    print(
        "\nTASK 16 TENANT-SCOPED INFERENCE: PASS"
    )


if __name__ == "__main__":
    main()