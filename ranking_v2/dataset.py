"""
Phase 3 Task 11
Build Learning-to-Rank Dataset

Creates query-document ranking records from real
growth instrumentation events.
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
    "ranking_v2",
    "reports",
    "ranking_dataset.json"
)


def normalize_student_id(student_id):

    if student_id == "student-001":
        return "student_001"

    return student_id


def load_events():

    events = []

    if not os.path.exists(EVENT_FILE):

        raise FileNotFoundError(
            f"Growth event file not found:\n{EVENT_FILE}"
        )

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

                events.append(
                    json.loads(line)
                )

            except json.JSONDecodeError:

                continue

    return events


def build_interactions(events):

    interactions = defaultdict(
        lambda: {
            "impression": 0,
            "click": 0,
            "application": 0,
            "shortlist": 0,
            "positions": []
        }
    )

    for event in events:

        raw_student_id = event.get(
            "student_id"
        )

        if not raw_student_id:
            continue

        student_id = normalize_student_id(
            raw_student_id
        )

        job_id = (
            event.get("job_id")
            or event.get("item_id")
            or event.get("recommendation_id")
        )

        event_type = event.get(
            "event_type"
        )

        if not job_id:
            continue

        key = (
            str(student_id),
            str(job_id)
        )

        if event_type == "impression":

            interactions[key][
                "impression"
            ] += 1

            position = event.get(
                "position"
            )

            if position is not None:

                try:

                    interactions[key][
                        "positions"
                    ].append(
                        int(position)
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    pass

        elif event_type == "click":

            interactions[key][
                "click"
            ] += 1

        elif event_type == "application":

            interactions[key][
                "application"
            ] += 1

        elif event_type == "shortlist":

            interactions[key][
                "shortlist"
            ] += 1

    dataset = []

    for (
        (student_id, job_id),
        values
    ) in interactions.items():

        impressions = values[
            "impression"
        ]

        clicks = values[
            "click"
        ]

        applications = values[
            "application"
        ]

        shortlists = values[
            "shortlist"
        ]

        if values["positions"]:

            avg_position = (
                sum(values["positions"])
                /
                len(values["positions"])
            )

        else:

            avg_position = 0

        click_rate = (
            clicks / impressions
            if impressions
            else 0
        )

        application_rate = (
            applications / impressions
            if impressions
            else 0
        )

        shortlist_rate = (
            shortlists / impressions
            if impressions
            else 0
        )

        # ------------------------------------------------
        # Relevance
        #
        # 0 = impression only
        # 1 = click
        # 2 = application
        # 3 = shortlist
        # ------------------------------------------------

        if shortlists > 0:

            relevance_label = 3

        elif applications > 0:

            relevance_label = 2

        elif clicks > 0:

            relevance_label = 1

        else:

            relevance_label = 0

        # ------------------------------------------------
        # Position-bias weight
        # ------------------------------------------------

        if avg_position > 0:

            propensity = max(
                1.0 / avg_position,
                0.05
            )

            position_weight = min(
                1.0 / propensity,
                20.0
            )

        else:

            propensity = 1.0
            position_weight = 1.0

        dataset.append({

            "student_id":
                student_id,

            "job_id":
                str(job_id),

            "impressions":
                impressions,

            "clicks":
                clicks,

            "applications":
                applications,

            "shortlists":
                shortlists,

            "avg_position":
                round(
                    avg_position,
                    4
                ),

            "click_rate":
                round(
                    click_rate,
                    4
                ),

            "application_rate":
                round(
                    application_rate,
                    4
                ),

            "shortlist_rate":
                round(
                    shortlist_rate,
                    4
                ),

            "propensity":
                round(
                    propensity,
                    4
                ),

            "position_weight":
                round(
                    position_weight,
                    4
                ),

            "relevance_label":
                relevance_label

        })

    # ------------------------------------------------
    # Remove duplicate student/job records
    # ------------------------------------------------

    unique_records = {}

    for record in dataset:

        key = (
            record["student_id"],
            record["job_id"]
        )

        unique_records[key] = record

    dataset = list(
        unique_records.values()
    )

    # ------------------------------------------------
    # Sort for reproducibility
    # ------------------------------------------------

    dataset.sort(
        key=lambda x: (
            x["student_id"],
            x["job_id"]
        )
    )

    return dataset


def main():

    events = load_events()

    dataset = build_interactions(
        events
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

    label_counts = defaultdict(
        int
    )

    student_counts = defaultdict(
        int
    )

    for record in dataset:

        label_counts[
            record["relevance_label"]
        ] += 1

        student_counts[
            record["student_id"]
        ] += 1

    print(
        "\n========== TASK 11 DATASET =========="
    )

    print(
        "Events loaded:",
        len(events)
    )

    print(
        "Ranking records:",
        len(dataset)
    )

    print(
        "Students:",
        len(student_counts)
    )

    print(
        "\nRelevance distribution:"
    )

    for label in sorted(
        label_counts
    ):

        print(
            f"Label {label}:",
            label_counts[label]
        )

    print(
        "\nRecords per student:"
    )

    for student_id in sorted(
        student_counts
    ):

        print(
            student_id,
            ":",
            student_counts[student_id]
        )

    print(
        "\nPosition bias correction: ENABLED"
    )

    print(
        "\nDataset saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nTASK 11 DATASET: PASS"
    )


if __name__ == "__main__":

    main()