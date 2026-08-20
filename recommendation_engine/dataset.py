"""
Phase 3 Task 12
Personalization & Recommendation Engine
Build Recommendation Dataset
"""

import json
import os
from collections import defaultdict


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

EVENT_FILE = os.path.join(
    PROJECT_ROOT,
    "growth_instrumentation",
    "data",
    "growth_events.jsonl"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "recommendation_engine",
    "reports",
    "recommendation_dataset.json"
)


SUPPORTED_EVENTS = {
    "impression",
    "click",
    "application",
    "shortlist"
}


def load_events():
    """Load events from growth instrumentation."""

    events = []

    if not os.path.exists(EVENT_FILE):
        print("ERROR: Event file not found:")
        print(EVENT_FILE)
        return events

    with open(
        EVENT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            try:
                event = json.loads(line)
                events.append(event)

            except json.JSONDecodeError:
                continue

    return events


def build_dataset(events):
    """
    Build student-job interaction records.

    Each record represents the interaction between
    one student and one job.
    """

    interactions = defaultdict(
        lambda: {
            "impressions": 0,
            "clicks": 0,
            "applications": 0,
            "shortlists": 0
        }
    )

    for event in events:

        student_id = event.get(
            "student_id"
        )

        job_id = (
            event.get("job_id")
            or event.get("item_id")
            or event.get("listing_id")
            or event.get("content_id")
        )

        event_type = event.get(
            "event_type"
        )

        if not student_id:
            continue

        if not job_id:
            continue

        if event_type not in SUPPORTED_EVENTS:
            continue

        key = (
            str(student_id),
            str(job_id)
        )

        interactions[key][
            f"{event_type}s"
            if event_type != "impression"
            else "impressions"
        ] += 1

    dataset = []

    for (
        (student_id, job_id),
        values
    ) in interactions.items():

        impressions = values[
            "impressions"
        ]

        clicks = values[
            "clicks"
        ]

        applications = values[
            "applications"
        ]

        shortlists = values[
            "shortlists"
        ]

        engagement_score = (
            clicks
            + (applications * 3)
            + (shortlists * 4)
        )

        interaction_strength = (
            1 if clicks > 0 else 0
        )

        if applications > 0:
            interaction_strength = 2

        if shortlists > 0:
            interaction_strength = 3

        ctr = (
            clicks / impressions
            if impressions
            else 0
        )

        dataset.append({

            "student_id":
                student_id,

            "job_id":
                job_id,

            "impressions":
                impressions,

            "clicks":
                clicks,

            "applications":
                applications,

            "shortlists":
                shortlists,

            "ctr":
                round(
                    ctr,
                    4
                ),

            "engagement_score":
                engagement_score,

            "interaction_strength":
                interaction_strength
        })

    return dataset


def main():

    print(
        "\n========== TASK 12 DATASET =========="
    )

    events = load_events()

    print(
        "Events loaded:",
        len(events)
    )

    dataset = build_dataset(
        events
    )

    students = sorted(
        set(
            record["student_id"]
            for record in dataset
        )
    )

    jobs = sorted(
        set(
            record["job_id"]
            for record in dataset
        )
    )

    print(
        "Interaction records:",
        len(dataset)
    )

    print(
        "Students:",
        len(students)
    )

    print(
        "Jobs:",
        len(jobs)
    )

    os.makedirs(
        os.path.dirname(
            OUTPUT_FILE
        ),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            dataset,
            file,
            indent=2
        )

    print(
        "\nDataset saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nTASK 12 DATASET: PASS"
    )


if __name__ == "__main__":
    main()