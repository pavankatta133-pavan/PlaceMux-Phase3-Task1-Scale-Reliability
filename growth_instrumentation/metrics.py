"""
Phase 3 Task 6
Growth Instrumentation - Metrics Calculator

Calculates:
    - impressions
    - clicks
    - CTR
    - applications
    - application rate
    - shortlists
    - shortlist rate

Metrics are calculated separately for each model version.
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
    "ranking_metrics.json"
)


EVENT_TYPES = [
    "impression",
    "click",
    "application",
    "shortlist",
]


def calculate_percentage(
    numerator,
    denominator
):

    if denominator == 0:
        return 0

    return round(
        (numerator / denominator) * 100,
        2
    )


def calculate_metrics(events):

    model_data = defaultdict(
        lambda: {
            "impressions": 0,
            "clicks": 0,
            "applications": 0,
            "shortlists": 0,
        }
    )

    for event in events:

        model_version = event[
            "model_version"
        ]

        event_type = event[
            "event_type"
        ]

        if event_type in EVENT_TYPES:

            model_data[
                model_version
            ][event_type + "s"] += 1

    results = []

    for model_version in sorted(
        model_data.keys()
    ):

        data = model_data[
            model_version
        ]

        impressions = data[
            "impressions"
        ]

        clicks = data[
            "clicks"
        ]

        applications = data[
            "applications"
        ]

        shortlists = data[
            "shortlists"
        ]

        ctr = calculate_percentage(
            clicks,
            impressions
        )

        application_rate = (
            calculate_percentage(
                applications,
                impressions
            )
        )

        shortlist_rate = (
            calculate_percentage(
                shortlists,
                impressions
            )
        )

        results.append({

            "model_version":
                model_version,

            "impressions":
                impressions,

            "clicks":
                clicks,

            "ctr_percent":
                ctr,

            "applications":
                applications,

            "application_rate_percent":
                application_rate,

            "shortlists":
                shortlists,

            "shortlist_rate_percent":
                shortlist_rate,
        })

    return results


def save_report(results):

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    report = {

        "experiment_id":
            "exp_001",

        "models":
            results,
    }

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
        "GROWTH METRICS"
    )

    print("=" * 60)

    events = read_events()

    print(
        f"\nTotal events analyzed: "
        f"{len(events)}"
    )

    results = calculate_metrics(
        events
    )

    report = save_report(
        results
    )

    print("\nModel Metrics")
    print("-" * 60)

    for model in report[
        "models"
    ]:

        print(
            f"\nModel: "
            f"{model['model_version']}"
        )

        print(
            f"Impressions: "
            f"{model['impressions']}"
        )

        print(
            f"Clicks: "
            f"{model['clicks']}"
        )

        print(
            f"CTR: "
            f"{model['ctr_percent']} %"
        )

        print(
            f"Applications: "
            f"{model['applications']}"
        )

        print(
            f"Application Rate: "
            f"{model['application_rate_percent']} %"
        )

        print(
            f"Shortlists: "
            f"{model['shortlists']}"
        )

        print(
            f"Shortlist Rate: "
            f"{model['shortlist_rate_percent']} %"
        )

    print(
        "\nMetrics report saved to:"
    )

    print(
        REPORT_FILE
    )


if __name__ == "__main__":
    main()