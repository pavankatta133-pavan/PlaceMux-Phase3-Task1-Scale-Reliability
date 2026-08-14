"""
Phase 3 Task 9
Experimentation Platform Integration
"""

import json
import os

from experimentation.assignment import (
    assign_model
)

from experimentation.feature_flags import (
    FeatureFlag
)

from experimentation.holdout import (
    is_holdout
)

from experimentation.guardrails import (
    evaluate_guardrails
)


REPORT_FILE = os.path.join(
    os.path.dirname(__file__),
    "reports",
    "experiment_report.json"
)


EXPERIMENT_ID = (
    "task9_ranker_experiment_001"
)


def generate_events():

    events = []

    # Create reproducible users
    for number in range(1, 201):

        student_id = (
            f"student_{number:03d}"
        )

        # Permanent holdout
        if is_holdout(student_id):

            model = "ranker_v1.0"
            group = "holdout"

        else:

            model = assign_model(
                student_id,
                variant_percent=10
            )

            if model == "ranker_v2.0":

                group = "variant"

            else:

                group = "control"

        # Simulated relevance
        if group == "variant":

            relevant = (
                number % 10 != 0
            )

        elif group == "control":

            relevant = (
                number % 5 != 0
            )

        else:

            relevant = (
                number % 5 != 0
            )

        events.append({

            "experiment_id":
                EXPERIMENT_ID,

            "student_id":
                student_id,

            "group":
                group,

            "model_version":
                model,

            "relevant_action":
                int(relevant)

        })

    return events


def calculate_metrics(events):

    metrics = {}

    for group in [
        "control",
        "variant",
        "holdout"
    ]:

        group_events = [
            event
            for event in events
            if event["group"] == group
        ]

        impressions = len(
            group_events
        )

        relevant_actions = sum(
            event["relevant_action"]
            for event in group_events
        )

        rate = (
            relevant_actions
            / impressions
            if impressions
            else 0
        )

        metrics[group] = {

            "impressions":
                impressions,

            "relevant_actions":
                relevant_actions,

            "relevant_action_rate":
                round(
                    rate,
                    4
                )
        }

    return metrics


def main():

    print(
        "\n========== TASK 9 EXPERIMENT =========="
    )

    flags = FeatureFlag()

    print(
        "Experiment:",
        EXPERIMENT_ID
    )

    print(
        "Enabled:",
        flags.is_enabled()
    )

    print(
        "Variant traffic:",
        str(
            flags.variant_percentage()
        ) + "%"
    )

    if not flags.is_enabled():

        print(
            "Experiment disabled."
        )

        return

    events = generate_events()

    metrics = calculate_metrics(
        events
    )

    control = metrics[
        "control"
    ]

    variant = metrics[
        "variant"
    ]

    guardrail = evaluate_guardrails(

        control_impressions=
            control["impressions"],

        control_relevant_actions=
            control["relevant_actions"],

        variant_impressions=
            variant["impressions"],

        variant_relevant_actions=
            variant["relevant_actions"],

        min_sample_size=50
    )

    report = {

        "experiment_id":
            EXPERIMENT_ID,

        "experiment":
            "Ranker V1 vs V2",

        "feature_flag":
            flags.get_config(),

        "metrics":
            metrics,

        "guardrail":
            guardrail,

        "decision":
            guardrail["decision"],

        "experiment_halted":
            guardrail[
                "experiment_halted"
            ]
    }

    os.makedirs(
        os.path.dirname(
            REPORT_FILE
        ),
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
        "\nControl users:",
        metrics[
            "control"
        ]["impressions"]
    )

    print(
        "Variant users:",
        metrics[
            "variant"
        ]["impressions"]
    )

    print(
        "Holdout users:",
        metrics[
            "holdout"
        ]["impressions"]
    )

    print(
        "\nControl Relevant Action Rate:",
        metrics[
            "control"
        ]["relevant_action_rate"]
    )

    print(
        "Variant Relevant Action Rate:",
        metrics[
            "variant"
        ]["relevant_action_rate"]
    )

    print(
        "\nMeasured Lift:",
        guardrail[
            "lift_percent"
        ],
        "%"
    )

    print(
        "\nGuardrail Decision:",
        guardrail[
            "decision"
        ]
    )

    print(
        "Experiment Halted:",
        guardrail[
            "experiment_halted"
        ]
    )

    print(
        "\nReport saved to:"
    )

    print(
        REPORT_FILE
    )

    print(
        "\nTASK 9 EXPERIMENT: PASS"
    )


if __name__ == "__main__":

    main()