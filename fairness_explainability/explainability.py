"""
Task 14
Per-Decision Explainability
"""

import json
import os


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    PROJECT_ROOT,
    "fairness_explainability",
    "data",
    "matching_data.json"
)


def load_data():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def explain_decision(candidate):

    score = (
        0.5 * candidate["skills_match"]
        + 0.3 * candidate["education_score"]
        + 0.2 * candidate["location_score"]
    )

    decision = (
        "selected"
        if score >= 0.75
        else "not selected"
    )

    explanation = (
        f"Candidate {candidate['candidate_id']} "
        f"was {decision} because the matching score was "
        f"{score:.2f}. "
        f"The score was calculated from skills match "
        f"({candidate['skills_match']:.2f}), education score "
        f"({candidate['education_score']:.2f}), and location "
        f"score ({candidate['location_score']:.2f}). "
        f"The candidate had {candidate['experience_years']} "
        f"years of experience."
    )

    return {
        "candidate_id": candidate["candidate_id"],
        "decision": decision,
        "score": round(score, 4),
        "explanation": explanation
    }


def main():

    print(
        "\n========== TASK 14 EXPLAINABILITY =========="
    )

    records = load_data()

    result = explain_decision(
        records[0]
    )

    print(
        "\nDecision:"
    )

    print(
        result["decision"]
    )

    print(
        "\nExplanation:"
    )

    print(
        result["explanation"]
    )

    if not result["explanation"]:

        raise RuntimeError(
            "Explanation was not generated."
        )

    print(
        "\nTASK 14 EXPLAINABILITY: PASS"
    )


if __name__ == "__main__":

    main()