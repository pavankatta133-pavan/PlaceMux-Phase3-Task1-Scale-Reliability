"""
Task 17
Public API, Webhooks & ATS Partner Integrations

End-to-End Integration Test
"""

from public_api.api import (
    safe_score_candidate
)

from public_api.api_config import (
    authenticate_partner,
    get_partner
)

from public_api.rate_limit import (
    RateLimiter,
    RateLimitExceeded,
    QuotaExceeded
)

from public_api.webhook import (
    create_score_completed_event,
    create_score_failed_event,
    validate_webhook_event
)


def test_partner_authentication():

    alpha = authenticate_partner(
        "ats_alpha_key"
    )

    beta = authenticate_partner(
        "ats_beta_key"
    )

    if alpha != "ats_alpha":
        raise RuntimeError(
            "ATS Alpha authentication failed."
        )

    if beta != "ats_beta":
        raise RuntimeError(
            "ATS Beta authentication failed."
        )

    print(
        "Partner authentication: PASS"
    )


def test_public_scoring():

    response = safe_score_candidate(
        api_key="ats_alpha_key",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    if response["status"] != "success":
        raise RuntimeError(
            "Public scoring failed."
        )

    data = response["data"]

    if data["partner_id"] != "ats_alpha":
        raise RuntimeError(
            "Incorrect partner in API response."
        )

    if data["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Incorrect tenant in API response."
        )

    if not isinstance(
        data["score"],
        (int, float)
    ):
        raise RuntimeError(
            "API score is not numeric."
        )

    if not data["explanation"]:
        raise RuntimeError(
            "API explanation is missing."
        )

    print(
        "Public score + explanation: PASS"
    )

    print(
        "Score:",
        data["score"]
    )

    print(
        "Decision:",
        data["decision"]
    )


def test_second_partner():

    response = safe_score_candidate(
        api_key="ats_beta_key",
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001"
    )

    if response["status"] != "success":
        raise RuntimeError(
            "ATS Beta scoring failed."
        )

    data = response["data"]

    if data["partner_id"] != "ats_beta":
        raise RuntimeError(
            "ATS Beta identity is incorrect."
        )

    if data["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "ATS Beta tenant is incorrect."
        )

    print(
        "Multi-partner scoring: PASS"
    )


def test_invalid_authentication():

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


def test_rate_limit():

    limiter = RateLimiter()

    partner_id = "ats_alpha"

    rate_limit = get_partner(
        partner_id
    )["rate_limit"]

    for _ in range(rate_limit):

        limiter.record_request(
            partner_id
        )

    try:

        limiter.record_request(
            partner_id
        )

    except RateLimitExceeded:

        print(
            "Rate-limit enforcement: PASS"
        )

    else:

        raise RuntimeError(
            "Rate limit was not enforced."
        )


def test_daily_quota():

    limiter = RateLimiter()

    partner_id = "ats_beta"

    quota = get_partner(
        partner_id
    )["daily_quota"]

    limiter.daily_usage[
        partner_id
    ] = quota

    try:

        limiter.record_request(
            partner_id
        )

    except QuotaExceeded:

        print(
            "Daily quota enforcement: PASS"
        )

    else:

        raise RuntimeError(
            "Daily quota was not enforced."
        )


def test_webhook_success():

    event = create_score_completed_event(
        partner_id="ats_alpha",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001",
        score=0.95,
        decision="selected",
        explanation=(
            "Candidate selected based on "
            "configured matching criteria."
        )
    )

    validate_webhook_event(
        event
    )

    if event["event_type"] != (
        "score.completed"
    ):
        raise RuntimeError(
            "Incorrect success webhook."
        )

    if event["partner_id"] != "ats_alpha":
        raise RuntimeError(
            "Webhook partner is incorrect."
        )

    if event["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Webhook tenant is incorrect."
        )

    if not event["payload"]["explanation"]:
        raise RuntimeError(
            "Webhook explanation is missing."
        )

    print(
        "Success webhook: PASS"
    )


def test_webhook_failure():

    event = create_score_failed_event(
        partner_id="ats_alpha",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001",
        error_code="MODEL_UNAVAILABLE",
        message=(
            "Scoring service is temporarily "
            "unavailable."
        )
    )

    validate_webhook_event(
        event
    )

    if event["event_type"] != (
        "score.failed"
    ):
        raise RuntimeError(
            "Incorrect failure webhook."
        )

    if event["payload"]["error_code"] != (
        "MODEL_UNAVAILABLE"
    ):
        raise RuntimeError(
            "Incorrect failure code."
        )

    print(
        "Failure webhook: PASS"
    )


def test_model_failure():

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


def test_model_protection():

    response = safe_score_candidate(
        api_key="ats_alpha_key",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001"
    )

    data = response["data"]

    forbidden = {
        "model",
        "model_path",
        "model_file",
        "weights",
        "embedding",
        "raw_model",
        "internal_model"
    }

    exposed = forbidden.intersection(
        data.keys()
    )

    if exposed:
        raise RuntimeError(
            f"Model internals exposed: {exposed}"
        )

    print(
        "Model protection: PASS"
    )


def test_tenant_partner_isolation():

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

    if alpha["data"]["partner_id"] != "ats_alpha":
        raise RuntimeError(
            "Alpha partner identity leaked."
        )

    if beta["data"]["partner_id"] != "ats_beta":
        raise RuntimeError(
            "Beta partner identity leaked."
        )

    if alpha["data"]["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Alpha tenant identity leaked."
        )

    if beta["data"]["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "Beta tenant identity leaked."
        )

    print(
        "Partner/tenant isolation: PASS"
    )


def main():

    print(
        "\n========== TASK 17 INTEGRATION TEST =========="
    )

    test_partner_authentication()

    test_public_scoring()

    test_second_partner()

    test_invalid_authentication()

    test_rate_limit()

    test_daily_quota()

    test_webhook_success()

    test_webhook_failure()

    test_model_failure()

    test_model_protection()

    test_tenant_partner_isolation()

    print(
        "\nPublic API: PASS"
    )

    print(
        "Partner authentication: PASS"
    )

    print(
        "Score + explanation: PASS"
    )

    print(
        "Rate limiting: PASS"
    )

    print(
        "Daily quota: PASS"
    )

    print(
        "Webhooks: PASS"
    )

    print(
        "Failure handling: PASS"
    )

    print(
        "Model protection: PASS"
    )

    print(
        "Partner/tenant isolation: PASS"
    )

    print(
        "\nTASK 17 INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":
    main()