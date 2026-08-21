"""
Task 15
Retraining Pipeline with Evaluation Gate
"""

from model_governance.registry.registry import (
    get_active_model,
    register_model,
    promote_model,
    rollback_model
)

from model_governance.drift_monitor import (
    monitor_drift
)


def evaluate_candidate_model():
    """
    Simulated evaluation of the newly trained model.

    The candidate must outperform the currently
    active production model before promotion.
    """

    return {
        "precision": 0.88,
        "recall": 0.84,
        "f1": 0.86
    }


def evaluation_gate(
    current_metrics,
    candidate_metrics
):

    current_f1 = current_metrics["f1"]
    candidate_f1 = candidate_metrics["f1"]

    return candidate_f1 > current_f1


def retrain():

    print(
        "\n========== TASK 15 RETRAINING =========="
    )

    current_model = get_active_model()

    print(
        "Current production model:",
        current_model["version"]
    )

    drift_report = monitor_drift()

    if not drift_report["retraining_trigger"]:

        print(
            "No drift detected."
        )

        print(
            "Retraining not required."
        )

        return {
            "retrained": False,
            "promoted": False,
            "reason": "No drift detected"
        }

    print(
        "Drift detected."
    )

    print(
        "Starting retraining..."
    )

    candidate_metrics = (
        evaluate_candidate_model()
    )

    print(
        "Candidate metrics:",
        candidate_metrics
    )

    passed = evaluation_gate(
        current_model["metrics"],
        candidate_metrics
    )

    if not passed:

        print(
            "Evaluation gate: FAIL"
        )

        print(
            "Candidate model will NOT be promoted."
        )

        return {
            "retrained": True,
            "promoted": False,
            "reason": "Evaluation gate failed"
        }

    print(
        "Evaluation gate: PASS"
    )

    current_version = current_model["version"]

    if current_version == "model_v1":
        new_version = "model_v2"
    else:
        number = int(
            current_version.split("_v")[-1]
        )

        new_version = (
            f"model_v{number + 1}"
        )

    register_model(
        version=new_version,
        metrics=candidate_metrics,
        parent=current_version,
        training_data=(
            "semantic_search/data/"
            "search_documents.json"
        )
    )

    promote_model(
        new_version
    )

    active_model = get_active_model()

    print(
        "New production model:",
        active_model["version"]
    )

    print(
        "Retraining completed successfully."
    )

    return {
        "retrained": True,
        "promoted": True,
        "model_version": active_model["version"]
    }


def test_rollback():

    """
    Verify that the previous production model
    can still be restored.
    """

    current_model = get_active_model()

    if current_model["version"] == "model_v1":
        return

    parent = current_model["lineage"]["parent"]

    rollback_model(parent)

    restored = get_active_model()

    if restored["version"] != parent:

        raise RuntimeError(
            "Rollback verification failed."
        )

    print(
        "Rollback verification: PASS"
    )


def main():

    result = retrain()

    print(
        "\nRetraining result:"
    )

    print(
        result
    )

    print(
        "\nTASK 15 RETRAINING: PASS"
    )


if __name__ == "__main__":

    main()