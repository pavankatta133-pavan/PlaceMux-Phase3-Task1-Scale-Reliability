"""
Task 15
Evaluation Gate + Rollback Test
"""

from model_governance.registry.registry import (
    get_active_model,
    register_model,
    promote_model,
    rollback_model
)

from model_governance.retraining import (
    evaluation_gate
)


def main():

    print(
        "\n========== TASK 15 EVALUATION GATE TEST =========="
    )

    # -------------------------------------------------
    # Get current production model
    # -------------------------------------------------

    current_model = get_active_model()

    print(
        "Current production model:",
        current_model["version"]
    )

    current_metrics = current_model["metrics"]

    print(
        "Current F1:",
        current_metrics["f1"]
    )

    # -------------------------------------------------
    # Create intentionally bad candidate
    # -------------------------------------------------

    bad_candidate_metrics = {
        "precision": 0.60,
        "recall": 0.55,
        "f1": 0.57
    }

    print(
        "\nCandidate F1:",
        bad_candidate_metrics["f1"]
    )

    # -------------------------------------------------
    # Evaluation gate
    # -------------------------------------------------

    passed = evaluation_gate(
        current_metrics,
        bad_candidate_metrics
    )

    if passed:

        raise RuntimeError(
            "Evaluation gate incorrectly accepted "
            "the bad candidate model."
        )

    print(
        "\nEvaluation gate correctly rejected "
        "bad candidate: PASS"
    )

    # -------------------------------------------------
    # Register bad candidate as a candidate only
    # -------------------------------------------------

    candidate_version = "model_bad_test"

    try:

        register_model(
            version=candidate_version,
            metrics=bad_candidate_metrics,
            parent=current_model["version"],
            training_data=(
                "controlled_test_data"
            )
        )

    except ValueError:

        # Safe if the test is run more than once.
        pass

    # -------------------------------------------------
    # Verify candidate was NOT promoted
    # -------------------------------------------------

    active_model = get_active_model()

    if active_model["version"] != current_model["version"]:

        raise RuntimeError(
            "Bad candidate was incorrectly promoted."
        )

    print(
        "Production model protected: PASS"
    )

    # -------------------------------------------------
    # Verify rollback capability
    # -------------------------------------------------

    # Promote a temporary good model so that we
    # can demonstrate rollback.

    temporary_version = "model_rollback_test"

    try:

        register_model(
            version=temporary_version,
            metrics={
                "precision": 0.90,
                "recall": 0.88,
                "f1": 0.89
            },
            parent=current_model["version"],
            training_data=(
                "rollback_test_data"
            )
        )

    except ValueError:

        pass

    promote_model(
        temporary_version
    )

    promoted = get_active_model()

    if promoted["version"] != temporary_version:

        raise RuntimeError(
            "Temporary model promotion failed."
        )

    print(
        "Temporary promotion: PASS"
    )

    # Roll back to original production model.

    rollback_model(
        current_model["version"]
    )

    restored = get_active_model()

    if restored["version"] != current_model["version"]:

        raise RuntimeError(
            "Rollback did not restore the "
            "previous production model."
        )

    print(
        "Rollback restoration: PASS"
    )

    # -------------------------------------------------
    # Final result
    # -------------------------------------------------

    print(
        "\nEvaluation gate: PASS"
    )

    print(
        "Bad model rejection: PASS"
    )

    print(
        "Production protection: PASS"
    )

    print(
        "Rollback: PASS"
    )

    print(
        "\nTASK 15 EVALUATION GATE: PASS"
    )


if __name__ == "__main__":

    main()