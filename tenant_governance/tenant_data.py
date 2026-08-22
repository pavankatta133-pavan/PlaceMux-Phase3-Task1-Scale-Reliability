"""
Task 16
Enterprise Multi-Tenancy & RBAC
Tenant-Scoped Data Isolation
"""

from copy import deepcopy


TENANT_DATA = {
    "tenant_alpha": {
        "tenant_id": "tenant_alpha",
        "jobs": [
            {
                "job_id": "alpha_job_001",
                "title": "Python Backend Developer",
                "required_skills": [
                    "Python",
                    "FastAPI",
                    "SQL"
                ]
            },
            {
                "job_id": "alpha_job_002",
                "title": "Machine Learning Engineer",
                "required_skills": [
                    "Python",
                    "Machine Learning",
                    "TensorFlow"
                ]
            }
        ],
        "candidates": [
            {
                "candidate_id": "alpha_candidate_001",
                "skills": [
                    "Python",
                    "FastAPI",
                    "SQL"
                ],
                "experience": 5,
                "education": 0.85
            }
        ]
    },

    "tenant_beta": {
        "tenant_id": "tenant_beta",
        "jobs": [
            {
                "job_id": "beta_job_001",
                "title": "Java Backend Developer",
                "required_skills": [
                    "Java",
                    "Spring",
                    "SQL"
                ]
            },
            {
                "job_id": "beta_job_002",
                "title": "Data Scientist",
                "required_skills": [
                    "Python",
                    "Pandas",
                    "Statistics"
                ]
            }
        ],
        "candidates": [
            {
                "candidate_id": "beta_candidate_001",
                "skills": [
                    "Java",
                    "Spring",
                    "SQL"
                ],
                "experience": 4,
                "education": 0.80
            }
        ]
    }
}


def validate_tenant_id(tenant_id):
    """
    Reject unknown tenants.

    An unknown tenant must never receive another
    tenant's data as a fallback.
    """

    if tenant_id not in TENANT_DATA:
        raise ValueError(
            f"Unknown tenant: {tenant_id}"
        )


def get_tenant_data(tenant_id):
    """
    Return only the data belonging to the requested tenant.

    deepcopy prevents callers from modifying the
    underlying tenant store directly.
    """

    validate_tenant_id(
        tenant_id
    )

    return deepcopy(
        TENANT_DATA[tenant_id]
    )


def get_jobs(tenant_id):

    data = get_tenant_data(
        tenant_id
    )

    return data["jobs"]


def get_candidates(tenant_id):

    data = get_tenant_data(
        tenant_id
    )

    return data["candidates"]


def get_job(tenant_id, job_id):

    jobs = get_jobs(
        tenant_id
    )

    for job in jobs:

        if job["job_id"] == job_id:
            return job

    raise ValueError(
        f"Job {job_id} does not belong to "
        f"tenant {tenant_id}."
    )


def get_candidate(
    tenant_id,
    candidate_id
):

    candidates = get_candidates(
        tenant_id
    )

    for candidate in candidates:

        if candidate["candidate_id"] == candidate_id:
            return candidate

    raise ValueError(
        f"Candidate {candidate_id} does not belong to "
        f"tenant {tenant_id}."
    )


def assert_no_cross_tenant_data_leak():

    alpha = get_tenant_data(
        "tenant_alpha"
    )

    beta = get_tenant_data(
        "tenant_beta"
    )

    alpha_text = str(alpha)
    beta_text = str(beta)

    for job in beta["jobs"]:

        if job["job_id"] in alpha_text:
            raise RuntimeError(
                "Tenant B job leaked into Tenant A."
            )

    for job in alpha["jobs"]:

        if job["job_id"] in beta_text:
            raise RuntimeError(
                "Tenant A job leaked into Tenant B."
            )

    for candidate in beta["candidates"]:

        if candidate["candidate_id"] in alpha_text:
            raise RuntimeError(
                "Tenant B candidate leaked into Tenant A."
            )

    for candidate in alpha["candidates"]:

        if candidate["candidate_id"] in beta_text:
            raise RuntimeError(
                "Tenant A candidate leaked into Tenant B."
            )


def test_unknown_tenant_is_rejected():

    try:

        get_tenant_data(
            "tenant_unknown"
        )

    except ValueError:

        return

    raise RuntimeError(
        "Unknown tenant was not rejected."
    )


def main():

    print(
        "\n========== TASK 16 TENANT DATA ISOLATION =========="
    )

    alpha = get_tenant_data(
        "tenant_alpha"
    )

    beta = get_tenant_data(
        "tenant_beta"
    )

    print(
        "Tenant Alpha jobs:",
        len(alpha["jobs"])
    )

    print(
        "Tenant Alpha candidates:",
        len(alpha["candidates"])
    )

    print(
        "Tenant Beta jobs:",
        len(beta["jobs"])
    )

    print(
        "Tenant Beta candidates:",
        len(beta["candidates"])
    )

    # Verify tenant IDs are correct.
    if alpha["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Tenant Alpha data is incorrectly scoped."
        )

    if beta["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "Tenant Beta data is incorrectly scoped."
        )

    assert_no_cross_tenant_data_leak()

    print(
        "\nCross-tenant isolation: PASS"
    )

    test_unknown_tenant_is_rejected()

    print(
        "Unknown tenant rejection: PASS"
    )

    # Verify returned data is isolated from the
    # underlying store.
    alpha_copy = get_tenant_data(
        "tenant_alpha"
    )

    alpha_copy["jobs"].clear()

    if len(
        get_jobs("tenant_alpha")
    ) == 0:

        raise RuntimeError(
            "Tenant data was modified through a returned object."
        )

    print(
        "Data mutation isolation: PASS"
    )

    print(
        "\nTASK 16 TENANT DATA ISOLATION: PASS"
    )


if __name__ == "__main__":
    main()