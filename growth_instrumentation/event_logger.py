"""
Phase 3 Task 6
Growth Instrumentation Event Logger

Supports normal event logging and controlled failure
injection for reliability testing.
"""

import json
import os
from threading import Lock

from growth_instrumentation.event_schema import (
    create_event,
)


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "growth_instrumentation",
    "data",
)

EVENT_LOG_FILE = os.path.join(
    DATA_DIR,
    "growth_events.jsonl",
)

_lock = Lock()


def ensure_data_directory():

    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )


def instrumentation_failure_enabled():

    return (
        os.getenv(
            "TASK6_FORCE_INSTRUMENTATION_FAILURE",
            "false",
        ).lower()
        == "true"
    )


def log_event(
    event_type,
    ranking_request_id,
    student_id,
    job_id,
    position,
    model_version,
    metadata=None,
):

    ensure_data_directory()

    # -------------------------------------------------
    # TASK 6 FAILURE INJECTION
    # -------------------------------------------------
    # When enabled, simulate an analytics/logging
    # failure without affecting the recommendation
    # calculation itself.
    # -------------------------------------------------

    if instrumentation_failure_enabled():

        raise RuntimeError(
            "Synthetic growth instrumentation failure "
            "injected for Phase 3 Task 6 testing."
        )

    event = create_event(
        event_type=event_type,
        ranking_request_id=ranking_request_id,
        student_id=student_id,
        job_id=job_id,
        position=position,
        model_version=model_version,
        metadata=metadata,
    )

    with _lock:

        with open(
            EVENT_LOG_FILE,
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                json.dumps(
                    event.to_dict()
                )
                + "\n"
            )

    return event.to_dict()


def read_events():

    ensure_data_directory()

    if not os.path.exists(
        EVENT_LOG_FILE
    ):

        return []

    events = []

    with open(
        EVENT_LOG_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            events.append(
                json.loads(line)
            )

    return events