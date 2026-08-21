"""
Task 15
Model Registry
"""

import json
import os


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

REGISTRY_FILE = os.path.join(
    PROJECT_ROOT,
    "model_governance",
    "registry",
    "model_registry.json"
)


def load_registry():
    with open(
        REGISTRY_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_registry(registry):
    with open(
        REGISTRY_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            registry,
            file,
            indent=2
        )


def get_active_model():
    registry = load_registry()

    active_version = registry["active_model"]

    return registry["models"][active_version]


def register_model(
    version,
    metrics,
    parent=None,
    training_data="unknown",
    status="candidate"
):
    registry = load_registry()

    if version in registry["models"]:
        raise ValueError(
            f"Model {version} already exists."
        )

    registry["models"][version] = {
        "version": version,
        "status": status,
        "metrics": metrics,
        "lineage": {
            "parent": parent,
            "training_data": training_data
        }
    }

    save_registry(registry)


def promote_model(version):
    registry = load_registry()

    if version not in registry["models"]:
        raise ValueError(
            f"Model {version} is not registered."
        )

    current = registry["active_model"]

    registry["models"][current]["status"] = "archived"
    registry["models"][version]["status"] = "production"

    registry["active_model"] = version

    save_registry(registry)


def rollback_model(version):
    registry = load_registry()

    if version not in registry["models"]:
        raise ValueError(
            f"Model {version} is not registered."
        )

    current = registry["active_model"]

    registry["models"][current]["status"] = "rolled_back"

    registry["models"][version]["status"] = "production"

    registry["active_model"] = version

    save_registry(registry)


def main():

    print(
        "\n========== TASK 15 MODEL REGISTRY =========="
    )

    model = get_active_model()

    print(
        "Active model:",
        model["version"]
    )

    print(
        "Status:",
        model["status"]
    )

    print(
        "Metrics:",
        model["metrics"]
    )

    print(
        "Parent:",
        model["lineage"]["parent"]
    )

    print(
        "Training data:",
        model["lineage"]["training_data"]
    )

    print(
        "\nTASK 15 MODEL REGISTRY: PASS"
    )


if __name__ == "__main__":
    main()