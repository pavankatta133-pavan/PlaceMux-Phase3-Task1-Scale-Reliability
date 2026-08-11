"""
Phase 3 Task 6
Growth Instrumentation - End-to-End Validation

Validates that:
    impression -> click -> application -> shortlist

events can be joined using ranking_request_id,
student_id, job_id, position and model_version.
"""

import json
import os
import sys
from collections import defaultdict


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)

from growth_instrumentation.event_logger import (
    read_events
)


REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "growth_instrumentation",
    "reports"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "end_to_end_validation.json"
)


EVENT_SEQUENCE = [
    "impression",
    "click",
    "application",
    "shortlist",
]


def create_event_key(event):

    return (
        event["ranking_request_id"],
        event["student_id"],
        event["job_id"],
        event["position"],
        event["model_version"],
    )


def validate_events(events):

    grouped = defaultdict(set)

    invalid_events = []

    for event in events:

        required_fields = [
            "event_id",
            "event_type",
            "ranking_request_id",
            "student_id",
            "job_id",
            "position",
            "model_version",
            "timestamp",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in event
        ]

        if missing_fields:

            invalid_events.append({
                "event_id":
                    event.get(
                        "event_id"
                    ),

                "missing_fields":
                    missing_fields,
            })

            continue

        key = create_event_key(
            event
        )

        grouped[key].add(
            event["event_type"]
        )

    complete_journeys = 0
    partial_journeys = 0

    sequence_counts = {
        "impression": 0,
        "click": 0,
        "application": 0,
        "shortlist": 0,
    }

    journey_examples = []

    for key, event_types in grouped.items():

        for event_type in EVENT_SEQUENCE:

            if event_type in event_types:

                sequence_counts[
                    event_type
                ] += 1

        if all(
            event_type in event_types
            for event_type in EVENT_SEQUENCE
        ):

            complete_journeys += 1

            if len(journey_examples) < 10:

                journey_examples.append({
                    "ranking_request_id":
                        key[0],

                    "student_id":
                        key[1],

                    "job_id":
                        key[2],

                    "position":
                        key[3],

                    "model_version":
                        key[4],

                    "event_sequence":
                        EVENT_SEQUENCE,
                })

        elif "impression" in event_types:

            partial_journeys += 1

    total_groups = len(grouped)

    report = {

        "validation":
            "Growth Instrumentation "
            "End-to-End Event Flow",

        "total_events":
            len(events),

        "unique_ranked_results":
            total_groups,

        "complete_journeys":
            complete_journeys,

        "partial_journeys":
            partial_journeys,

        "event_presence": {

            "impression":
                sequence_counts[
                    "impression"
                ],

            "click":
                sequence_counts[
                    "click"
                ],

            "application":
                sequence_counts[
                    "application"
                ],

            "shortlist":
                sequence_counts[
                    "shortlist"
                ],
        },

        "invalid_events":
            invalid_events,

        "sample_complete_journeys":
            journey_examples,

        "overall_success":
            (
                len(events) > 0
                and
                total_groups > 0
                and
                invalid_events == []
            ),
    }

    return report


def save_report(report):

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

    return report


def main():

    print("=" * 60)

    print(
        "PHASE 3 TASK 6 - "
        "END-TO-END EVENT VALIDATION"
    )

    print("=" * 60)

    events = read_events()

    print(
        f"\nTotal events: "
        f"{len(events)}"
    )

    report = validate_events(
        events
    )

    save_report(
        report
    )

    print(
        "\nUnique ranked results: "
        f"{report['unique_ranked_results']}"
    )

    print(
        "Complete journeys: "
        f"{report['complete_journeys']}"
    )

    print(
        "Partial journeys: "
        f"{report['partial_journeys']}"
    )

    print("\nEvent presence:")

    for event_type, count in (
        report["event_presence"]
        .items()
    ):

        print(
            f"{event_type.capitalize():15}: "
            f"{count}"
        )

    print(
        "\nInvalid events: "
        f"{len(report['invalid_events'])}"
    )

    print(
        "\nOverall validation: "
        f"{'PASS' if report['overall_success'] else 'FAIL'}"
    )

    print(
        "\nValidation report saved to:"
    )

    print(
        REPORT_FILE
    )


if __name__ == "__main__":
    main()