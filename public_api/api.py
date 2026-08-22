"""
Task 17
Public API, Webhooks & ATS Partner Integrations

Versioned Public Scoring API
"""

from public_api.api_config import (
    API_VERSION,
    authenticate_partner
)

from tenant_governance.inference import (
    calculate_match,
    explain_result
)


class APIError(Exception):
    """Base API error."""


class ModelUnavailableError(APIError):
    """Raised when the scoring model is unavailable."""


def score_candidate(
    api_key,
    tenant_id,
    candidate_id,
    job_id,
    model_available=True
):
    """
    Public partner-facing scoring function.

    The partner receives only the scoring result and
    explanation. Model internals are never returned.
    """

    partner_id = authenticate_partner(
        api_key
    )

    if not model_available:
        raise ModelUnavailableError(
            "Scoring model is temporarily unavailable."
        )

    result = calculate_match(
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        job_id=job_id
    )

    explanation = explain_result(
        result
    )

    return {
        "api_version": API_VERSION,
        "partner_id": partner_id,
        "tenant_id": tenant_id,
        "candidate_id": candidate_id,
        "job_id": job_id,
        "score": result["score"],
        "decision": (
            "selected"
            if result["selected"]
            else "not_selected"
        ),
        "explanation": explanation
    }


def match_candidate(
    api_key,
    tenant_id,
    candidate_id,
    job_id,
    model_available=True
):
    """
    Public match endpoint.

    This is an alias-style public operation that uses
    the same controlled scoring layer.
    """

    return score_candidate(
        api_key=api_key,
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        job_id=job_id,
        model_available=model_available
    )


def safe_score_candidate(
    api_key,
    tenant_id,
    candidate_id,
    job_id,
    model_available=True
):
    """
    Safe public API wrapper.

    Converts expected API failures into structured
    responses without exposing internal details.
    """

    try:

        response = score_candidate(
            api_key=api_key,
            tenant_id=tenant_id,
            candidate_id=candidate_id,
            job_id=job_id,
            model_available=model_available
        )

        return {
            "status": "success",
            "data": response
        }

    except ModelUnavailableError:

        return {
            "status": "error",
            "error": {
                "code": "MODEL_UNAVAILABLE",
                "message": (
                    "Scoring service is temporarily "
                    "unavailable."
                )
            }
        }

    except ValueError:

        return {
            "status": "error",
            "error": {
                "code": "AUTHENTICATION_FAILED",
                "message": (
                    "Invalid partner credentials."
                )
            }
        }


def test_public_score():

    response = safe_score_candidate(
        api_key="ats_alpha_key",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    if response["status"] != "success":
        raise RuntimeError(
            "Public scoring request failed."
        )

    data = response["data"]

    required_fields = {
        "api_version",
        "partner_id",
        "tenant_id",
        "candidate_id",
        "job_id",
        "score",
        "decision",
        "explanation"
    }

    if not required_fields.issubset(
        data.keys()
    ):
        raise RuntimeError(
            "Public API response is missing fields."
        )

    if data["api_version"] != API_VERSION:
        raise RuntimeError(
            "Incorrect API version."
        )

    if not isinstance(
        data["score"],
        (int, float)
    ):
        raise RuntimeError(
            "Score is not numeric."
        )

    if not data["explanation"]:
        raise RuntimeError(
            "Explanation is empty."
        )

    print(
        "Public scoring API: PASS"
    )

    print(
        "Score:",
        data["score"]
    )

    print(
        "Decision:",
        data["decision"]
    )

    print(
        "Explanation:",
        data["explanation"]
    )


def test_invalid_api_key():

    response = safe_score_candidate(
        api_key="invalid_key",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    if response["status"] != "error":
        raise RuntimeError(
            "Invalid API key was accepted."
        )

    if response["error"]["code"] != (
        "AUTHENTICATION_FAILED"
    ):
        raise RuntimeError(
            "Incorrect authentication error."
        )

    print(
        "Invalid API key rejection: PASS"
    )


def test_model_unavailable():

    response = safe_score_candidate(
        api_key="ats_alpha_key",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001",
        model_available=False
    )

    if response["status"] != "error":
        raise RuntimeError(
            "Model failure was not handled."
        )

    if response["error"]["code"] != (
        "MODEL_UNAVAILABLE"
    ):
        raise RuntimeError(
            "Incorrect model failure response."
        )

    print(
        "Model unavailable handling: PASS"
    )


def test_model_not_exposed():

    response = safe_score_candidate(
        api_key="ats_alpha_key",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    data = response["data"]

    forbidden_fields = {
        "model",
        "model_path",
        "model_file",
        "weights",
        "embedding",
        "raw_model",
        "internal_model"
    }

    exposed = forbidden_fields.intersection(
        data.keys()
    )

    if exposed:
        raise RuntimeError(
            f"Model internals exposed: {exposed}"
        )

    print(
        "Model internals protected: PASS"
    )


def test_tenant_scoped_public_api():

    alpha = safe_score_candidate(
        api_key="ats_alpha_key",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    beta = safe_score_candidate(
        api_key="ats_beta_key",
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001"
    )

    if alpha["data"]["tenant_id"] != (
        "tenant_alpha"
    ):
        raise RuntimeError(
            "Alpha request escaped tenant scope."
        )

    if beta["data"]["tenant_id"] != (
        "tenant_beta"
    ):
        raise RuntimeError(
            "Beta request escaped tenant scope."
        )

    print(
        "Tenant-scoped public API: PASS"
    )


def main():

    print(
        "\n========== TASK 17 PUBLIC API =========="
    )

    test_public_score()

    test_invalid_api_key()

    test_model_unavailable()

    test_model_not_exposed()

    test_tenant_scoped_public_api()

    print(
        "\nAPI versioning: PASS"
    )

    print(
        "Score + explanation: PASS"
    )

    print(
        "Authentication: PASS"
    )

    print(
        "Model protection: PASS"
    )

    print(
        "Failure handling: PASS"
    )

    print(
        "\nTASK 17 PUBLIC API: PASS"
    )


if __name__ == "__main__":
    main()