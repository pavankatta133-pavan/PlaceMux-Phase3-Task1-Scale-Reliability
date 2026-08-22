"""
Task 16
Cross-Tenant Isolation Test

Proves that one tenant cannot access another tenant's
candidate, job, configuration, or inference data.
"""

from tenant_governance.tenant_config import (
    get_tenant_config,
    get_matching_config
)

from tenant_governance.tenant_data import (
    get_tenant_data,
    get_job,
    get_candidate
)

from tenant_governance.inference import (
    calculate_match
)


def expect_failure(description, function):
    """
    Execute an operation that should be rejected.
    """

    try:

        function()

    except (ValueError, KeyError):

        print(
            f"{description}: PASS"
        )

        return

    raise RuntimeError(
        f"{description}: FAILED — "
        "cross-tenant access was allowed."
    )


def test_configuration_isolation():

    alpha_config = get_matching_config(
        "tenant_alpha"
    )

    beta_config = get_matching_config(
        "tenant_beta"
    )

    if alpha_config == beta_config:

        raise RuntimeError(
            "Tenant configurations are unexpectedly identical."
        )

    print(
        "Per-tenant configuration isolation: PASS"
    )


def test_data_isolation():

    alpha = get_tenant_data(
        "tenant_alpha"
    )

    beta = get_tenant_data(
        "tenant_beta"
    )

    alpha_ids = {
        item["job_id"]
        for item in alpha["jobs"]
    }

    beta_ids = {
        item["job_id"]
        for item in beta["jobs"]
    }

    if alpha_ids & beta_ids:

        raise RuntimeError(
            "Job IDs overlap across tenants."
        )

    alpha_candidate_ids = {
        item["candidate_id"]
        for item in alpha["candidates"]
    }

    beta_candidate_ids = {
        item["candidate_id"]
        for item in beta["candidates"]
    }

    if alpha_candidate_ids & beta_candidate_ids:

        raise RuntimeError(
            "Candidate IDs overlap across tenants."
        )

    print(
        "Tenant data isolation: PASS"
    )


def test_cross_tenant_job_access():

    expect_failure(
        "Alpha cannot access Beta job",
        lambda: get_job(
            "tenant_alpha",
            "beta_job_001"
        )
    )

    expect_failure(
        "Beta cannot access Alpha job",
        lambda: get_job(
            "tenant_beta",
            "alpha_job_001"
        )
    )


def test_cross_tenant_candidate_access():

    expect_failure(
        "Alpha cannot access Beta candidate",
        lambda: get_candidate(
            "tenant_alpha",
            "beta_candidate_001"
        )
    )

    expect_failure(
        "Beta cannot access Alpha candidate",
        lambda: get_candidate(
            "tenant_beta",
            "alpha_candidate_001"
        )
    )


def test_cross_tenant_inference():

    expect_failure(
        "Alpha cannot infer using Beta data",
        lambda: calculate_match(
            tenant_id="tenant_alpha",
            candidate_id="beta_candidate_001",
            job_id="alpha_job_001"
        )
    )

    expect_failure(
        "Beta cannot infer using Alpha data",
        lambda: calculate_match(
            tenant_id="tenant_beta",
            candidate_id="alpha_candidate_001",
            job_id="beta_job_001"
        )
    )


def test_unknown_tenant():

    expect_failure(
        "Unknown tenant rejected",
        lambda: get_tenant_config(
            "tenant_unknown"
        )
    )


def test_result_tenant_identity():

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
            "Alpha inference returned incorrect tenant identity."
        )

    if beta_result["tenant_id"] != "tenant_beta":

        raise RuntimeError(
            "Beta inference returned incorrect tenant identity."
        )

    print(
        "Inference tenant identity: PASS"
    )


def main():

    print(
        "\n========== TASK 16 CROSS-TENANT ISOLATION =========="
    )

    test_configuration_isolation()

    test_data_isolation()

    test_cross_tenant_job_access()

    test_cross_tenant_candidate_access()

    test_cross_tenant_inference()

    test_unknown_tenant()

    test_result_tenant_identity()

    print(
        "\nNo tenant data leakage: PASS"
    )

    print(
        "Cross-tenant access rejection: PASS"
    )

    print(
        "Cross-tenant inference rejection: PASS"
    )

    print(
        "Tenant configuration isolation: PASS"
    )

    print(
        "\nTASK 16 ISOLATION TEST: PASS"
    )


if __name__ == "__main__":
    main()