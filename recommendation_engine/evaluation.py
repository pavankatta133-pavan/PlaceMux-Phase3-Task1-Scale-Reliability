"""
Phase 3 Task 12
Recommendation Engine Evaluation

Metrics:
    Precision@5
    Coverage
    Diversity

Systems compared:
    1. Popularity Baseline
    2. Personalized Recommendation Engine
"""

import json
import os
from collections import defaultdict

from recommendation_engine.recommender import (
    RecommendationEngine
)

from recommendation_engine.baseline import (
    PopularityBaseline
)


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


DATASET_FILE = os.path.join(
    PROJECT_ROOT,
    "recommendation_engine",
    "reports",
    "recommendation_dataset.json"
)


REPORT_FILE = os.path.join(
    PROJECT_ROOT,
    "recommendation_engine",
    "reports",
    "evaluation_report.json"
)


K = 5


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset():

    if not os.path.exists(
        DATASET_FILE
    ):
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_FILE}"
        )

    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# BUILD RELEVANCE DATA
# =========================================================

def build_relevance_map(
    dataset
):
    """
    A job is relevant to a student when the student
    performed at least one meaningful action:

        click
        application
        shortlist
    """

    relevance = defaultdict(set)

    for record in dataset:

        student_id = record.get(
            "student_id"
        )

        job_id = record.get(
            "job_id"
        )

        if not student_id or not job_id:
            continue

        clicks = record.get(
            "clicks",
            0
        )

        applications = record.get(
            "applications",
            0
        )

        shortlists = record.get(
            "shortlists",
            0
        )

        if (
            clicks > 0
            or applications > 0
            or shortlists > 0
        ):

            relevance[
                student_id
            ].add(
                job_id
            )

    return relevance


# =========================================================
# PRECISION@K
# =========================================================

def precision_at_k(
    recommendations,
    relevant_jobs,
    k=5
):

    if not recommendations:
        return 0.0

    top_k = recommendations[:k]

    hits = 0

    for recommendation in top_k:

        job_id = recommendation.get(
            "job_id"
        )

        if job_id in relevant_jobs:

            hits += 1

    return hits / len(top_k)


# =========================================================
# COVERAGE
# =========================================================

def calculate_coverage(
    recommendation_lists,
    total_jobs
):

    if total_jobs == 0:
        return 0.0

    unique_recommended_jobs = set()

    for recommendations in recommendation_lists:

        for recommendation in recommendations:

            job_id = recommendation.get(
                "job_id"
            )

            if job_id:
                unique_recommended_jobs.add(
                    job_id
                )

    return (
        len(unique_recommended_jobs)
        / total_jobs
    )


# =========================================================
# DIVERSITY
# =========================================================

def calculate_diversity(
    recommendation_lists
):

    all_recommendations = []

    for recommendations in recommendation_lists:

        for recommendation in recommendations:

            job_id = recommendation.get(
                "job_id"
            )

            if job_id:

                all_recommendations.append(
                    job_id
                )

    if not all_recommendations:
        return 0.0

    unique_jobs = len(
        set(all_recommendations)
    )

    total_recommendations = len(
        all_recommendations
    )

    return (
        unique_jobs
        / total_recommendations
    )


# =========================================================
# EVALUATE BASELINE
# =========================================================

def evaluate_baseline(
    baseline,
    students,
    relevance_map,
    total_jobs
):

    precision_values = []

    recommendation_lists = []

    # Popularity baseline returns the same
    # popular-job list for every student.

    recommendations = (
        baseline.recommend_jobs(
            k=K
        )
    )

    for student_id in students:

        recommendation_lists.append(
            recommendations
        )

        relevant_jobs = relevance_map.get(
            student_id,
            set()
        )

        precision = precision_at_k(
            recommendations,
            relevant_jobs,
            K
        )

        precision_values.append(
            precision
        )

    average_precision = (
        sum(precision_values)
        /
        len(precision_values)
        if precision_values
        else 0.0
    )

    coverage = calculate_coverage(
        recommendation_lists,
        total_jobs
    )

    diversity = calculate_diversity(
        recommendation_lists
    )

    return {

        "system":
            "Popularity Baseline",

        "precision_at_5":
            round(
                average_precision,
                4
            ),

        "coverage":
            round(
                coverage,
                4
            ),

        "diversity":
            round(
                diversity,
                4
            )
    }


# =========================================================
# EVALUATE PERSONALIZED ENGINE
# =========================================================

def evaluate_personalized(
    recommender,
    students,
    relevance_map,
    total_jobs
):

    precision_values = []

    recommendation_lists = []

    for student_id in students:

        # -------------------------------------------------
        # IMPORTANT
        #
        # During offline evaluation we DO NOT exclude
        # interacted jobs.
        #
        # This allows us to check whether the model
        # ranks jobs that the student actually engaged
        # with.
        # -------------------------------------------------

        recommendations = (
            recommender.recommend_jobs(
                student_id,
                k=K,
                exclude_interacted=False
            )
        )

        recommendation_lists.append(
            recommendations
        )

        relevant_jobs = relevance_map.get(
            student_id,
            set()
        )

        precision = precision_at_k(
            recommendations,
            relevant_jobs,
            K
        )

        precision_values.append(
            precision
        )

    average_precision = (
        sum(precision_values)
        /
        len(precision_values)
        if precision_values
        else 0.0
    )

    coverage = calculate_coverage(
        recommendation_lists,
        total_jobs
    )

    diversity = calculate_diversity(
        recommendation_lists
    )

    return {

        "system":
            "Personalized Recommendation Engine",

        "precision_at_5":
            round(
                average_precision,
                4
            ),

        "coverage":
            round(
                coverage,
                4
            ),

        "diversity":
            round(
                diversity,
                4
            )
    }


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n========== TASK 12 MODEL EVALUATION =========="
    )

    dataset = load_dataset()

    students = sorted(
        set(
            record.get(
                "student_id"
            )
            for record in dataset
            if record.get(
                "student_id"
            )
        )
    )

    jobs = sorted(
        set(
            record.get(
                "job_id"
            )
            for record in dataset
            if record.get(
                "job_id"
            )
        )
    )

    relevance_map = build_relevance_map(
        dataset
    )

    print(
        "Dataset records:",
        len(dataset)
    )

    print(
        "Students:",
        len(students)
    )

    print(
        "Jobs:",
        len(jobs)
    )

    # -----------------------------------------------------
    # Show relevance information
    # -----------------------------------------------------

    print(
        "\nRelevant jobs per student:"
    )

    for student_id in students:

        print(
            student_id,
            ":",
            sorted(
                relevance_map.get(
                    student_id,
                    set()
                )
            )
        )

    # -----------------------------------------------------
    # BASELINE
    # -----------------------------------------------------

    print(
        "\nEvaluating popularity baseline..."
    )

    baseline = PopularityBaseline()

    baseline_results = evaluate_baseline(
        baseline,
        students,
        relevance_map,
        len(jobs)
    )

    print(
        "Baseline Precision@5:",
        round(
            baseline_results[
                "precision_at_5"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "Baseline Coverage:",
        round(
            baseline_results[
                "coverage"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "Baseline Diversity:",
        round(
            baseline_results[
                "diversity"
            ] * 100,
            2
        ),
        "%"
    )

    # -----------------------------------------------------
    # PERSONALIZED
    # -----------------------------------------------------

    print(
        "\nEvaluating personalized engine..."
    )

    recommender = RecommendationEngine()

    personalized_results = evaluate_personalized(
        recommender,
        students,
        relevance_map,
        len(jobs)
    )

    print(
        "Personalized Precision@5:",
        round(
            personalized_results[
                "precision_at_5"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "Personalized Coverage:",
        round(
            personalized_results[
                "coverage"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "Personalized Diversity:",
        round(
            personalized_results[
                "diversity"
            ] * 100,
            2
        ),
        "%"
    )

    # -----------------------------------------------------
    # IMPROVEMENT
    # -----------------------------------------------------

    precision_improvement = (
        personalized_results[
            "precision_at_5"
        ]
        -
        baseline_results[
            "precision_at_5"
        ]
    )

    coverage_improvement = (
        personalized_results[
            "coverage"
        ]
        -
        baseline_results[
            "coverage"
        ]
    )

    diversity_improvement = (
        personalized_results[
            "diversity"
        ]
        -
        baseline_results[
            "diversity"
        ]
    )

    print(
        "\nImprovement:"
    )

    print(
        "Precision@5:",
        round(
            precision_improvement * 100,
            2
        ),
        "%"
    )

    print(
        "Coverage:",
        round(
            coverage_improvement * 100,
            2
        ),
        "%"
    )

    print(
        "Diversity:",
        round(
            diversity_improvement * 100,
            2
        ),
        "%"
    )

    # -----------------------------------------------------
    # SAVE REPORT
    # -----------------------------------------------------

    report = {

        "task":
            "Phase 3 Task 12",

        "dataset_records":
            len(dataset),

        "students":
            len(students),

        "jobs":
            len(jobs),

        "k":
            K,

        "baseline":
            baseline_results,

        "personalized":
            personalized_results,

        "improvement": {

            "precision_at_5":
                round(
                    precision_improvement,
                    4
                ),

            "coverage":
                round(
                    coverage_improvement,
                    4
                ),

            "diversity":
                round(
                    diversity_improvement,
                    4
                )
        }
    }

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

    print(
        "\nEvaluation report saved to:"
    )

    print(
        REPORT_FILE
    )

    print(
        "\nTASK 12 MODEL EVALUATION: PASS"
    )


if __name__ == "__main__":

    main()