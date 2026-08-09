import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "observability",
    "slo_config.json"
)

SLO_REPORT_FILE = os.path.join(
    BASE_DIR,
    "observability",
    "reports",
    "slo_report.json"
)

ERROR_BUDGET_REPORT = os.path.join(
    BASE_DIR,
    "observability",
    "reports",
    "error_budget_report.json"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def calculate_budget():

    config = load_json(CONFIG_FILE)
    report = load_json(SLO_REPORT_FILE)

    metrics = report["metrics"]
    error_config = config["error_budget"]

    # --------------------------------
    # Availability budget
    # --------------------------------

    availability_target = (
        error_config[
            "availability_target_percent"
        ]
    )

    actual_availability = (
        metrics["availability_percent"]
    )

    availability_budget = (
        100 - availability_target
    )

    availability_error = (
        100 - actual_availability
    )

    availability_remaining = max(
        0,
        availability_budget - availability_error
    )

    # --------------------------------
    # Latency budget
    # --------------------------------

    latency_target = (
        error_config[
            "latency_target_percent"
        ]
    )

    successful_requests = (
        metrics["successful_requests"]
    )

    total_requests = (
        metrics["total_requests"]
    )

    if total_requests > 0:

        latency_compliant = (
            1
            if metrics["p95_latency_ms"]
            <= config["slo"]["p95_latency_ms"]
            else 0
        )

        latency_compliance = (
            latency_compliant * 100
        )

    else:

        latency_compliance = 0

    latency_budget = (
        100 - latency_target
    )

    latency_error = (
        100 - latency_compliance
    )

    latency_remaining = max(
        0,
        latency_budget - latency_error
    )

    # --------------------------------
    # Quality budget
    # --------------------------------

    quality_target = (
        error_config[
            "quality_target_percent"
        ]
    )

    if (
        metrics["minimum_score"]
        >= config["slo"][
            "minimum_quality_score"
        ]
    ):

        quality_compliance = 100

    else:

        quality_compliance = 0

    quality_budget = (
        100 - quality_target
    )

    quality_error = (
        100 - quality_compliance
    )

    quality_remaining = max(
        0,
        quality_budget - quality_error
    )

    # --------------------------------
    # Overall status
    # --------------------------------

    budgets = [
        availability_remaining,
        latency_remaining,
        quality_remaining
    ]

    if any(
        budget <= 0
        for budget in budgets
    ):

        status = "BUDGET_EXHAUSTED"

    else:

        status = "WITHIN_BUDGET"

    result = {

        "service":
            config["service"],

        "model_version":
            config["model_version"],

        "availability": {

            "target_percent":
                availability_target,

            "actual_percent":
                actual_availability,

            "allowed_error_percent":
                availability_budget,

            "observed_error_percent":
                availability_error,

            "remaining_budget_percent":
                availability_remaining
        },

        "latency": {

            "target_compliance_percent":
                latency_target,

            "observed_compliance_percent":
                latency_compliance,

            "allowed_error_percent":
                latency_budget,

            "observed_error_percent":
                latency_error,

            "remaining_budget_percent":
                latency_remaining
        },

        "quality": {

            "target_compliance_percent":
                quality_target,

            "observed_compliance_percent":
                quality_compliance,

            "allowed_error_percent":
                quality_budget,

            "observed_error_percent":
                quality_error,

            "remaining_budget_percent":
                quality_remaining
        },

        "overall_status":
            status,

        "recommendation":
            (
                "Continue normal development "
                "and monitoring."
                if status == "WITHIN_BUDGET"
                else
                "Pause risky changes and "
                "prioritize reliability remediation."
            )
    }

    return result


def save_report(result):

    os.makedirs(
        os.path.dirname(
            ERROR_BUDGET_REPORT
        ),
        exist_ok=True
    )

    with open(
        ERROR_BUDGET_REPORT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )


if __name__ == "__main__":

    result = calculate_budget()

    save_report(result)

    print()
    print("Error Budget Report")
    print("====================")

    print(
        "Availability Remaining:",
        result[
            "availability"
        ][
            "remaining_budget_percent"
        ],
        "%"
    )

    print(
        "Latency Remaining:",
        result[
            "latency"
        ][
            "remaining_budget_percent"
        ],
        "%"
    )

    print(
        "Quality Remaining:",
        result[
            "quality"
        ][
            "remaining_budget_percent"
        ],
        "%"
    )

    print(
        "Overall Status:",
        result["overall_status"]
    )

    print(
        "Recommendation:",
        result["recommendation"]
    )