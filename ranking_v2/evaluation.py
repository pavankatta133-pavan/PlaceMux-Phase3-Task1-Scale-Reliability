"""
Phase 3 Task 11
Offline Learning-to-Rank Evaluation

Compares:
1. Existing heuristic ranker
2. LTR Ranker v2

Metrics:
- nDCG@5
- nDCG@10
- MAP@5
- MAP@10

nDCG is used as the primary metric because
the dataset contains graded relevance labels.
"""

import json
import math
import os
from collections import defaultdict

from ranking_v2.baseline import heuristic_score
from ranking_v2.ranker import rank_records


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    PROJECT_ROOT,
    "ranking_v2",
    "reports",
    "ranking_dataset.json"
)

REPORT_FILE = os.path.join(
    PROJECT_ROOT,
    "ranking_v2",
    "reports",
    "ranking_evaluation.json"
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    if not os.path.exists(DATA_FILE):

        raise FileNotFoundError(
            f"Ranking dataset not found:\n{DATA_FILE}"
        )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# GROUP DATA BY STUDENT
# ============================================================

def group_by_student(records):

    groups = defaultdict(list)

    for record in records:

        student_id = record.get(
            "student_id"
        )

        if student_id:

            groups[
                student_id
            ].append(record)

    return groups


# ============================================================
# DCG
# ============================================================

def dcg(
    relevances,
    k
):

    total = 0.0

    for index, relevance in enumerate(
        relevances[:k]
    ):

        position = index + 1

        total += (
            (2 ** relevance - 1)
            /
            math.log2(
                position + 1
            )
        )

    return total


# ============================================================
# NDCG
# ============================================================

def ndcg(
    relevances,
    k
):

    if not relevances:

        return 0.0

    actual_dcg = dcg(
        relevances,
        k
    )

    ideal_relevances = sorted(
        relevances,
        reverse=True
    )

    ideal_dcg = dcg(
        ideal_relevances,
        k
    )

    if ideal_dcg == 0:

        return 0.0

    return (
        actual_dcg
        /
        ideal_dcg
    )


# ============================================================
# AVERAGE PRECISION
# ============================================================

def average_precision(
    relevances,
    k
):

    relevant_total = sum(
        1
        for relevance in relevances
        if relevance > 0
    )

    if relevant_total == 0:

        return None

    hits = 0

    precision_sum = 0.0

    for index, relevance in enumerate(
        relevances[:k]
    ):

        if relevance > 0:

            hits += 1

            precision_sum += (
                hits
                /
                (index + 1)
            )

    denominator = min(
        relevant_total,
        k
    )

    if denominator == 0:

        return None

    return (
        precision_sum
        /
        denominator
    )


# ============================================================
# EVALUATE BASELINE RANKER
# ============================================================

def evaluate_baseline(
    records
):

    ranked_records = sorted(
        records,
        key=heuristic_score,
        reverse=True
    )

    relevances = [

        record.get(
            "relevance_label",
            0
        )

        for record in ranked_records
    ]

    return {

        "ndcg@5":
            ndcg(
                relevances,
                5
            ),

        "ndcg@10":
            ndcg(
                relevances,
                10
            ),

        "map@5":
            average_precision(
                relevances,
                5
            ),

        "map@10":
            average_precision(
                relevances,
                10
            )
    }


# ============================================================
# EVALUATE LTR RANKER
# ============================================================

def evaluate_ltr(
    records
):

    ranked_records = rank_records(
        records
    )

    relevances = [

        record.get(
            "relevance_label",
            0
        )

        for record in ranked_records
    ]

    return {

        "ndcg@5":
            ndcg(
                relevances,
                5
            ),

        "ndcg@10":
            ndcg(
                relevances,
                10
            ),

        "map@5":
            average_precision(
                relevances,
                5
            ),

        "map@10":
            average_precision(
                relevances,
                10
            )
    }


# ============================================================
# AVERAGE METRICS
# ============================================================

def average_metric(
    values
):

    valid_values = [

        value

        for value in values

        if value is not None
    ]

    if not valid_values:

        return 0.0

    return (
        sum(valid_values)
        /
        len(valid_values)
    )


def average_results(
    results
):

    output = {}

    metrics = [
        "ndcg@5",
        "ndcg@10",
        "map@5",
        "map@10"
    ]

    for metric in metrics:

        output[
            metric
        ] = average_metric(

            [
                result.get(
                    metric
                )

                for result in results
            ]
        )

    return output


# ============================================================
# IMPROVEMENT CALCULATION
# ============================================================

def calculate_improvement(
    baseline,
    variant
):

    if baseline == 0:

        return 0.0

    return (
        (
            variant - baseline
        )
        /
        baseline
    ) * 100


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n========== TASK 11 MODEL EVALUATION =========="
    )

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    dataset = load_dataset()

    print(
        "Total ranking records:",
        len(dataset)
    )

    # --------------------------------------------------------
    # Group by student
    # --------------------------------------------------------

    student_groups = group_by_student(
        dataset
    )

    print(
        "Students / ranking queries:",
        len(student_groups)
    )

    # --------------------------------------------------------
    # Validate ranking groups
    # --------------------------------------------------------

    valid_groups = {

        student_id: records

        for student_id, records
        in student_groups.items()

        if len(records) >= 2
    }

    print(
        "Valid ranking queries:",
        len(valid_groups)
    )

    if not valid_groups:

        raise ValueError(
            "No valid ranking groups found."
        )

    # --------------------------------------------------------
    # Evaluate every student separately
    # --------------------------------------------------------

    baseline_results = []

    ltr_results = []

    for student_id, records in (
        valid_groups.items()
    ):

        baseline_result = evaluate_baseline(
            records
        )

        ltr_result = evaluate_ltr(
            records
        )

        baseline_results.append(
            baseline_result
        )

        ltr_results.append(
            ltr_result
        )

    # --------------------------------------------------------
    # Average results
    # --------------------------------------------------------

    baseline_average = average_results(
        baseline_results
    )

    ltr_average = average_results(
        ltr_results
    )

    # --------------------------------------------------------
    # Calculate improvement
    # --------------------------------------------------------

    improvements = {}

    for metric in baseline_average:

        improvements[
            metric
        ] = round(

            calculate_improvement(
                baseline_average[
                    metric
                ],

                ltr_average[
                    metric
                ]
            ),

            2
        )

    # --------------------------------------------------------
    # Print baseline
    # --------------------------------------------------------

    print(
        "\nExisting Heuristic:"
    )

    print(
        "NDCG@5 :",
        round(
            baseline_average[
                "ndcg@5"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "NDCG@10:",
        round(
            baseline_average[
                "ndcg@10"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "MAP@5  :",
        round(
            baseline_average[
                "map@5"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "MAP@10 :",
        round(
            baseline_average[
                "map@10"
            ] * 100,
            2
        ),
        "%"
    )

    # --------------------------------------------------------
    # Print LTR
    # --------------------------------------------------------

    print(
        "\nLTR Ranker v2:"
    )

    print(
        "NDCG@5 :",
        round(
            ltr_average[
                "ndcg@5"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "NDCG@10:",
        round(
            ltr_average[
                "ndcg@10"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "MAP@5  :",
        round(
            ltr_average[
                "map@5"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "MAP@10 :",
        round(
            ltr_average[
                "map@10"
            ] * 100,
            2
        ),
        "%"
    )

    # --------------------------------------------------------
    # Print improvements
    # --------------------------------------------------------

    print(
        "\nImprovement:"
    )

    for metric, value in (
        improvements.items()
    ):

        print(
            metric.upper(),
            ":",
            f"{value}%"
        )

    # ========================================================
    # TASK 11 DECISION
    # ========================================================
    #
    # nDCG is the PRIMARY metric.
    #
    # MAP is reported but is not the primary decision
    # because this dataset contains very few label-0
    # non-relevant candidates.
    #
    # We require the LTR model to improve at least one
    # of the primary nDCG metrics without reducing the
    # other nDCG metric.
    # ========================================================

    baseline_ndcg5 = baseline_average[
        "ndcg@5"
    ]

    baseline_ndcg10 = baseline_average[
        "ndcg@10"
    ]

    ltr_ndcg5 = ltr_average[
        "ndcg@5"
    ]

    ltr_ndcg10 = ltr_average[
        "ndcg@10"
    ]

    ndcg5_improved = (
        ltr_ndcg5
        >
        baseline_ndcg5
    )

    ndcg10_improved = (
        ltr_ndcg10
        >
        baseline_ndcg10
    )

    ndcg5_not_worse = (
        ltr_ndcg5
        >=
        baseline_ndcg5
    )

    ndcg10_not_worse = (
        ltr_ndcg10
        >=
        baseline_ndcg10
    )

    # --------------------------------------------------------
    # Primary evaluation decision
    # --------------------------------------------------------

    passed = (

        (
            ndcg5_improved
            or
            ndcg10_improved
        )

        and

        ndcg5_not_worse

        and

        ndcg10_not_worse
    )

    # --------------------------------------------------------
    # Evaluation explanation
    # --------------------------------------------------------

    if passed:

        decision_reason = (
            "LTR improved at least one primary "
            "nDCG metric without reducing the other."
        )

    else:

        decision_reason = (
            "LTR did not improve the primary "
            "nDCG metrics over the baseline."
        )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    report = {

        "task":
            "Phase 3 Task 11",

        "evaluation_type":
            "per-student offline ranking evaluation",

        "total_records":
            len(dataset),

        "ranking_queries":
            len(student_groups),

        "evaluated_queries":
            len(valid_groups),

        "baseline":
            baseline_average,

        "ltr_ranker_v2":
            ltr_average,

        "improvement_percent":
            improvements,

        "primary_metric":
            "nDCG",

        "secondary_metrics": [
            "MAP@5",
            "MAP@10"
        ],

        "position_bias_correction":
            True,

        "dataset_note":
            (
                "The dataset contains graded relevance "
                "labels and relatively few label-0 records. "
                "Therefore nDCG is used as the primary "
                "ranking-quality metric."
            ),

        "metrics": {

            "ndcg@5_improved":
                ndcg5_improved,

            "ndcg@10_improved":
                ndcg10_improved,

            "ndcg@5_not_worse":
                ndcg5_not_worse,

            "ndcg@10_not_worse":
                ndcg10_not_worse,

            "map@5_improved":
                (
                    ltr_average["map@5"]
                    >
                    baseline_average["map@5"]
                ),

            "map@10_improved":
                (
                    ltr_average["map@10"]
                    >
                    baseline_average["map@10"]
                )
        },

        "decision":
            (
                "PASS"
                if passed
                else
                "LTR DID NOT BEAT BASELINE"
            ),

        "reason":
            decision_reason,

        "evaluation_pass":
            passed
    }

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(
            REPORT_FILE
        ),
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
            indent=2
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print(
        "\nEvaluation report saved to:"
    )

    print(
        REPORT_FILE
    )

    if passed:

        print(
            "\nTASK 11 MODEL EVALUATION: PASS"
        )

    else:

        print(
            "\nTASK 11 MODEL EVALUATION: "
            "LTR DID NOT BEAT BASELINE"
        )

        print(
            "Reason:",
            decision_reason
        )


if __name__ == "__main__":

    main()