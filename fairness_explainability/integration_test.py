"""
Task 14
End-to-End Integration Test
"""

import json
import os
import urllib.request

from fairness_explainability.bias_audit import (
    load_data,
    calculate_metrics,
    calculate_fairness_metrics
)

from fairness_explainability.mitigation import (
    apply_mitigation
)


BASE_URL = "http://127.0.0.1:8001"


def test_api():

    payload = json.dumps({
        "candidate_id": "candidate_001"
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{BASE_URL}/explain",
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=10
    ) as response:

        result = json.loads(
            response.read().decode("utf-8")
        )

    if not result.get("explanation"):
        raise RuntimeError(
            "Explanation was not returned."
        )

    return result


def main():

    print(
        "\n========== TASK 14 INTEGRATION TEST =========="
    )

    records = load_data()

    before_metrics = calculate_metrics(
        records
    )

    before_fairness = calculate_fairness_metrics(
        before_metrics
    )

    mitigated = apply_mitigation(
        records
    )

    after_metrics = {}

    groups = sorted(
        set(
            record["group"]
            for record in mitigated
        )
    )

    for group in groups:

        group_records = [
            record
            for record in mitigated
            if record["group"] == group
        ]

        selected = sum(
            record["selected_after_mitigation"]
            for record in group_records
        )

        qualified = [
            record
            for record in group_records
            if record["qualified"] == 1
        ]

        qualified_selected = sum(
            record["selected_after_mitigation"]
            for record in qualified
        )

        after_metrics[group] = {
            "selection_rate":
                selected / len(group_records),
            "true_positive_rate":
                qualified_selected / len(qualified)
        }

    print(
        "\nBefore mitigation:"
    )

    print(
        json.dumps(
            before_fairness,
            indent=2
        )
    )

    print(
        "\nAfter mitigation:"
    )

    print(
        json.dumps(
            after_metrics,
            indent=2
        )
    )

    result = test_api()

    print(
        "\nAPI explanation:"
    )

    print(
        result["explanation"]
    )

    if (
        after_metrics["A"]["selection_rate"]
        != after_metrics["B"]["selection_rate"]
    ):

        raise RuntimeError(
            "Selection rates are not balanced."
        )

    if (
        after_metrics["A"]["true_positive_rate"]
        != after_metrics["B"]["true_positive_rate"]
    ):

        raise RuntimeError(
            "True positive rates are not balanced."
        )

    print(
        "\nBefore/after fairness comparison: PASS"
    )

    print(
        "Per-decision explanation API: PASS"
    )

    print(
        "\nTASK 14 INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":

    main()