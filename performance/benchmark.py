import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

BASELINE_FILE = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "baseline_report.json"
)

OPTIMIZED_FILE = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "optimized_report.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "before_after_report.json"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def calculate():

    baseline = load_json(
        BASELINE_FILE
    )

    optimized = load_json(
        OPTIMIZED_FILE
    )

    baseline_time = baseline[
        "baseline_processing_time_ms"
    ]

    optimized_time = optimized[
        "optimized_processing_time_ms"
    ]

    if baseline_time > 0:

        improvement = (
            (baseline_time - optimized_time)
            / baseline_time
        ) * 100

    else:

        improvement = 0

    baseline_quality = baseline[
        "prediction_quality"
    ]["average_score"]

    optimized_quality = optimized[
        "prediction_quality"
    ]["average_score"]

    quality_difference = (
        optimized_quality
        - baseline_quality
    )

    slo_target = 500.0

    baseline_p95 = baseline[
        "logged_latency"
    ]["p95_ms"]

    optimized_p95 = optimized[
        "logged_p95_latency_ms"
    ]

    report = {

        "comparison": {

            "baseline_processing_ms":
                round(
                    baseline_time,
                    4
                ),

            "optimized_processing_ms":
                round(
                    optimized_time,
                    4
                ),

            "latency_improvement_percent":
                round(
                    improvement,
                    2
                )
        },

        "latency_slo": {

            "target_p95_ms":
                slo_target,

            "baseline_p95_ms":
                baseline_p95,

            "optimized_p95_ms":
                optimized_p95,

            "baseline_meets_slo":
                baseline_p95 <= slo_target,

            "optimized_meets_slo":
                optimized_p95 <= slo_target
        },

        "quality_comparison": {

            "baseline_average_score":
                baseline_quality,

            "optimized_average_score":
                optimized_quality,

            "quality_difference":
                round(
                    quality_difference,
                    4
                ),

            "quality_maintained":
                quality_difference >= 0
        },

        "conclusion":
            (
                "Optimization maintained or improved "
                "quality while reducing processing time."
                if (
                    optimized_time < baseline_time
                    and quality_difference >= 0
                )
                else
                "Optimization requires further evaluation."
            )
    }

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

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
    print("Before / After Performance")
    print("==========================")

    print(
        "Baseline Processing:",
        result[
            "comparison"
        ]["baseline_processing_ms"],
        "ms"
    )

    print(
        "Optimized Processing:",
        result[
            "comparison"
        ]["optimized_processing_ms"],
        "ms"
    )

    print(
        "Latency Improvement:",
        result[
            "comparison"
        ]["latency_improvement_percent"],
        "%"
    )

    print(
        "Baseline Quality:",
        result[
            "quality_comparison"
        ]["baseline_average_score"]
    )

    print(
        "Optimized Quality:",
        result[
            "quality_comparison"
        ]["optimized_average_score"]
    )

    print(
        "Quality Maintained:",
        result[
            "quality_comparison"
        ]["quality_maintained"]
    )

    print(
        "Optimized Meets SLO:",
        result[
            "latency_slo"
        ]["optimized_meets_slo"]
    )