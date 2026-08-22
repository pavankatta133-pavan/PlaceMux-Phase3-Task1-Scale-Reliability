"""
Task 17
Public API, Webhooks & ATS Partner Integrations

Webhook Delivery
"""

from datetime import datetime, timezone
import json


WEBHOOK_EVENTS = {
    "score.completed",
    "score.failed"
}


class WebhookError(Exception):
    """Base webhook error."""


def create_webhook_event(
    event_type,
    partner_id,
    tenant_id,
    candidate_id,
    job_id,
    payload
):
    """
    Create a webhook event that an ATS partner can consume.
    """

    if event_type not in WEBHOOK_EVENTS:
        raise WebhookError(
            f"Unsupported webhook event: {event_type}"
        )

    if not partner_id:
        raise WebhookError(
            "partner_id is required."
        )

    if not tenant_id:
        raise WebhookError(
            "tenant_id is required."
        )

    return {
        "event_id": (
            f"{event_type}-"
            f"{partner_id}-"
            f"{candidate_id}"
        ),
        "event_type": event_type,
        "api_version": "v1",
        "partner_id": partner_id,
        "tenant_id": tenant_id,
        "candidate_id": candidate_id,
        "job_id": job_id,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "payload": payload
    }


def create_score_completed_event(
    partner_id,
    tenant_id,
    candidate_id,
    job_id,
    score,
    decision,
    explanation
):
    """
    Create a webhook event after successful scoring.
    """

    payload = {
        "score": score,
        "decision": decision,
        "explanation": explanation
    }

    return create_webhook_event(
        event_type="score.completed",
        partner_id=partner_id,
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        job_id=job_id,
        payload=payload
    )


def create_score_failed_event(
    partner_id,
    tenant_id,
    candidate_id,
    job_id,
    error_code,
    message
):
    """
    Create a webhook event for a failed scoring request.
    """

    payload = {
        "error_code": error_code,
        "message": message
    }

    return create_webhook_event(
        event_type="score.failed",
        partner_id=partner_id,
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        job_id=job_id,
        payload=payload
    )


def serialize_event(event):
    """
    Serialize an event for delivery to an ATS partner.
    """

    return json.dumps(
        event,
        separators=(",", ":")
    )


def validate_webhook_event(event):
    """
    Validate the public webhook contract.
    """

    required_fields = {
        "event_id",
        "event_type",
        "api_version",
        "partner_id",
        "tenant_id",
        "candidate_id",
        "job_id",
        "timestamp",
        "payload"
    }

    missing = (
        required_fields
        - set(event.keys())
    )

    if missing:
        raise WebhookError(
            f"Missing webhook fields: {missing}"
        )

    if event["event_type"] not in WEBHOOK_EVENTS:
        raise WebhookError(
            "Invalid webhook event type."
        )

    if event["api_version"] != "v1":
        raise WebhookError(
            "Unsupported API version."
        )

    return True


def test_score_completed_webhook():

    event = create_score_completed_event(
        partner_id="ats_alpha",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001",
        score=0.95,
        decision="selected",
        explanation=(
            "Candidate selected based on "
            "matching criteria."
        )
    )

    validate_webhook_event(
        event
    )

    if event["event_type"] != (
        "score.completed"
    ):
        raise RuntimeError(
            "Incorrect completion event."
        )

    if event["tenant_id"] != (
        "tenant_alpha"
    ):
        raise RuntimeError(
            "Incorrect tenant in webhook."
        )

    if event["payload"]["score"] != 0.95:
        raise RuntimeError(
            "Score missing from webhook."
        )

    if not event["payload"]["explanation"]:
        raise RuntimeError(
            "Explanation missing from webhook."
        )

    print(
        "Score completion webhook: PASS"
    )


def test_score_failed_webhook():

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
            "Incorrect failure event."
        )

    if event["payload"]["error_code"] != (
        "MODEL_UNAVAILABLE"
    ):
        raise RuntimeError(
            "Incorrect failure code."
        )

    print(
        "Score failure webhook: PASS"
    )


def test_webhook_serialization():

    event = create_score_completed_event(
        partner_id="ats_beta",
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001",
        score=0.88,
        decision="selected",
        explanation=(
            "Candidate selected based on "
            "configured matching criteria."
        )
    )

    serialized = serialize_event(
        event
    )

    if not serialized:
        raise RuntimeError(
            "Webhook serialization failed."
        )

    decoded = json.loads(
        serialized
    )

    if decoded["partner_id"] != (
        "ats_beta"
    ):
        raise RuntimeError(
            "Serialized webhook has wrong partner."
        )

    if decoded["tenant_id"] != (
        "tenant_beta"
    ):
        raise RuntimeError(
            "Serialized webhook has wrong tenant."
        )

    print(
        "Webhook serialization: PASS"
    )


def test_invalid_event():

    try:

        create_webhook_event(
            event_type="invalid.event",
            partner_id="ats_alpha",
            tenant_id="tenant_alpha",
            candidate_id="alpha_candidate_001",
            job_id="alpha_job_001",
            payload={}
        )

    except WebhookError:

        print(
            "Invalid webhook rejection: PASS"
        )

        return

    raise RuntimeError(
        "Invalid webhook event was accepted."
    )


def test_partner_tenant_isolation():

    alpha_event = create_score_completed_event(
        partner_id="ats_alpha",
        tenant_id="tenant_alpha",
        candidate_id="alpha_candidate_001",
        job_id="alpha_job_001",
        score=0.95,
        decision="selected",
        explanation="Alpha result."
    )

    beta_event = create_score_completed_event(
        partner_id="ats_beta",
        tenant_id="tenant_beta",
        candidate_id="beta_candidate_001",
        job_id="beta_job_001",
        score=0.88,
        decision="selected",
        explanation="Beta result."
    )

    if alpha_event["partner_id"] != "ats_alpha":
        raise RuntimeError(
            "Alpha partner identity leaked."
        )

    if beta_event["partner_id"] != "ats_beta":
        raise RuntimeError(
            "Beta partner identity leaked."
        )

    if alpha_event["tenant_id"] != "tenant_alpha":
        raise RuntimeError(
            "Alpha tenant identity leaked."
        )

    if beta_event["tenant_id"] != "tenant_beta":
        raise RuntimeError(
            "Beta tenant identity leaked."
        )

    print(
        "Partner and tenant isolation: PASS"
    )


def main():

    print(
        "\n========== TASK 17 WEBHOOKS =========="
    )

    test_score_completed_webhook()

    test_score_failed_webhook()

    test_webhook_serialization()

    test_invalid_event()

    test_partner_tenant_isolation()

    print(
        "\nScore completion events: PASS"
    )

    print(
        "Failure events: PASS"
    )

    print(
        "Webhook serialization: PASS"
    )

    print(
        "Partner/tenant isolation: PASS"
    )

    print(
        "\nTASK 17 WEBHOOKS: PASS"
    )


if __name__ == "__main__":
    main()