"""
Phase 3 Task 12
Personalization & Recommendation Engine

Two-sided recommendation engine:

1. Student -> Jobs
2. Job -> Students

The engine supports two modes:

Production:
    exclude_interacted=True

Offline evaluation:
    exclude_interacted=False
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


class RecommendationEngine:

    def __init__(
        self,
        dataset_file=DATASET_FILE
    ):

        self.dataset_file = dataset_file

        self.data = []

        self.student_jobs = defaultdict(list)

        self.job_students = defaultdict(list)

        self.job_popularity = defaultdict(float)

        self.student_engagement = defaultdict(float)

        self.global_job_scores = {}

        self.load_data()

    # ==================================================
    # LOAD DATA
    # ==================================================

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

            self.data = json.load(file)

        for record in self.data:

            student_id = record.get(
                "student_id"
            )

            job_id = record.get(
                "job_id"
            )

            if not student_id or not job_id:
                continue

            engagement_score = record.get(
                "engagement_score",
                0
            )

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

            self.student_jobs[
                student_id
            ].append(record)

            self.job_students[
                job_id
            ].append(record)

            # ------------------------------------------
            # Job popularity
            # ------------------------------------------

            popularity_score = (
                clicks
                + (applications * 3)
                + (shortlists * 4)
            )

            self.job_popularity[
                job_id
            ] += popularity_score

            # ------------------------------------------
            # Student engagement
            # ------------------------------------------

            self.student_engagement[
                student_id
            ] += engagement_score

        self.global_job_scores = dict(
            self.job_popularity
        )

    # ==================================================
    # STUDENT PROFILE
    # ==================================================

    def get_student_profile(
        self,
        student_id
    ):

        records = self.student_jobs.get(
            student_id,
            []
        )

        if not records:

            return {
                "average_engagement": 0.0,
                "total_engagement": 0.0,
                "interacted_jobs": set()
            }

        total_engagement = sum(
            record.get(
                "engagement_score",
                0
            )
            for record in records
        )

        average_engagement = (
            total_engagement
            / len(records)
        )

        interacted_jobs = {
            record["job_id"]
            for record in records
        }

        return {
            "average_engagement":
                average_engagement,

            "total_engagement":
                total_engagement,

            "interacted_jobs":
                interacted_jobs
        }

    # ==================================================
    # JOB SCORE
    # ==================================================

    def calculate_job_score(
        self,
        student_id,
        job_id
    ):

        records = self.job_students.get(
            job_id,
            []
        )

        if not records:
            return 0.0

        # ------------------------------------------
        # Global popularity
        # ------------------------------------------

        popularity = self.job_popularity.get(
            job_id,
            0.0
        )

        # ------------------------------------------
        # Average engagement for this job
        # ------------------------------------------

        job_engagement = sum(
            record.get(
                "engagement_score",
                0
            )
            for record in records
        )

        average_job_engagement = (
            job_engagement
            / len(records)
        )

        # ------------------------------------------
        # Student-specific signal
        #
        # We use the student's overall engagement
        # level to personalize the ranking.
        # ------------------------------------------

        profile = self.get_student_profile(
            student_id
        )

        student_average = profile[
            "average_engagement"
        ]

        # Difference between student's engagement
        # level and job engagement.
        #
        # This is a weak personalization signal.
        # Popularity remains the main signal because
        # this dataset does not contain rich job metadata.
        # ------------------------------------------

        personalization_signal = (
            average_job_engagement
            * (
                1.0
                +
                min(
                    student_average / 100.0,
                    1.0
                )
            )
        )

        # ------------------------------------------
        # Final score
        # ------------------------------------------

        final_score = (
            popularity * 0.60
            +
            average_job_engagement * 0.25
            +
            personalization_signal * 0.15
        )

        return final_score

    # ==================================================
    # STUDENT -> JOBS
    # ==================================================

    def recommend_jobs(
        self,
        student_id,
        k=5,
        exclude_interacted=True
    ):

        profile = self.get_student_profile(
            student_id
        )

        interacted_jobs = profile[
            "interacted_jobs"
        ]

        candidates = []

        # ------------------------------------------
        # Score every available job
        # ------------------------------------------

        for job_id in self.job_students.keys():

            # Production mode:
            # Do not recommend jobs the student
            # has already interacted with.
            if (
                exclude_interacted
                and job_id in interacted_jobs
            ):
                continue

            score = self.calculate_job_score(
                student_id,
                job_id
            )

            candidates.append({

                "job_id":
                    job_id,

                "score":
                    round(
                        score,
                        4
                    )
            })

        # ------------------------------------------
        # Highest score first
        # ------------------------------------------

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return candidates[:k]

    # ==================================================
    # JOB -> STUDENTS
    # ==================================================

    def recommend_candidates(
        self,
        job_id,
        k=5
    ):

        records = self.job_students.get(
            job_id,
            []
        )

        candidates = []

        for record in records:

            student_id = record.get(
                "student_id"
            )

            engagement_score = record.get(
                "engagement_score",
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

            clicks = record.get(
                "clicks",
                0
            )

            # ------------------------------------------
            # Candidate ranking score
            # ------------------------------------------

            candidate_score = (
                engagement_score
                + (applications * 5)
                + (shortlists * 8)
                + (clicks * 0.5)
            )

            candidates.append({

                "student_id":
                    student_id,

                "score":
                    round(
                        candidate_score,
                        4
                    ),

                "applications":
                    applications,

                "shortlists":
                    shortlists,

                "clicks":
                    clicks,

                "engagement_score":
                    engagement_score
            })

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return candidates[:k]


# ======================================================
# STANDALONE TEST
# ======================================================

def main():

    print(
        "\n========== TASK 12 RECOMMENDATION ENGINE =========="
    )

    engine = RecommendationEngine()

    students = list(
        engine.student_jobs.keys()
    )

    jobs = list(
        engine.job_students.keys()
    )

    print(
        "Students:",
        len(students)
    )

    print(
        "Jobs:",
        len(jobs)
    )

    # ------------------------------------------
    # Student -> Jobs
    # ------------------------------------------

    if students:

        student_id = students[0]

        print(
            "\nStudent -> Jobs"
        )

        print(
            "Student:",
            student_id
        )

        recommendations = (
            engine.recommend_jobs(
                student_id,
                k=5,
                exclude_interacted=True
            )
        )

        for item in recommendations:

            print(
                item
            )

    # ------------------------------------------
    # Job -> Students
    # ------------------------------------------

    if jobs:

        job_id = jobs[0]

        print(
            "\nJob -> Candidates"
        )

        print(
            "Job:",
            job_id
        )

        recommendations = (
            engine.recommend_candidates(
                job_id,
                k=5
            )
        )

        for item in recommendations:

            print(
                item
            )

    print(
        "\nTASK 12 RECOMMENDATION ENGINE: PASS"
    )


if __name__ == "__main__":

    main()