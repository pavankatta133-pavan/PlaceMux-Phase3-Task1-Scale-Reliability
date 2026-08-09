import csv
import json
import os
import statistics
import threading
import time
import urllib.error
import urllib.request


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "load_testing",
    "load_config.json"
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "post_launch_health",
    "logs",
    "prediction_logs.csv"
)

REPORT_FILE = os.path.join(
    BASE_DIR,
    "load_testing",
    "reports",
    "load_test_report.json"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_real_inputs():

    if not os.path.exists(LOG_FILE):
        raise FileNotFoundError(
            "Prediction log file not found: "
            + LOG_FILE
        )

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        rows = list(csv.DictReader(file))

    if not rows:
        raise RuntimeError(
            "Prediction log is empty."
        )

    return rows


def percentile(values, p):

    if not values:
        return 0.0

    values = sorted(values)

    index = int(
        (p / 100)
        * (len(values) - 1)
    )

    return values[index]


def send_request(host, port, endpoint, row):

    payload = {
        "student_id":
            row.get("student_id", "student_001"),

        "job_id":
            row.get("job_id", "job_001"),

        "student_skills": [
            "Python",
            "SQL",
            "Machine Learning"
        ],

        "job_skills": [
            "Python",
            "Machine Learning"
        ]
    }

    data = json.dumps(
        payload
    ).encode("utf-8")

    url = (
        f"http://{host}:{port}"
        f"{endpoint}"
    )

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type":
                "application/json"
        },
        method="POST"
    )

    start = time.perf_counter()

    try:

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            response.read()

            latency = (
                time.perf_counter()
                - start
            ) * 1000

            return {
                "success": True,
                "status_code":
                    response.status,
                "latency_ms":
                    latency
            }

    except Exception as exc:

        latency = (
            time.perf_counter()
            - start
        ) * 1000

        return {
            "success": False,
            "status_code":
                None,
            "latency_ms":
                latency,
            "error":
                str(exc)
        }


def run_qps_level(
    host,
    port,
    endpoint,
    rows,
    qps,
    requests_per_level
):

    results = []

    interval = 1.0 / qps

    start_time = time.perf_counter()

    threads = []

    result_lock = threading.Lock()

    def worker(row):

        result = send_request(
            host,
            port,
            endpoint,
            row
        )

        with result_lock:
            results.append(result)

    for i in range(requests_per_level):

        row = rows[
            i % len(rows)
        ]

        thread = threading.Thread(
            target=worker,
            args=(row,)
        )

        threads.append(thread)

        thread.start()

        elapsed = (
            time.perf_counter()
            - start_time
        )

        target_elapsed = (
            (i + 1)
            * interval
        )

        sleep_time = (
            target_elapsed
            - elapsed
        )

        if sleep_time > 0:
            time.sleep(
                sleep_time
            )

    for thread in threads:
        thread.join()

    latencies = [
        result["latency_ms"]
        for result in results
    ]

    successful = sum(
        1
        for result in results
        if result["success"]
    )

    total = len(results)

    success_rate = (
        successful / total * 100
        if total
        else 0
    )

    duration = (
        time.perf_counter()
        - start_time
    )

    actual_qps = (
        total / duration
        if duration > 0
        else 0
    )

    return {
        "target_qps":
            qps,

        "actual_qps":
            round(
                actual_qps,
                2
            ),

        "requests":
            total,

        "successful":
            successful,

        "failed":
            total - successful,

        "success_rate_percent":
            round(
                success_rate,
                2
            ),

        "average_latency_ms":
            round(
                statistics.mean(
                    latencies
                ),
                2
            )
            if latencies else 0,

        "p95_latency_ms":
            round(
                percentile(
                    latencies,
                    95
                ),
                2
            ),

        "max_latency_ms":
            round(
                max(latencies),
                2
            )
            if latencies else 0
    }


def main():

    config = load_json(
        CONFIG_FILE
    )

    rows = load_real_inputs()

    host = config[
        "target"
    ]["host"]

    port = config[
        "target"
    ]["port"]

    endpoint = config[
        "target"
    ]["endpoint"]

    qps_levels = config[
        "load_profile"
    ]["qps_levels"]

    requests_per_level = config[
        "load_profile"
    ]["requests_per_level"]

    results = []

    print()
    print(
        "PlaceMux Horizontal Load Test"
    )
    print(
        "============================="
    )

    for qps in qps_levels:

        print(
            f"\nTesting target QPS: {qps}"
        )

        result = run_qps_level(
            host,
            port,
            endpoint,
            rows,
            qps,
            requests_per_level
        )

        results.append(result)

        print(
            "Actual QPS:",
            result["actual_qps"]
        )

        print(
            "Success Rate:",
            result[
                "success_rate_percent"
            ],
            "%"
        )

        print(
            "Average Latency:",
            result[
                "average_latency_ms"
            ],
            "ms"
        )

        print(
            "P95 Latency:",
            result[
                "p95_latency_ms"
            ],
            "ms"
        )

        print(
            "Maximum Latency:",
            result[
                "max_latency_ms"
            ],
            "ms"
        )

    report = {

        "experiment":
            "Horizontal Scale & Load Readiness",

        "data_source":
            "Real production-style prediction logs",

        "success_criteria":
            config[
                "success_criteria"
            ],

        "headroom_target_percent":
            config[
                "headroom_target_percent"
            ],

        "results":
            results
    }

    os.makedirs(
        os.path.dirname(REPORT_FILE),
        exist_ok=True
    )

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

    print()
    print(
        "Load test report saved to:"
    )
    print(
        REPORT_FILE
    )


if __name__ == "__main__":
    main()