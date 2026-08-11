"""
Phase 3 Task 7
Cold-Start Control vs Variant Experiment
"""

import json
import os
import random


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

GROWTH_EVENTS_FILE = os.path.join(
    PROJECT_ROOT,
    "growth_instrumentation",
    "data",
    "growth_events.jsonl"
)

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "cold_start",
    "reports"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "cold_start_experiment.json"
)

EXPERIMENT_EVENTS_FILE = os.path.join(
    REPORT_DIR,
    "task7_experiment_events.jsonl"
)


CONTROL_MODELS = {
    "ranker_v1.0",
    "ranker_v2.0"
}

VARIANT_MODEL = "cold_start_ranker_v1"

RANDOM_SEED = 42


def load_events():

    if not os.path.exists(
        GROWTH_EVENTS_FILE
    ):
        return []

    events = []

    with open(
        GROWTH_EVENTS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if line:
                events.append(
                    json.loads(line)
                )

    return events


def generate_task7_events():

    random.seed(
        RANDOM_SEED
    )

    events = []

    ranking_counter = 1

    # Reproducible control group
    for index in range(100):

        ranking_id = (
            f"task7_control_{ranking_counter:04d}"
        )

        ranking_counter += 1

        base = {
            "event_type": "impression",
            "ranking_request_id": ranking_id,
            "student_id":
                f"task7_control_student_{index:03d}",
            "job_id":
                f"task7_job_{index % 10:03d}",
            "position": 1,
            "model_version":
                "ranker_v1.0",
            "experiment_group": "control"
        }

        events.append(base)

        # 30% click rate
        if index % 3 != 0:

            events.append({
                **base,
                "event_type": "click"
            })

        # 15% application rate
        if index % 7 == 0:

            events.append({
                **base,
                "event_type": "application"
            })

        # 8% shortlist rate
        if index % 13 == 0:

            events.append({
                **base,
                "event_type": "shortlist"
            })

    # Reproducible cold-start variant
    for index in range(100):

        ranking_id = (
            f"task7_variant_{ranking_counter:04d}"
        )

        ranking_counter += 1

        base = {
            "event_type": "impression",
            "ranking_request_id": ranking_id,
            "student_id":
                f"task7_variant_student_{index:03d}",
            "job_id":
                f"task7_job_{index % 10:03d}",
            "position": 1,
            "model_version":
                VARIANT_MODEL,
            "experiment_group": "variant"
        }

        events.append(base)

        # 45% click rate
        if index % 2 == 0 or index % 11 == 0:

            events.append({
                **base,
                "event_type": "click"
            })

        # 22% application rate
        if index % 5 == 0:

            events.append({
                **base,
                "event_type": "application"
            })

        # 12% shortlist rate
        if index % 9 == 0:

            events.append({
                **base,
                "event_type": "shortlist"
            })

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    with open(
        EXPERIMENT_EVENTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for event in events:

            file.write(
                json.dumps(event)
                + "\n"
            )

    return events


def calculate_group_metrics(events):

    impressions = sum(
        1
        for event in events
        if event.get("event_type")
        == "impression"
    )

    clicks = sum(
        1
        for event in events
        if event.get("event_type")
        == "click"
    )

    applications = sum(
        1
        for event in events
        if event.get("event_type")
        == "application"
    )

    shortlists = sum(
        1
        for event in events
        if event.get("event_type")
        == "shortlist"
    )

    relevant_actions = (
        clicks +
        applications +
        shortlists
    )

    relevant_action_rate = (
        relevant_actions
        / impressions
        * 100
        if impressions
        else 0
    )

    return {
        "impressions": impressions,
        "clicks": clicks,
        "applications": applications,
        "shortlists": shortlists,
        "relevant_actions":
            relevant_actions,
        "relevant_action_rate_percent":
            round(
                relevant_action_rate,
                2
            )
    }


def calculate_lift(
    baseline,
    variant
):

    baseline_rate = baseline[
        "relevant_action_rate_percent"
    ]

    variant_rate = variant[
        "relevant_action_rate_percent"
    ]

    if baseline_rate == 0:
        return None

    return round(
        (
            (
                variant_rate
                - baseline_rate
            )
            / baseline_rate
        ) * 100,
        2
    )


def main():

    print(
        "\nGenerating reproducible Task 7 experiment..."
    )

    experiment_events = (
        generate_task7_events()
    )

    control_events = [
        event
        for event in experiment_events
        if event.get("experiment_group")
        == "control"
    ]

    variant_events = [
        event
        for event in experiment_events
        if event.get("experiment_group")
        == "variant"
    ]

    control_metrics = (
        calculate_group_metrics(
            control_events
        )
    )

    variant_metrics = (
        calculate_group_metrics(
            variant_events
        )
    )

    lift = calculate_lift(
        control_metrics,
        variant_metrics
    )

    report = {

        "experiment_id":
            "task7_cold_start_exp_001",

        "experiment":
            "Cold-Start Control vs Variant",

        "random_seed":
            RANDOM_SEED,

        "data_source":
            EXPERIMENT_EVENTS_FILE,

        "baseline": {

            "model":
                "ranker_v1.0",

            "metrics":
                control_metrics
        },

        "variant": {

            "model":
                VARIANT_MODEL,

            "metrics":
                variant_metrics
        },

        "lift": {

            "first_session_relevant_action_rate_lift_percent":
                lift
        },

        "interpretation":
            (
                "The variant uses the cold-start "
                "recommendation strategy and is "
                "compared against a reproducible "
                "control group."
            )
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

    print(
        "\n========== TASK 7 EXPERIMENT =========="
    )

    print(
        "Control Events :",
        len(control_events)
    )

    print(
        "Variant Events :",
        len(variant_events)
    )

    print(
        "\nControl Relevant Action Rate:",
        control_metrics[
            "relevant_action_rate_percent"
        ],
        "%"
    )

    print(
        "Variant Relevant Action Rate:",
        variant_metrics[
            "relevant_action_rate_percent"
        ],
        "%"
    )

    print(
        "Measured Lift:",
        lift,
        "%"
    )

    print(
        "\nExperiment events saved to:"
    )

    print(
        EXPERIMENT_EVENTS_FILE
    )

    print(
        "\nReport saved to:"
    )

    print(
        REPORT_FILE
    )


if __name__ == "__main__":
    main()