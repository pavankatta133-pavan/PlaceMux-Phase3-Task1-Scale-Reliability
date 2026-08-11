"""
Phase 3 Task 6
Growth Instrumentation - End-to-End Event Generator

Generates realistic ranking events for:
    impression
    click
    application
    shortlist

Supports both:
    ranker_v1.0
    ranker_v2.0
"""

import os
import random
import sys
import uuid

# Allow execution from project root
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
    log_event
)


MODEL_VERSIONS = [
    "ranker_v1.0",
    "ranker_v2.0",
]


JOBS = [
    "job_001",
    "job_002",
    "job_003",
    "job_004",
    "job_005",
]


STUDENTS = [
    "student_001",
    "student_002",
    "student_003",
    "student_004",
    "student_005",
    "student_006",
    "student_007",
    "student_008",
    "student_009",
    "student_010",
]


def generate_ranking_request(
    model_version,
    student_id,
):
    """
    Generate one ranked result list.

    Each ranking request contains multiple positions.
    """

    ranking_request_id = str(
        uuid.uuid4()
    )

    selected_jobs = random.sample(
        JOBS,
        k=len(JOBS)
    )

    results = []

    for position, job_id in enumerate(
        selected_jobs,
        start=1
    ):

        result = {
            "ranking_request_id":
                ranking_request_id,

            "student_id":
                student_id,

            "job_id":
                job_id,

            "position":
                position,

            "model_version":
                model_version,
        }

        results.append(result)

    return results


def generate_events(
    requests_per_model=100
):

    total_events = {
        "impression": 0,
        "click": 0,
        "application": 0,
        "shortlist": 0,
    }

    for model_version in MODEL_VERSIONS:

        print(
            f"\nGenerating traffic for "
            f"{model_version}..."
        )

        for _ in range(
            requests_per_model
        ):

            student_id = random.choice(
                STUDENTS
            )

            ranking_results = (
                generate_ranking_request(
                    model_version,
                    student_id,
                )
            )

            for result in ranking_results:

                ranking_request_id = (
                    result[
                        "ranking_request_id"
                    ]
                )

                student_id = result[
                    "student_id"
                ]

                job_id = result[
                    "job_id"
                ]

                position = result[
                    "position"
                ]

                # -------------------------------------------------
                # 1. IMPRESSION
                # -------------------------------------------------

                log_event(
                    event_type="impression",

                    ranking_request_id=(
                        ranking_request_id
                    ),

                    student_id=student_id,

                    job_id=job_id,

                    position=position,

                    model_version=(
                        model_version
                    ),
                )

                total_events[
                    "impression"
                ] += 1

                # -------------------------------------------------
                # 2. CLICK
                # -------------------------------------------------

                # Higher-ranked positions
                # receive a higher click probability.
                click_probability = max(
                    0.05,
                    0.35
                    - (
                        position * 0.04
                    )
                )

                clicked = (
                    random.random()
                    < click_probability
                )

                if not clicked:
                    continue

                log_event(
                    event_type="click",

                    ranking_request_id=(
                        ranking_request_id
                    ),

                    student_id=student_id,

                    job_id=job_id,

                    position=position,

                    model_version=(
                        model_version
                    ),
                )

                total_events[
                    "click"
                ] += 1

                # -------------------------------------------------
                # 3. APPLICATION
                # -------------------------------------------------

                application_probability = (
                    0.25
                )

                applied = (
                    random.random()
                    < application_probability
                )

                if not applied:
                    continue

                log_event(
                    event_type="application",

                    ranking_request_id=(
                        ranking_request_id
                    ),

                    student_id=student_id,

                    job_id=job_id,

                    position=position,

                    model_version=(
                        model_version
                    ),
                )

                total_events[
                    "application"
                ] += 1

                # -------------------------------------------------
                # 4. SHORTLIST
                # -------------------------------------------------

                shortlist_probability = (
                    0.20
                )

                shortlisted = (
                    random.random()
                    < shortlist_probability
                )

                if not shortlisted:
                    continue

                log_event(
                    event_type="shortlist",

                    ranking_request_id=(
                        ranking_request_id
                    ),

                    student_id=student_id,

                    job_id=job_id,

                    position=position,

                    model_version=(
                        model_version
                    ),
                )

                total_events[
                    "shortlist"
                ] += 1

        print(
            f"{model_version} traffic generated."
        )

    return total_events


def main():

    print("=" * 60)

    print(
        "PHASE 3 TASK 6 - "
        "GROWTH EVENT GENERATION"
    )

    print("=" * 60)

    totals = generate_events(
        requests_per_model=100
    )

    print("\nEvent Generation Complete")
    print("-" * 40)

    for event_type, count in totals.items():

        print(
            f"{event_type.capitalize():15}: "
            f"{count}"
        )

    print("\nModels covered:")

    for model in MODEL_VERSIONS:

        print(
            f"- {model}"
        )


if __name__ == "__main__":
    main()