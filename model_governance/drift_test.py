"""
Task 15
Controlled Drift Test
"""

import json
import os

from model_governance.drift_monitor import (
    calculate_statistics,
    calculate_drift,
    BASELINE,
    DRIFT_THRESHOLDS
)


def main():

    print(
        "\n========== TASK 15 CONTROLLED DRIFT TEST =========="
    )

    # Simulated production data with intentional drift.
    # This does NOT modify the real dataset.

    drifted_records = []

    for index in range(12):

        drifted_records.append({
            "id": f"drift_doc_{index}",
            "text": (
                "This is intentionally long production "
                "content used to simulate a significant "
                "distribution change for drift monitoring. "
                "Additional text is included so that the "
                "average document length changes substantially."
            )
        })

    current = calculate_statistics(
        drifted_records
    )

    drift_detected, features = calculate_drift(
        BASELINE,
        current
    )

    print(
        "Baseline statistics:"
    )

    print(
        BASELINE
    )

    print(
        "\nDrifted statistics:"
    )

    print(
        current
    )

    print(
        "\nFeature drift results:"
    )

    print(
        json.dumps(
            features,
            indent=2
        )
    )

    print(
        "\nDrift detected:",
        drift_detected
    )

    if not drift_detected:

        raise RuntimeError(
            "Controlled drift was not detected."
        )

    print(
        "\nControlled drift detection: PASS"
    )

    print(
        "Retraining trigger condition: PASS"
    )

    print(
        "\nTASK 15 CONTROLLED DRIFT TEST: PASS"
    )


if __name__ == "__main__":

    main()