"""
Phase 3 Task 6
Growth Instrumentation - Position Analysis

Analyzes:
    - impressions by ranking position
    - clicks by ranking position
    - CTR by position
    - model version coverage
    - invalid position records
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
    "position_analysis.json"
)


def percentage(
    numerator,
    denominator
):

    if denominator == 0:
        return 0

    return round(
        (numerator / denominator) * 100,
        2
    )


def analyze_positions(events):

    position_data = defaultdict(
        lambda: {
            "impressions": 0,
            "clicks": 0,
            "applications": 0,
            "shortlists": 0,
            "models": set(),
        }
    )

    invalid_positions = []

    missing_model_versions = []

    for event in events:

        event_type = event.get(
            "event_type"
        )

        position = event.get(
            "position"
        )

        model_version = event.get(
            "model_version"
        )

        # Validate position
        if (
            not isinstance(
                position,
                int
            )
            or position < 1
        ):

            invalid_positions.append(
                {
                    "event_id":
                        event.get(
                            "event_id"
                        ),

                    "position":
                        position,
                }
            )

            continue

        # Validate model version
        if not model_version:

            missing_model_versions.append(
                event.get(
                    "event_id"
                )
            )

            continue

        key = (
            model_version,
            position
        )

        position_data[
            key
        ]["models"].add(
            model_version
        )

        if event_type == "impression":

            position_data[
                key
            ]["impressions"] += 1

        elif event_type == "click":

            position_data[
                key
            ]["clicks"] += 1

        elif event_type == "application":

            position_data[
                key
            ]["applications"] += 1

        elif event_type == "shortlist":

            position_data[
                key
            ]["shortlists"] += 1

    results = []

    for (
        model_version,
        position
    ), data in sorted(
        position_data.items()
    ):

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

        results.append({

            "model_version":
                model_version,

            "position":
                position,

            "impressions":
                impressions,

            "clicks":
                clicks,

            "ctr_percent":
                percentage(
                    clicks,
                    impressions
                ),

            "applications":
                applications,

            "application_rate_percent":
                percentage(
                    applications,
                    impressions
                ),

            "shortlists":
                shortlists,

            "shortlist_rate_percent":
                percentage(
                    shortlists,
                    impressions
                ),
        })

    models = sorted(
        {
            event.get(
                "model_version"
            )
            for event in events
            if event.get(
                "model_version"
            )
        }
    )

    positions = sorted(
        {
            event.get(
                "position"
            )
            for event in events
            if isinstance(
                event.get(
                    "position"
                ),
                int
            )
        }
    )

    return {

        "analysis":
            "Ranking Position Analysis",

        "total_events":
            len(events),

        "models_found":
            models,

        "positions_found":
            positions,

        "position_metrics":
            results,

        "invalid_positions":
            invalid_positions,

        "missing_model_versions":
            missing_model_versions,

        "position_logging_complete":
            (
                len(invalid_positions)
                == 0
            ),

        "model_version_logging_complete":
            (
                len(
                    missing_model_versions
                )
                == 0
            ),

        "overall_success":
            (
                len(events) > 0
                and
                len(invalid_positions) == 0
                and
                len(
                    missing_model_versions
                ) == 0
                and
                len(models) >= 2
            ),
    }


def main():

    print("=" * 60)

    print(
        "PHASE 3 TASK 6 - "
        "POSITION-LEVEL ANALYSIS"
    )

    print("=" * 60)

    events = read_events()

    report = analyze_positions(
        events
    )

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

    print(
        f"\nTotal events: "
        f"{report['total_events']}"
    )

    print(
        "\nModels found:"
    )

    for model in report[
        "models_found"
    ]:

        print(
            f"- {model}"
        )

    print(
        "\nPositions found:"
    )

    for position in report[
        "positions_found"
    ]:

        print(
            f"- Position {position}"
        )

    print(
        "\nInvalid positions: "
        f"{len(report['invalid_positions'])}"
    )

    print(
        "Missing model versions: "
        f"{len(report['missing_model_versions'])}"
    )

    print(
        "\nPosition logging: "
        f"{'PASS' if report['position_logging_complete'] else 'FAIL'}"
    )

    print(
        "Model-version logging: "
        f"{'PASS' if report['model_version_logging_complete'] else 'FAIL'}"
    )

    print(
        "\nOverall analysis: "
        f"{'PASS' if report['overall_success'] else 'FAIL'}"
    )

    print(
        "\nReport saved to:"
    )

    print(
        REPORT_FILE
    )


if __name__ == "__main__":
    main()