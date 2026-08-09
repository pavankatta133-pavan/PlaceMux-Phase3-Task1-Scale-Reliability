import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

REPORT_FILE = os.path.join(
    BASE_DIR,
    "load_testing",
    "reports",
    "load_test_report.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "load_testing",
    "reports",
    "capacity_analysis.json"
)


def main():

    with open(
        REPORT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        report = json.load(file)

    results = report["results"]

    criteria = report[
        "success_criteria"
    ]

    max_p95 = criteria[
        "max_p95_latency_ms"
    ]

    min_success = criteria[
        "minimum_success_rate_percent"
    ]

    passing = []

    failing = []

    for result in results:

        meets_latency = (
            result["p95_latency_ms"]
            <= max_p95
        )

        meets_success = (
            result["success_rate_percent"]
            >= min_success
        )

        result["meets_latency_slo"] = (
            meets_latency
        )

        result["meets_success_slo"] = (
            meets_success
        )

        result["meets_all_slos"] = (
            meets_latency
            and meets_success
        )

        if result["meets_all_slos"]:
            passing.append(result)
        else:
            failing.append(result)

    if passing:

        safe_capacity = max(
            item["actual_qps"]
            for item in passing
        )

        safe_target_qps = safe_capacity

    else:

        safe_capacity = 0
        safe_target_qps = 0

    if failing:

        first_breaking_qps = min(
            item["target_qps"]
            for item in failing
        )

    else:

        first_breaking_qps = None

    headroom_percent = report[
        "headroom_target_percent"
    ]

    recommended_capacity = (
        safe_target_qps
        * (1 - headroom_percent / 100)
    )

    analysis = {

        "experiment":
            "Horizontal Scale Capacity Analysis",

        "slo": {

            "max_p95_latency_ms":
                max_p95,

            "minimum_success_rate_percent":
                min_success
        },

        "capacity": {

            "highest_passing_actual_qps":
                round(
                    safe_capacity,
                    2
                ),

            "first_breaking_target_qps":
                first_breaking_qps,

            "recommended_operating_qps":
                round(
                    recommended_capacity,
                    2
                ),

            "headroom_percent":
                headroom_percent
        },

        "passing_levels":
            passing,

        "failing_levels":
            failing,

        "interpretation": (
            "The first failing load level indicates "
            "where additional horizontal capacity "
            "is required."
            if first_breaking_qps is not None
            else
            "No breaking point was observed within "
            "the tested load range."
        )
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            analysis,
            file,
            indent=4
        )

    print()
    print(
        "Horizontal Capacity Analysis"
    )
    print(
        "============================"
    )

    print(
        "Highest Passing QPS:",
        round(
            safe_capacity,
            2
        )
    )

    print(
        "First Breaking QPS:",
        first_breaking_qps
    )

    print(
        "Recommended Operating QPS:",
        round(
            recommended_capacity,
            2
        )
    )

    print(
        "Headroom:",
        headroom_percent,
        "%"
    )


if __name__ == "__main__":
    main()