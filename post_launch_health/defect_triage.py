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

OUTPUT_FILE = os.path.join(
    REPORT_DIR,
    "intelligence_defects.json"
)


def load_data():

    live = pd.read_csv(
        LOG_FILE
    )

    offline = pd.read_csv(
        OFFLINE_FILE
    )

    return live, offline


def create_defects():

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    live, offline = load_data()

    defects = []

    # -------------------------------------------------
    # DEFECT 1: Missing user feedback
    # -------------------------------------------------

    feedback_missing = live[
        live["user_feedback"]
        .fillna("")
        .astype(str)
        .str.strip()
        == ""
    ]

    if len(feedback_missing) > 0:

        defects.append({

            "defect_id":
                "INT-001",

            "title":
                "User feedback is missing from live predictions",

            "severity":
                "Medium",

            "priority":
                "P1",

            "evidence":
                f"{len(feedback_missing)} of "
                f"{len(live)} logged predictions "
                "contain no user feedback.",

            "likely_cause":
                "The prediction API currently logs "
                "predictions but does not yet collect "
                "explicit user relevance feedback.",

            "business_impact":
                "The team cannot reliably measure "
                "whether recommendations are useful "
                "to users after launch.",

            "owner":
                "ML Platform / Product Analytics",

            "recommended_action":
                "Add recommendation feedback events "
                "such as relevant, not relevant, "
                "clicked, applied and dismissed.",

            "status":
                "Open"
        })


    # -------------------------------------------------
    # DEFECT 2: Low-score recommendations
    # -------------------------------------------------

    low_score = live[
        pd.to_numeric(
            live["predicted_score"]
        ) < 50
    ]

    if len(low_score) > 0:

        defects.append({

            "defect_id":
                "INT-002",

            "title":
                "Low-score recommendation requires review",

            "severity":
                "Low",

            "priority":
                "P2",

            "evidence":
                f"{len(low_score)} of "
                f"{len(live)} predictions "
                "have a match score below 50.",

            "likely_cause":
                "Low overlap between student skills "
                "and required job skills.",

            "business_impact":
                "Low-quality matches may reduce "
                "recommendation usefulness if they "
                "are surfaced too prominently.",

            "owner":
                "Recommendation Engineering",

            "recommended_action":
                "Review ranking thresholds and consider "
                "filtering or explaining low-confidence "
                "recommendations.",

            "status":
                "Open"
        })


    # -------------------------------------------------
    # DEFECT 3: No production relevance labels
    # -------------------------------------------------

    defects.append({

        "defect_id":
            "INT-003",

        "title":
            "Production relevance labels are unavailable",

        "severity":
            "Medium",

        "priority":
            "P1",

        "evidence":
            "Current evaluation uses benchmark "
            "expected scores rather than genuine "
            "post-launch user relevance labels.",

        "likely_cause":
            "The system has prediction logging but "
            "does not yet maintain a labelled feedback "
            "dataset for online evaluation.",

        "business_impact":
            "Offline-online agreement cannot yet be "
            "interpreted as real user recommendation "
            "accuracy.",

        "owner":
            "ML Engineering / Product Analytics",

        "recommended_action":
            "Build a feedback-labelled evaluation "
            "dataset and calculate precision, recall, "
            "ranking quality or other agreed relevance "
            "metrics on real interactions.",

        "status":
            "Open"
    })


    # -------------------------------------------------
    # DEFECT 4: Small live sample
    # -------------------------------------------------

    if len(live) < 100:

        defects.append({

            "defect_id":
                "INT-004",

            "title":
                "Live evaluation sample is too small",

            "severity":
                "Low",

            "priority":
                "P2",

            "evidence":
                f"Only {len(live)} live predictions "
                "are currently available for analysis.",

            "likely_cause":
                "The post-launch monitoring pipeline "
                "has only recently been activated.",

            "business_impact":
                "Small samples can make model-health "
                "metrics unstable and may hide rare "
                "failure patterns.",

            "owner":
                "ML Platform",

            "recommended_action":
                "Continue collecting production-safe "
                "interaction logs and define minimum "
                "sample thresholds before automated "
                "health decisions.",

            "status":
                "Open"
        })


    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    severity_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    defects.sort(
        key=lambda item:
            (
                severity_order.get(
                    item["severity"],
                    99
                ),
                item["priority"]
            )
    )

    report = {

        "project":
            "Sprint A - Scale & Reliability",

        "phase":
            "Phase 3",

        "task":
            "Task 1 - Post-Launch Health",

        "total_defects":
            len(defects),

        "ranking_method":
            "Severity first, followed by priority",

        "defects":
            defects
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

    print(
        "Intelligence defect report generated:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nTotal defects:",
        len(defects)
    )

    for defect in defects:

        print(
            f"{defect['defect_id']} | "
            f"{defect['severity']} | "
            f"{defect['priority']} | "
            f"{defect['title']}"
        )


if __name__ == "__main__":

    create_defects()