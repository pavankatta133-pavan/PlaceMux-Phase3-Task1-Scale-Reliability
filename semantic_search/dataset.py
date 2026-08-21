"""
Phase 3 Task 13
Semantic Search Dataset
"""

import json
import os


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "semantic_search",
    "data"
)

CATALOG_FILE = os.path.join(
    DATA_DIR,
    "job_catalog.json"
)

DOCUMENT_FILE = os.path.join(
    DATA_DIR,
    "search_documents.json"
)

QUERY_FILE = os.path.join(
    DATA_DIR,
    "search_queries.json"
)


def load_catalog():

    with open(
        CATALOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def build_documents(jobs):

    documents = []

    for index, job in enumerate(
        jobs,
        start=1
    ):

        skills = ", ".join(
            job.get("skills", [])
        )

        text = (
            f"{job.get('title', '')}. "
            f"Skills: {skills}. "
            f"{job.get('description', '')}"
        )

        documents.append({

            "document_id":
                f"doc_{index:04d}",

            "job_id":
                job["job_id"],

            "document_type":
                "job",

            "title":
                job["title"],

            "skills":
                job["skills"],

            "text":
                text
        })

    return documents


def build_queries():

    return [

        {
            "query_id": "query_001",
            "query": "Python backend developer FastAPI REST API SQL",
            "relevant_job_ids": ["job_001", "job_005"]
        },

        {
            "query_id": "query_002",
            "query": "machine learning Python data preprocessing model training",
            "relevant_job_ids": ["job_002", "job_005"]
        },

        {
            "query_id": "query_003",
            "query": "deep learning TensorFlow Keras neural networks computer vision",
            "relevant_job_ids": ["job_003", "job_005"]
        },

        {
            "query_id": "query_004",
            "query": "Python SQL data analysis Pandas dashboards",
            "relevant_job_ids": ["job_004"]
        },

        {
            "query_id": "query_005",
            "query": "AI machine learning model deployment Python FastAPI",
            "relevant_job_ids": ["job_005"]
        },

        {
            "query_id": "query_006",
            "query": "Java Python SQL software engineering Git",
            "relevant_job_ids": ["job_006"]
        }
    ]


def main():

    print(
        "\n========== TASK 13 DATASET =========="
    )

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    jobs = load_catalog()

    documents = build_documents(
        jobs
    )

    queries = build_queries()

    with open(
        DOCUMENT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            documents,
            file,
            indent=2
        )

    with open(
        QUERY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            queries,
            file,
            indent=2
        )

    print(
        "Jobs:",
        len(jobs)
    )

    print(
        "Search documents:",
        len(documents)
    )

    print(
        "Evaluation queries:",
        len(queries)
    )

    print(
        "\nDocuments saved to:"
    )

    print(
        DOCUMENT_FILE
    )

    print(
        "\nQueries saved to:"
    )

    print(
        QUERY_FILE
    )

    print(
        "\nTASK 13 DATASET: PASS"
    )


if __name__ == "__main__":
    main()