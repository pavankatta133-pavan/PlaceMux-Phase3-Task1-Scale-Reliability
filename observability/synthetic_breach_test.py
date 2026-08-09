import csv
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
    "prediction_logs_backup.csv"
)


def create_synthetic_breach():

    os.makedirs(
        os.path.dirname(BACKUP_LOG),
        exist_ok=True
    )

    # Backup the original prediction log
    shutil.copyfile(
        REAL_LOG,
        BACKUP_LOG
    )

    with open(
        REAL_LOG,
        "r",
        encoding="utf-8"
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    if not rows:
        print("No prediction logs found.")
        return False

    # Synthetic latency breach
    for row in rows:
        row["latency_ms"] = "750"

    # Synthetic degenerate prediction output
    for row in rows:
        row["predicted_score"] = "100.0"

    with open(
        REAL_LOG,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = list(rows[0].keys())

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Synthetic breach created.")
    print("Latency set to 750 ms.")
    print("All prediction scores set to 100.")

    return True


def restore_real_log():

    if os.path.exists(BACKUP_LOG):

        shutil.copyfile(
            BACKUP_LOG,
            REAL_LOG
        )

        print(
            "Original prediction logs restored."
        )

    else:

        print(
            "Backup log not found."
        )


def run_monitor():

    monitor_file = os.path.join(
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
            monitor_file
        ],
        check=False
    )


def run_alert_manager():

    alert_file = os.path.join(
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
            alert_file
        ],
        check=False
    )


def main():

    try:

        success = create_synthetic_breach()

        if not success:
            return

        run_monitor()

        run_alert_manager()

        print()
        print(
            "Synthetic breach test completed."
        )

    finally:

        restore_real_log()


if __name__ == "__main__":

    main()