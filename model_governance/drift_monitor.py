"""
Task 15
Drift Detection Monitor
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
    "semantic_search",
    "data",
    "search_documents.json"
)

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "model_governance",
    "reports"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "drift_report.json"
)


# Expected baseline statistics for the monitored
# intelligence-layer data.
BASELINE = {
    "document_count": 6,
    "average_text_length": 300.0
}


DRIFT_THRESHOLDS = {
    "document_count": 0.20,
    "average_text_length": 0.20
}


def load_data():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def calculate_statistics(records):

    if not records:
        raise ValueError(
            "No records available for drift monitoring."
        )

    text_lengths = []

    for record in records:

        text = str(
            record.get(
                "text",
                ""
            )
        )

        text_lengths.append(
            len(text)
        )

    return {
        "document_count": len(records),
        "average_text_length": round(
            sum(text_lengths) / len(text_lengths),
            4
        )
    }


def calculate_drift(
    baseline,
    current
):

    feature_results = {}

    drift_detected = False

    for feature in baseline:

        baseline_value = baseline[feature]
        current_value = current[feature]

        if baseline_value == 0:

            change_ratio = 0.0

        else:

            change_ratio = abs(
                current_value - baseline_value
            ) / baseline_value

        threshold = DRIFT_THRESHOLDS[
            feature
        ]

        feature_drift = (
            change_ratio > threshold
        )

        if feature_drift:
            drift_detected = True

        feature_results[feature] = {
            "baseline": baseline_value,
            "current": current_value,
            "change_ratio": round(
                change_ratio,
                4
            ),
            "threshold": threshold,
            "drift_detected": feature_drift
        }

    return (
        drift_detected,
        feature_results
    )


def monitor_drift():

    records = load_data()

    current = calculate_statistics(
        records
    )

    drift_detected, features = (
        calculate_drift(
            BASELINE,
            current
        )
    )

    report = {
        "baseline": BASELINE,
        "current": current,
        "features": features,
        "drift_detected": drift_detected,
        "retraining_trigger": drift_detected
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

    return report


def main():

    print(
        "\n========== TASK 15 DRIFT MONITORING =========="
    )

    report = monitor_drift()

    print(
        "Features monitored:",
        len(report["features"])
    )

    print(
        "Drift detected:",
        report["drift_detected"]
    )

    print(
        "Retraining trigger:",
        report["retraining_trigger"]
    )

    print(
        "\nReport saved to:"
    )

    print(
        REPORT_FILE
    )

    print(
        "\nTASK 15 DRIFT MONITORING: PASS"
    )


if __name__ == "__main__":

    main()