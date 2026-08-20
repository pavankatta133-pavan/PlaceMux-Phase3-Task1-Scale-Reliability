"""
Phase 3 Task 12
Baseline Recommendation System

Baseline strategy:
Recommend the most popular jobs based on
historical engagement.
"""

import json
import os
from collections import defaultdict


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


class PopularityBaseline:

    def __init__(
        self,
        dataset_file=DATASET_FILE
    ):

        self.dataset_file = dataset_file

        self.data = []

        self.job_scores = defaultdict(
            float
        )

        self.load_data()

    # --------------------------------------------------
    # Load dataset
    # --------------------------------------------------

    def load_data(self):

        if not os.path.exists(
            self.dataset_file
        ):
            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_file}"
            )

        with open(
            self.dataset_file,
            "r",
            encoding="utf-8"
        ) as file:

            self.data = json.load(
                file
            )

        for record in self.data:

            job_id = record[
                "job_id"
            ]

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

            # Popularity score
            score = (
                clicks
                + (applications * 3)
                + (shortlists * 4)
            )

            self.job_scores[
                job_id
            ] += score

    # --------------------------------------------------
    # Recommend popular jobs
    # --------------------------------------------------

    def recommend_jobs(
        self,
        k=5
    ):

        recommendations = []

        ranked_jobs = sorted(
            self.job_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for job_id, score in ranked_jobs[:k]:

            recommendations.append({

                "job_id":
                    job_id,

                "score":
                    round(
                        score,
                        4
                    )
            })

        return recommendations


def main():

    print(
        "\n========== TASK 12 BASELINE =========="
    )

    baseline = PopularityBaseline()

    recommendations = (
        baseline.recommend_jobs(
            k=5
        )
    )

    print(
        "\nPopular Job Recommendations:"
    )

    for recommendation in recommendations:

        print(
            recommendation
        )

    print(
        "\nTASK 12 BASELINE: PASS"
    )


if __name__ == "__main__":
    main()