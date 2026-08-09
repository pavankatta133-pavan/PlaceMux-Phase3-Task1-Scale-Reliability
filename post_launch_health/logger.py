import csv
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LOG_DIR = os.path.join(
    BASE_DIR,
    "logs"
)

LOG_FILE = os.path.join(
    LOG_DIR,
    "prediction_logs.csv"
)


FIELDS = [
    "timestamp",
    "request_id",
    "student_id",
    "job_id",
    "predicted_score",
    "rank",
    "model_version",
    "latency_ms",
    "prediction_status",
    "user_feedback"
]


def initialize_log():

    os.makedirs(
        LOG_DIR,
        exist_ok=True
    )

    if not os.path.exists(LOG_FILE):

        with open(
            LOG_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDS
            )

            writer.writeheader()


def log_prediction(
    request_id,
    student_id,
    job_id,
    predicted_score,
    rank,
    model_version,
    latency_ms,
    prediction_status,
    user_feedback=""
):

    initialize_log()

    row = {
        "timestamp":
            datetime.now().isoformat(),

        "request_id":
            request_id,

        "student_id":
            student_id,

        "job_id":
            job_id,

        "predicted_score":
            predicted_score,

        "rank":
            rank,

        "model_version":
            model_version,

        "latency_ms":
            latency_ms,

        "prediction_status":
            prediction_status,

        "user_feedback":
            user_feedback
    }

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writerow(row)


if __name__ == "__main__":

    initialize_log()

    print(
        "Prediction log initialized:"
    )

    print(LOG_FILE)