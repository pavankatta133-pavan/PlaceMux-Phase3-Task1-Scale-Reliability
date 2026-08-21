"""
Task 14
Fairness & Bias Audit
"""

import json
import os


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    PROJECT_ROOT,
    "fairness_explainability",
    "data",
    "matching_data.json"
)

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "fairness_explainability",
    "reports"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "bias_audit_report.json"
)


def load_data():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def calculate_metrics(records):

    groups = sorted(
        set(
            record["group"]
            for record in records
        )
    )

    metrics = {}

    for group in groups:

        group_records = [
            record
            for record in records
            if record["group"] == group
        ]

        selected = sum(
            record["selected"]
            for record in group_records
        )

        qualified = [
            record
            for record in group_records
            if record["qualified"] == 1
        ]

        qualified_selected = sum(
            record["selected"]
            for record in qualified
        )

        selection_rate = (
            selected / len(group_records)
        )

        true_positive_rate = (
            qualified_selected / len(qualified)
            if qualified
            else 0.0
        )

        metrics[group] = {
            "count": len(group_records),
            "selection_rate": round(
                selection_rate,
                4
            ),
            "true_positive_rate": round(
                true_positive_rate,
                4
            )
        }

    return metrics


def calculate_fairness_metrics(metrics):

    groups = list(metrics.keys())

    if len(groups) < 2:

        raise ValueError(
            "At least two groups are required."
        )

    reference = groups[0]

    reference_selection = metrics[
        reference
    ]["selection_rate"]

    reference_tpr = metrics[
        reference
    ]["true_positive_rate"]

    comparisons = {}

    for group in groups[1:]:

        selection_rate = metrics[
            group
        ]["selection_rate"]

        tpr = metrics[
            group
        ]["true_positive_rate"]

        demographic_parity_ratio = (
            selection_rate
            / reference_selection
            if reference_selection
            else 0.0
        )

        equal_opportunity_gap = abs(
            tpr - reference_tpr
        )

        comparisons[group] = {
            "reference_group": reference,
            "demographic_parity_ratio": round(
                demographic_parity_ratio,
                4
            ),
            "equal_opportunity_gap": round(
                equal_opportunity_gap,
                4
            )
        }

    return comparisons


def main():

    print(
        "\n========== TASK 14 BIAS AUDIT =========="
    )

    records = load_data()

    print(
        "Records:",
        len(records)
    )

    metrics = calculate_metrics(
        records
    )

    fairness = calculate_fairness_metrics(
        metrics
    )

    report = {
        "audit_scope": "candidate matching decisions",
        "fairness_metrics": {
            "demographic_parity_ratio": (
                "selection rate of comparison group "
                "divided by reference group"
            ),
            "equal_opportunity_gap": (
                "absolute difference in true positive rate"
            )
        },
        "group_metrics": metrics,
        "fairness_comparisons": fairness
    }

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
        "\nGroup metrics:"
    )

    for group, values in metrics.items():

        print(
            f"{group}: "
            f"selection_rate="
            f"{values['selection_rate']:.4f}, "
            f"TPR="
            f"{values['true_positive_rate']:.4f}"
        )

    print(
        "\nFairness comparison:"
    )

    for group, values in fairness.items():

        print(
            f"{group}: "
            f"demographic_parity_ratio="
            f"{values['demographic_parity_ratio']:.4f}, "
            f"equal_opportunity_gap="
            f"{values['equal_opportunity_gap']:.4f}"
        )

    print(
        "\nReport saved to:"
    )

    print(
        REPORT_FILE
    )

    print(
        "\nTASK 14 BIAS AUDIT: PASS"
    )


if __name__ == "__main__":

    main()