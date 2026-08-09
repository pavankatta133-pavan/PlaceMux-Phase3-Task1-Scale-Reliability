import os
import json
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "post_launch_health",
    "logs",
    "prediction_logs.csv"
)

OFFLINE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "offline_evaluation.csv"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "post_launch_health",
    "reports"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "model_health_report.json"
)


def calculate_health():

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    live = pd.read_csv(LOG_FILE)

    offline = pd.read_csv(OFFLINE_FILE)

    merged = live.merge(
        offline,
        on=[
            "student_id",
            "job_id"
        ],
        how="inner"
    )

    if merged.empty:
        raise ValueError(
            "No matching records found between "
            "live logs and offline benchmark."
        )

    merged["predicted_score"] = (
        pd.to_numeric(
            merged["predicted_score"]
        )
    )

    merged["expected_score"] = (
        pd.to_numeric(
            merged["expected_score"]
        )
    )

    merged["absolute_error"] = (
        abs(
            merged["predicted_score"]
            -
            merged["expected_score"]
        )
    )

    mae = merged[
        "absolute_error"
    ].mean()

    live_average_score = (
        merged[
            "predicted_score"
        ].mean()
    )

    offline_average_score = (
        merged[
            "expected_score"
        ].mean()
    )

    score_gap = (
        live_average_score
        -
        offline_average_score
    )

    success_rate = (
        (
            live[
                "prediction_status"
            ]
            == "success"
        ).mean()
        * 100
    )

    latency = pd.to_numeric(
        live["latency_ms"]
    )

    report = {

        "project":
            "Sprint A - Scale & Reliability",

        "phase":
            "Phase 3",

        "task":
            "Task 1 - Post-Launch Health",

        "model_version":
            live[
                "model_version"
            ].iloc[-1],

        "traffic_summary": {

            "total_predictions":
                int(len(live)),

            "successful_predictions":
                int(
                    (
                        live[
                            "prediction_status"
                        ]
                        == "success"
                    ).sum()
                ),

            "success_rate_percent":
                round(
                    success_rate,
                    2
                )
        },

        "latency_summary": {

            "average_ms":
                round(
                    latency.mean(),
                    2
                ),

            "minimum_ms":
                round(
                    latency.min(),
                    2
                ),

            "maximum_ms":
                round(
                    latency.max(),
                    2
                )
        },

        "model_health": {

            "offline_average_score":
                round(
                    offline_average_score,
                    2
                ),

            "online_average_score":
                round(
                    live_average_score,
                    2
                ),

            "offline_online_gap":
                round(
                    score_gap,
                    2
                ),

            "mean_absolute_error":
                round(
                    mae,
                    2
                )
        },

        "evaluation_note":
            "Offline expected scores are benchmark "
            "labels derived from the documented skill "
            "overlap rule. They are not claimed to be "
            "real user relevance judgments."
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(
        "Model health report generated:"
    )

    print(REPORT_FILE)

    print("\nSummary")
    print(
        "Total predictions:",
        len(live)
    )

    print(
        "Success rate:",
        round(success_rate, 2),
        "%"
    )

    print(
        "Average latency:",
        round(latency.mean(), 2),
        "ms"
    )

    print(
        "Offline average:",
        round(
            offline_average_score,
            2
        )
    )

    print(
        "Online average:",
        round(
            live_average_score,
            2
        )
    )

    print(
        "Offline-online gap:",
        round(
            score_gap,
            2
        )
    )

    print(
        "MAE:",
        round(
            mae,
            2
        )
    )


if __name__ == "__main__":
    calculate_health()