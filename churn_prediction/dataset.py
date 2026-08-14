"""
Phase 3 Task 8
Build Churn Dataset
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
    "churn_prediction",
    "reports",
    "churn_dataset.json"
)


def load_events():

    events = []

    if not os.path.exists(EVENT_FILE):
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
                events.append(
                    json.loads(line)
                )

            except json.JSONDecodeError:
                continue

    return events


def build_dataset(events):

    users = defaultdict(
        lambda: {
            "impressions": 0,
            "clicks": 0,
            "applications": 0,
            "shortlists": 0
        }
    )


    # -----------------------------------------
    # Aggregate events for each student
    # -----------------------------------------

    for event in events:

        user = event.get(
            "student_id"
        )

        if not user:
            continue


        event_type = event.get(
            "event_type"
        )


        if event_type == "impression":

            users[user][
                "impressions"
            ] += 1


        elif event_type == "click":

            users[user][
                "clicks"
            ] += 1


        elif event_type == "application":

            users[user][
                "applications"
            ] += 1


        elif event_type == "shortlist":

            users[user][
                "shortlists"
            ] += 1


    dataset = []


    # -----------------------------------------
    # Create user-level features
    # -----------------------------------------

    for user, values in users.items():

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


        # -----------------------------------------
        # Engagement metrics
        # -----------------------------------------

        ctr = (
            clicks / impressions
            if impressions > 0
            else 0
        )


        application_rate = (
            applications / impressions
            if impressions > 0
            else 0
        )


        shortlist_rate = (
            shortlists / impressions
            if impressions > 0
            else 0
        )


        # -----------------------------------------
        # Engagement score
        #
        # Click       = 1 point
        # Application = 3 points
        # Shortlist   = 4 points
        # -----------------------------------------

        engagement_score = (
            clicks
            + (applications * 3)
            + (shortlists * 4)
        )


        # -----------------------------------------
        # Churn / disengagement proxy
        #
        # This is an observed engagement proxy,
        # NOT confirmed real-world churn.
        #
        # Users with very low engagement are
        # classified as at-risk.
        # -----------------------------------------

        if engagement_score <= 60:

            churn_label = 1

        else:

            churn_label = 0


        dataset.append({

            "student_id":
                user,

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

            "engagement_score":
                engagement_score,

            "churn_label":
                churn_label
        })


    return dataset


def main():

    events = load_events()


    dataset = build_dataset(
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


    # -----------------------------------------
    # Dataset statistics
    # -----------------------------------------

    churn_count = sum(
        record["churn_label"]
        for record in dataset
    )


    non_churn_count = (
        len(dataset)
        - churn_count
    )


    print(
        "\n========== TASK 8 DATASET =========="
    )


    print(
        "Events loaded:",
        len(events)
    )


    print(
        "Users:",
        len(dataset)
    )


    print(
        "Churn / At-risk:",
        churn_count
    )


    print(
        "Engaged:",
        non_churn_count
    )


    print(
        "\nDataset saved to:"
    )


    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":

    main()