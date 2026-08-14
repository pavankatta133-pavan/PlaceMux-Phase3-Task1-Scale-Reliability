"""
Phase 3 Task 10
Growth Integration & Experiment Readout

Runs a reproducible A/B experiment using logged growth events.
"""

import json
import os
import random
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

PREREG_FILE = os.path.join(
    PROJECT_ROOT,
    "experimentation",
    "preregistration.json"
)

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "experimentation",
    "reports"
)

EVENT_OUTPUT = os.path.join(
    REPORT_DIR,
    "task10_experiment_events.jsonl"
)


RANDOM_SEED = 42


def load_jsonl(path):

    events = []

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Event file not found: {path}"
        )

    with open(
        path,
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


def load_preregistration():

    with open(
        PREREG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def aggregate_users(events):

    users = defaultdict(
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

        if not student_id:
            continue

        event_type = event.get(
            "event_type"
        )

        if event_type == "impression":

            users[student_id][
                "impressions"
            ] += 1

        elif event_type == "click":

            users[student_id][
                "clicks"
            ] += 1

        elif event_type == "application":

            users[student_id][
                "applications"
            ] += 1

        elif event_type == "shortlist":

            users[student_id][
                "shortlists"
            ] += 1

    return users


def calculate_relevant_actions(
    values
):

    return (
        values["clicks"]
        + values["applications"]
        + values["shortlists"]
    )


def assign_groups(users):

    random.seed(
        RANDOM_SEED
    )

    student_ids = list(
        users.keys()
    )

    random.shuffle(
        student_ids
    )

    midpoint = len(
        student_ids
    ) // 2

    control_ids = set(
        student_ids[:midpoint]
    )

    groups = {}

    for student_id in student_ids:

        if student_id in control_ids:

            groups[student_id] = {
                "group": "control",
                "model_version": "ranker_v1.0"
            }

        else:

            groups[student_id] = {
                "group": "variant",
                "model_version": "ranker_v2.0"
            }

    return groups


def build_experiment_events(
    users,
    groups,
    experiment_id
):

    experiment_events = []

    for student_id, values in users.items():

        assignment = groups[
            student_id
        ]

        impressions = values[
            "impressions"
        ]

        relevant_actions = (
            calculate_relevant_actions(
                values
            )
        )

        experiment_events.append({

            "experiment_id":
                experiment_id,

            "student_id":
                student_id,

            "group":
                assignment["group"],

            "model_version":
                assignment[
                    "model_version"
                ],

            "impressions":
                impressions,

            "relevant_actions":
                relevant_actions

        })

    return experiment_events


def calculate_metrics(
    experiment_events
):

    metrics = {}

    for group in [
        "control",
        "variant"
    ]:

        rows = [
            row
            for row in experiment_events
            if row["group"] == group
        ]

        total_impressions = sum(
            row["impressions"]
            for row in rows
        )

        total_relevant_actions = sum(
            row["relevant_actions"]
            for row in rows
        )

        rate = (
            total_relevant_actions
            / total_impressions
            if total_impressions
            else 0
        )

        metrics[group] = {

            "users":
                len(rows),

            "impressions":
                total_impressions,

            "relevant_actions":
                total_relevant_actions,

            "relevant_action_rate":
                round(
                    rate,
                    4
                )
        }

    return metrics


def save_events(events):

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    with open(
        EVENT_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        for event in events:

            file.write(
                json.dumps(event)
                + "\n"
            )


def main():

    print(
        "\n========== TASK 10 A/B EXPERIMENT =========="
    )

    prereg = load_preregistration()

    print(
        "Experiment:",
        prereg[
            "experiment_id"
        ]
    )

    print(
        "Hypothesis:",
        prereg[
            "hypothesis"
        ]
    )

    print(
        "Primary Metric:",
        prereg[
            "primary_metric"
        ]
    )

    print(
        "\nLoading real logged data..."
    )

    events = load_jsonl(
        EVENT_FILE
    )

    print(
        "Events loaded:",
        len(events)
    )

    users = aggregate_users(
        events
    )

    print(
        "Users available:",
        len(users)
    )

    if len(users) < 2:

        raise ValueError(
            "At least two users are required "
            "for the A/B experiment."
        )

    groups = assign_groups(
        users
    )

    experiment_events = (
        build_experiment_events(
            users,
            groups,
            prereg[
                "experiment_id"
            ]
        )
    )

    save_events(
        experiment_events
    )

    metrics = calculate_metrics(
        experiment_events
    )

    print(
        "\n---------- CONTROL ----------"
    )

    print(
        "Users:",
        metrics[
            "control"
        ]["users"]
    )

    print(
        "Impressions:",
        metrics[
            "control"
        ]["impressions"]
    )

    print(
        "Relevant Actions:",
        metrics[
            "control"
        ]["relevant_actions"]
    )

    print(
        "Relevant Action Rate:",
        metrics[
            "control"
        ]["relevant_action_rate"]
    )

    print(
        "\n---------- VARIANT ----------"
    )

    print(
        "Users:",
        metrics[
            "variant"
        ]["users"]
    )

    print(
        "Impressions:",
        metrics[
            "variant"
        ]["impressions"]
    )

    print(
        "Relevant Actions:",
        metrics[
            "variant"
        ]["relevant_actions"]
    )

    print(
        "Relevant Action Rate:",
        metrics[
            "variant"
        ]["relevant_action_rate"]
    )

    print(
        "\nExperiment events saved to:"
    )

    print(
        EVENT_OUTPUT
    )

    print(
        "\nTASK 10 A/B EXPERIMENT: PASS"
    )


if __name__ == "__main__":

    main()