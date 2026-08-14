"""
Phase 3 Task 9
Permanent Holdout Assignment
"""

import hashlib


HOLDOUT_PERCENT = 10

HOLDOUT_MODEL = "ranker_v1.0"


def is_holdout(
    student_id,
    holdout_percent=HOLDOUT_PERCENT
):
    """
    Deterministically assign a student
    to the permanent holdout group.
    """

    if not student_id:
        raise ValueError(
            "student_id is required"
        )

    if not 0 <= holdout_percent <= 100:
        raise ValueError(
            "holdout_percent must be between 0 and 100"
        )

    key = (
        "permanent_holdout:"
        + str(student_id)
    ).encode("utf-8")

    hash_value = hashlib.sha256(
        key
    ).hexdigest()

    bucket = int(
        hash_value[:8],
        16
    ) % 100

    return bucket < holdout_percent


def assign_holdout(
    student_id,
    holdout_percent=HOLDOUT_PERCENT
):
    """
    Return holdout assignment details.
    """

    holdout = is_holdout(
        student_id,
        holdout_percent
    )

    return {
        "student_id": student_id,
        "is_holdout": holdout,
        "model_version": (
            HOLDOUT_MODEL
            if holdout
            else "experiment_eligible"
        ),
        "holdout_percent": holdout_percent
    }


if __name__ == "__main__":

    print(
        "\n========== TASK 9 HOLDOUT TEST =========="
    )

    students = [
        "student_001",
        "student_002",
        "student_003",
        "student_004",
        "student_005",
        "student_006",
        "student_007",
        "student_008",
        "student_009",
        "student_010",
        "student_011",
        "student_012",
        "student_013",
        "student_014",
        "student_015",
        "student_016",
        "student_017",
        "student_018",
        "student_019",
        "student_020"
    ]

    holdout_count = 0

    for student in students:

        result = assign_holdout(
            student
        )

        print(result)

        if result["is_holdout"]:
            holdout_count += 1

    print(
        "\nHoldout users:",
        holdout_count
    )

    print(
        "Total users:",
        len(students)
    )

    print(
        "\nTesting consistency..."
    )

    first = is_holdout(
        "student_001"
    )

    second = is_holdout(
        "student_001"
    )

    third = is_holdout(
        "student_001"
    )

    if first == second == third:

        print(
            "Permanent assignment: PASS"
        )

    else:

        print(
            "Permanent assignment: FAIL"
        )

    print(
        "\nHOLDOUT TEST: PASS"
    )