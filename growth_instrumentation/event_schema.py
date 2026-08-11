"""
Phase 3 Task 6
Growth Instrumentation - Event Schema

Defines the canonical event structure for:
    - impression
    - click
    - application
    - shortlist
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional
import uuid


VALID_EVENT_TYPES = {
    "impression",
    "click",
    "application",
    "shortlist",
}


@dataclass
class GrowthEvent:

    event_id: str
    event_type: str

    ranking_request_id: str

    student_id: str
    job_id: str

    position: int
    model_version: str

    timestamp: str

    metadata: Optional[dict] = None

    def to_dict(self):
        return asdict(self)


def create_event(
    event_type,
    ranking_request_id,
    student_id,
    job_id,
    position,
    model_version,
    metadata=None,
):
    """
    Create and validate a growth instrumentation event.
    """

    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(
            f"Invalid event_type: {event_type}"
        )

    if not ranking_request_id:
        raise ValueError(
            "ranking_request_id is required"
        )

    if not student_id:
        raise ValueError(
            "student_id is required"
        )

    if not job_id:
        raise ValueError(
            "job_id is required"
        )

    if not isinstance(position, int):
        raise ValueError(
            "position must be an integer"
        )

    if position < 1:
        raise ValueError(
            "position must be >= 1"
        )

    if not model_version:
        raise ValueError(
            "model_version is required"
        )

    return GrowthEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        ranking_request_id=ranking_request_id,
        student_id=student_id,
        job_id=job_id,
        position=position,
        model_version=model_version,
        timestamp=datetime.now(
            timezone.utc
        ).isoformat(),
        metadata=metadata or {},
    )