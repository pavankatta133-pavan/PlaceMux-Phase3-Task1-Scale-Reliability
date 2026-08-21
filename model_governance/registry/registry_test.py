"""
Task 15
Model Registry Versioning & Rollback Test
"""

from model_governance.registry.registry import (
    get_active_model,
    register_model,
    promote_model,
    rollback_model,
)


def main():

    print(
        "\n========== TASK 15 REGISTRY VERSIONING =========="
    )

    # -------------------------------------------------
    # Check initial production model
    # -------------------------------------------------

    active = get_active_model()

    print(
        "Initial active model:",
        active["version"]
    )

    if active["version"] != "model_v1":
        raise RuntimeError(
            "Initial model must be model_v1."
        )

    # -------------------------------------------------
    # Register model v2
    # -------------------------------------------------

    register_model(
        version="model_v2",
        metrics={
            "precision": 0.85,
            "recall": 0.81,
            "f1": 0.83
        },
        parent="model_v1",
        training_data=(
            "semantic_search/data/"
            "search_documents.json"
        )
    )

    print(
        "Registered model: model_v2"
    )

    # -------------------------------------------------
    # Promote model v2
    # -------------------------------------------------

    promote_model(
        "model_v2"
    )

    active = get_active_model()

    print(
        "Promoted model:",
        active["version"]
    )

    print(
        "Parent model:",
        active["lineage"]["parent"]
    )

    # -------------------------------------------------
    # Validate promotion
    # -------------------------------------------------

    if active["version"] != "model_v2":

        raise RuntimeError(
            "Model v2 was not promoted."
        )

    if active["lineage"]["parent"] != "model_v1":

        raise RuntimeError(
            "Model lineage is incorrect."
        )

    # -------------------------------------------------
    # Roll back to model v1
    # -------------------------------------------------

    rollback_model(
        "model_v1"
    )

    active = get_active_model()

    print(
        "After rollback:",
        active["version"]
    )

    # -------------------------------------------------
    # Validate rollback
    # -------------------------------------------------

    if active["version"] != "model_v1":

        raise RuntimeError(
            "Rollback failed."
        )

    # -------------------------------------------------
    # Final results
    # -------------------------------------------------

    print(
        "\nVersioning: PASS"
    )

    print(
        "Lineage: PASS"
    )

    print(
        "Promotion: PASS"
    )

    print(
        "Rollback: PASS"
    )

    print(
        "\nTASK 15 REGISTRY VERSIONING: PASS"
    )


if __name__ == "__main__":

    main()