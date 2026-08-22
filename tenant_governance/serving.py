"""
Task 16
Tenant-Scoped Serving and Safe Failure Handling
"""

from tenant_governance.inference import (
    calculate_match,
    explain_result
)


class ModelUnavailableError(Exception):
    """Raised when the tenant model is unavailable."""


def infer(
    tenant_id,
    candidate_id,
    job_id,
    model_available=True
):
    """
    Tenant-scoped inference endpoint.

    If the model is unavailable, fail safely instead of
    falling back to another tenant's model or data.
    """

    if not model_available:
        raise ModelUnavailableError(
            f"Model unavailable for tenant {tenant_id}."
        )

    return calculate_match(
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        job_id=job_id
    )


def explain(
    tenant_id,
    candidate_id,
    job_id,
    model_available=True
):
    """
    Return a tenant-scoped inference result with
    a plain-English explanation.
    """

    result = infer(
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        job_id=job_id,
        model_available=model_available
    )

    response = dict(result)

    response["explanation"] = explain_result(
        result
    )

    return response


def safe_infer(
    tenant_id,
    candidate_id,
    job_id,
    model_available=True
):
    """
    Safe serving wrapper.

    Model failures return an explicit unavailable
    response. No cross-tenant fallback is attempted.
    """

    try:

        result = explain(
            tenant_id=tenant_id,
            candidate_id=candidate_id,
            job_id=job_id,
            model_available=model_available
        )

        return {
            "status": "ok",
            "result": result
        }

    except ModelUnavailableError as error:

        return {
            "status": "unavailable",
            "tenant_id": tenant_id,
            "decision": "not_available",
            "message": str(error),
            "fallback_used": False
        }


def test_normal_serving():

    response = safe_infer(
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    if response["status"] != "ok":
        raise RuntimeError(
            "Normal tenant inference failed."
        )

    result = response["result"]

    if result["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Serving returned the wrong tenant."
        )

    if "explanation" not in result:
        raise RuntimeError(
            "Serving response has no explanation."
        )

    print(
        "Normal tenant serving: PASS"
    )


def test_model_unavailable():

    response = safe_infer(
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001",
        model_available=False
    )

    if response["status"] != "unavailable":
        raise RuntimeError(
            "Unavailable model was not handled safely."
        )

    if response["fallback_used"] is not False:
        raise RuntimeError(
            "Serving incorrectly used a fallback model."
        )

    if response["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Unavailable response has wrong tenant."
        )

    print(
        "Model unavailable failure path: PASS"
    )


def test_tenant_scoped_serving():

    alpha = safe_infer(
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    beta = safe_infer(
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001"
    )

    if alpha["result"]["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Alpha serving escaped tenant scope."
        )

    if beta["result"]["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "Beta serving escaped tenant scope."
        )

    print(
        "Multi-tenant serving isolation: PASS"
    )


def main():

    print(
        "\n========== TASK 16 SERVING =========="
    )

    test_normal_serving()

    test_model_unavailable()

    test_tenant_scoped_serving()

    print(
        "\nSafe model failure handling: PASS"
    )

    print(
        "No cross-tenant fallback: PASS"
    )

    print(
        "\nTASK 16 SERVING: PASS"
    )


if __name__ == "__main__":
    main()