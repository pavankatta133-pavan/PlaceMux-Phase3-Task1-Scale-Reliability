import json
import os
import shutil
import subprocess
import sys


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

REAL_LOG = os.path.join(
    BASE_DIR,
    "post_launch_health",
    "logs",
    "prediction_logs.csv"
)

BACKUP_LOG = os.path.join(
    BASE_DIR,
    "observability",
    "logs",
    "failure_test_backup.csv"
)

SLO_REPORT = os.path.join(
    BASE_DIR,
    "observability",
    "reports",
    "slo_report.json"
)

ALERT_REPORT = os.path.join(
    BASE_DIR,
    "observability",
    "reports",
    "alert_report.json"
)


def backup_log():

    os.makedirs(
        os.path.dirname(BACKUP_LOG),
        exist_ok=True
    )

    shutil.copyfile(
        REAL_LOG,
        BACKUP_LOG
    )


def create_failure_data():

    with open(
        REAL_LOG,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "timestamp,request_id,student_id,"
            "job_id,predicted_score,rank,"
            "model_version,latency_ms,"
            "prediction_status,user_feedback\n"
        )

        file.write(
            "2026-08-08T15:00:00,"
            "failure-test-001,"
            "student_failure,"
            "job_failure,"
            "100.0,1,"
            "phase3_matching_v1,"
            "900,failed,\n"
        )


def run_monitor():

    monitor = os.path.join(
        BASE_DIR,
        "observability",
        "observability_monitor.py"
    )

    print()
    print("Running SLO monitor...")
    print()

    subprocess.run(
        [
            sys.executable,
            monitor
        ],
        check=False
    )


def run_alerts():

    alert_manager = os.path.join(
        BASE_DIR,
        "observability",
        "alert_manager.py"
    )

    print()
    print("Running alert manager...")
    print()

    subprocess.run(
        [
            sys.executable,
            alert_manager
        ],
        check=False
    )


def show_results():

    if os.path.exists(SLO_REPORT):

        with open(
            SLO_REPORT,
            "r",
            encoding="utf-8"
        ) as file:

            report = json.load(file)

        print()
        print("SLO Status:")
        print(
            report["overall_status"]
        )

    if os.path.exists(ALERT_REPORT):

        with open(
            ALERT_REPORT,
            "r",
            encoding="utf-8"
        ) as file:

            report = json.load(file)

        print()
        print("Alert Status:")
        print(
            report["overall_status"]
        )

        print(
            "Alert Count:",
            report["alert_count"]
        )

        for alert in report["alerts"]:

            print(
                f"[{alert['severity']}] "
                f"{alert['alert']}"
            )


def restore_log():

    if os.path.exists(BACKUP_LOG):

        shutil.copyfile(
            BACKUP_LOG,
            REAL_LOG
        )

        print()
        print(
            "Original prediction logs restored."
        )


def main():

    try:

        backup_log()

        create_failure_data()

        run_monitor()

        run_alerts()

        show_results()

    finally:

        restore_log()


if __name__ == "__main__":

    main()