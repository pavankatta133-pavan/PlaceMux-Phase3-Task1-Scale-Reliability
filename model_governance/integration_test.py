"""
Task 15
End-to-End Model Governance Integration Test
"""

from pathlib import Path
import json

from model_governance.registry.registry import (
    get_active_model,
    register_model,
    promote_model,
    rollback_model
)

from model_governance.drift_monitor import (
    BASELINE,
    calculate_statistics,
    calculate_drift
)

from model_governance.retraining import (
    evaluation_gate
)


PROJECT_ROOT = Path(__file__).resolve().parent

MODEL_CARD = PROJECT_ROOT / "model_card.md"

REGISTRY_FILE = (
    PROJECT_ROOT
    / "registry"
    / "model_registry.json"
)


def test_model_registry():

    active = get_active_model()

    if not active:
        raise RuntimeError(
            "No active model found."
        )

    if "version" not in active:
        raise RuntimeError(
            "Active model has no version."
        )

    if "metrics" not in active:
        raise RuntimeError(
            "Active model has no metrics."
        )

    if "lineage" not in active:
        raise RuntimeError(
            "Active model has no lineage."
        )

    print(
        "Model registry: PASS"
    )

    return active


def test_drift_detection():

    drifted_records = []

    for index in range(12):

        drifted_records.append({
            "id": f"integration_drift_{index}",
            "text": (
                "This intentionally long record "
                "simulates production distribution "
                "change for the governance test."
            )
        })

    current = calculate_statistics(
        drifted_records
    )

    drift_detected, features = calculate_drift(
        BASELINE,
        current
    )

    if not drift_detected:

        raise RuntimeError(
            "Controlled drift was not detected."
        )

    print(
        "Drift detection: PASS"
    )

    return features


def test_evaluation_gate(active_model):

    candidate_metrics = {
        "precision": 0.90,
        "recall": 0.88,
        "f1": 0.89
    }

    passed = evaluation_gate(
        active_model["metrics"],
        candidate_metrics
    )

    if not passed:

        raise RuntimeError(
            "Good candidate failed evaluation gate."
        )

    bad_candidate = {
        "precision": 0.50,
        "recall": 0.45,
        "f1": 0.47
    }

    rejected = evaluation_gate(
        active_model["metrics"],
        bad_candidate
    )

    if rejected:

        raise RuntimeError(
            "Bad candidate passed evaluation gate."
        )

    print(
        "Evaluation gate: PASS"
    )


def test_model_card():

    if not MODEL_CARD.exists():

        raise RuntimeError(
            "Model card does not exist."
        )

    if MODEL_CARD.stat().st_size == 0:

        raise RuntimeError(
            "Model card is empty."
        )

    content = MODEL_CARD.read_text(
        encoding="utf-8"
    )

    required_sections = [
        "Model Overview",
        "Intended Use",
        "Data",
        "Model Metrics",
        "Model Versioning and Lineage",
        "Drift Monitoring",
        "Retraining and Evaluation Gate",
        "Fairness",
        "Explainability",
        "Limitations",
        "Monitoring and Governance"
    ]

    for section in required_sections:

        if section not in content:

            raise RuntimeError(
                f"Model card missing section: {section}"
            )

    print(
        "Model card: PASS"
    )


def test_rollback(active_model):

    original_version = active_model["version"]

    test_version = "model_integration_test"

    registry = json.loads(
        REGISTRY_FILE.read_text(
            encoding="utf-8"
        )
    )

    if test_version not in registry["models"]:

        register_model(
            version=test_version,
            metrics={
                "precision": 0.91,
                "recall": 0.89,
                "f1": 0.90
            },
            parent=original_version,
            training_data="integration_test_data"
        )

    promote_model(
        test_version
    )

    promoted = get_active_model()

    if promoted["version"] != test_version:

        raise RuntimeError(
            "Temporary promotion failed."
        )

    rollback_model(
        original_version
    )

    restored = get_active_model()

    if restored["version"] != original_version:

        raise RuntimeError(
            "Rollback failed."
        )

    print(
        "Rollback: PASS"
    )


def main():

    print(
        "\n========== TASK 15 INTEGRATION TEST =========="
    )

    active_model = test_model_registry()

    test_drift_detection()

    test_evaluation_gate(
        active_model
    )

    test_model_card()

    test_rollback(
        active_model
    )

    # Final verification after rollback.
    final_model = get_active_model()

    if final_model["version"] != active_model["version"]:

        raise RuntimeError(
            "Final active model is incorrect."
        )

    print(
        "\nRegistry: PASS"
    )

    print(
        "Drift monitoring: PASS"
    )

    print(
        "Retraining evaluation gate: PASS"
    )

    print(
        "Model card: PASS"
    )

    print(
        "Rollback: PASS"
    )

    print(
        "\nTASK 15 INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":

    main()