"""
Task 16
Enterprise Multi-Tenancy & RBAC
End-to-End Integration Test
"""

from tenant_governance.tenant_config import (
    get_matching_config,
    validate_all_tenants
)

from tenant_governance.tenant_data import (
    get_tenant_data,
    get_job,
    get_candidate
)

from tenant_governance.inference import (
    calculate_match,
    explain_result
)

from tenant_governance.serving import (
    safe_infer
)


def test_tenant_configurations():

    validate_all_tenants()

    alpha = get_matching_config(
        "tenant_alpha"
    )

    beta = get_matching_config(
        "tenant_beta"
    )

    if alpha == beta:
        raise RuntimeError(
            "Tenant configurations must be different."
        )

    if alpha["threshold"] == beta["threshold"]:
        raise RuntimeError(
            "Tenant thresholds are not tenant-specific."
        )

    if alpha["weights"] == beta["weights"]:
        raise RuntimeError(
            "Tenant weights are not tenant-specific."
        )

    print(
        "Tenant-specific configuration: PASS"
    )


def test_tenant_data():

    alpha = get_tenant_data(
        "tenant_alpha"
    )

    beta = get_tenant_data(
        "tenant_beta"
    )

    if alpha["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Alpha data has incorrect tenant ID."
        )

    if beta["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "Beta data has incorrect tenant ID."
        )

    alpha_text = str(alpha)
    beta_text = str(beta)

    if "beta_job_" in alpha_text:
        raise RuntimeError(
            "Beta job data leaked into Alpha."
        )

    if "alpha_job_" in beta_text:
        raise RuntimeError(
            "Alpha job data leaked into Beta."
        )

    if "beta_candidate_" in alpha_text:
        raise RuntimeError(
            "Beta candidate data leaked into Alpha."
        )

    if "alpha_candidate_" in beta_text:
        raise RuntimeError(
            "Alpha candidate data leaked into Beta."
        )

    print(
        "Tenant data isolation: PASS"
    )


def test_tenant_inference():

    alpha = calculate_match(
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    beta = calculate_match(
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001"
    )

    if alpha["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Alpha inference returned wrong tenant."
        )

    if beta["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "Beta inference returned wrong tenant."
        )

    if alpha["candidate_id"] != "alpha_candidate_001":
        raise RuntimeError(
            "Alpha candidate is incorrect."
        )

    if beta["candidate_id"] != "beta_candidate_001":
        raise RuntimeError(
            "Beta candidate is incorrect."
        )

    print(
        "Tenant-scoped inference: PASS"
    )

    print(
        "Alpha score:",
        alpha["score"]
    )

    print(
        "Beta score:",
        beta["score"]
    )


def test_different_tenant_tuning():

    alpha_config = get_matching_config(
        "tenant_alpha"
    )

    beta_config = get_matching_config(
        "tenant_beta"
    )

    alpha = calculate_match(
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    beta = calculate_match(
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001"
    )

    if alpha["threshold"] != alpha_config["threshold"]:
        raise RuntimeError(
            "Alpha threshold was not applied."
        )

    if beta["threshold"] != beta_config["threshold"]:
        raise RuntimeError(
            "Beta threshold was not applied."
        )

    if alpha["weights"] != alpha_config["weights"]:
        raise RuntimeError(
            "Alpha weights were not applied."
        )

    if beta["weights"] != beta_config["weights"]:
        raise RuntimeError(
            "Beta weights were not applied."
        )

    print(
        "Different tenant tuning: PASS"
    )


def test_explainability():

    alpha = calculate_match(
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    beta = calculate_match(
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001"
    )

    alpha_explanation = explain_result(
        alpha
    )

    beta_explanation = explain_result(
        beta
    )

    if not alpha_explanation:
        raise RuntimeError(
            "Alpha explanation is empty."
        )

    if not beta_explanation:
        raise RuntimeError(
            "Beta explanation is empty."
        )

    if "tenant_alpha" not in alpha_explanation:
        raise RuntimeError(
            "Alpha explanation has incorrect tenant."
        )

    if "tenant_beta" not in beta_explanation:
        raise RuntimeError(
            "Beta explanation has incorrect tenant."
        )

    print(
        "Plain-English explanations: PASS"
    )


def test_cross_tenant_access():

    failures = 0

    try:
        get_job(
            "tenant_alpha",
            "beta_job_001"
        )
    except ValueError:
        failures += 1

    try:
        get_job(
            "tenant_beta",
            "alpha_job_001"
        )
    except ValueError:
        failures += 1

    try:
        get_candidate(
            "tenant_alpha",
            "beta_candidate_001"
        )
    except ValueError:
        failures += 1

    try:
        get_candidate(
            "tenant_beta",
            "alpha_candidate_001"
        )
    except ValueError:
        failures += 1

    if failures != 4:
        raise RuntimeError(
            "Cross-tenant access was not fully rejected."
        )

    print(
        "Cross-tenant access rejection: PASS"
    )


def test_cross_tenant_inference():

    failures = 0

    try:
        calculate_match(
            tenant_id="tenant_alpha",
            candidate_id="beta_candidate_001",
            job_id="alpha_job_001"
        )
    except ValueError:
        failures += 1

    try:
        calculate_match(
            tenant_id="tenant_beta",
            candidate_id="alpha_candidate_001",
            job_id="beta_job_001"
        )
    except ValueError:
        failures += 1

    if failures != 2:
        raise RuntimeError(
            "Cross-tenant inference was not rejected."
        )

    print(
        "Cross-tenant inference rejection: PASS"
    )


def test_model_failure():

    alpha_response = safe_infer(
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001",
        model_available=False
    )

    beta_response = safe_infer(
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001",
        model_available=False
    )

    if alpha_response["status"] != "unavailable":
        raise RuntimeError(
            "Alpha model failure was not handled safely."
        )

    if beta_response["status"] != "unavailable":
        raise RuntimeError(
            "Beta model failure was not handled safely."
        )

    if alpha_response["fallback_used"] is not False:
        raise RuntimeError(
            "Alpha incorrectly used fallback model."
        )

    if beta_response["fallback_used"] is not False:
        raise RuntimeError(
            "Beta incorrectly used fallback model."
        )

    if alpha_response["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Alpha failure response has wrong tenant."
        )

    if beta_response["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "Beta failure response has wrong tenant."
        )

    print(
        "Model unavailable handling: PASS"
    )

    print(
        "No cross-tenant fallback: PASS"
    )


def main():

    print(
        "\n========== TASK 16 INTEGRATION TEST =========="
    )

    test_tenant_configurations()

    test_tenant_data()

    test_tenant_inference()

    test_different_tenant_tuning()

    test_explainability()

    test_cross_tenant_access()

    test_cross_tenant_inference()

    test_model_failure()

    print(
        "\nTenant configuration: PASS"
    )

    print(
        "Tenant data isolation: PASS"
    )

    print(
        "Tenant-scoped inference: PASS"
    )

    print(
        "Per-tenant tuning: PASS"
    )

    print(
        "Explainability: PASS"
    )

    print(
        "Cross-tenant isolation: PASS"
    )

    print(
        "Safe failure handling: PASS"
    )

    print(
        "\nTASK 16 INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":
    main()