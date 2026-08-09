import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

BENCHMARK_FILE = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "before_after_report.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "cost_report.json"
)


# Transparent local compute-cost proxy.
# This is NOT a cloud billing figure.
COST_PER_COMPUTE_SECOND = 0.0001


def load():

    with open(
        BENCHMARK_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def calculate():

    benchmark = load()

    baseline_ms = benchmark[
        "comparison"
    ]["baseline_processing_ms"]

    optimized_ms = benchmark[
        "comparison"
    ]["optimized_processing_ms"]

    baseline_cost = (
        baseline_ms / 1000
    ) * COST_PER_COMPUTE_SECOND

    optimized_cost = (
        optimized_ms / 1000
    ) * COST_PER_COMPUTE_SECOND

    if baseline_cost > 0:

        saving_percent = (
            (
                baseline_cost
                - optimized_cost
            )
            / baseline_cost
        ) * 100

    else:

        saving_percent = 0

    report = {

        "cost_type":
            "estimated local compute proxy",

        "warning":
            "This is an engineering estimate, "
            "not actual cloud billing.",

        "cost_per_compute_second":
            COST_PER_COMPUTE_SECOND,

        "baseline": {

            "processing_ms":
                baseline_ms,

            "estimated_cost_per_request":
                round(
                    baseline_cost,
                    10
                )
        },

        "optimized": {

            "processing_ms":
                optimized_ms,

            "estimated_cost_per_request":
                round(
                    optimized_cost,
                    10
                )
        },

        "estimated_saving_percent":
            round(
                saving_percent,
                2
            )
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    return report


if __name__ == "__main__":

    result = calculate()

    print()
    print("Estimated Cost Analysis")
    print("=======================")

    print(
        "Baseline Estimated Cost:",
        result[
            "baseline"
        ]["estimated_cost_per_request"]
    )

    print(
        "Optimized Estimated Cost:",
        result[
            "optimized"
        ]["estimated_cost_per_request"]
    )

    print(
        "Estimated Saving:",
        result[
            "estimated_saving_percent"
        ],
        "%"
    )

    print()
    print(
        "Note: This is a local compute-cost "
        "proxy, not actual cloud billing."
    )