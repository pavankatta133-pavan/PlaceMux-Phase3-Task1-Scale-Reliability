"""
Phase 3 Task 9
Deterministic Experiment Assignment
"""

import hashlib


CONTROL_MODEL = "ranker_v1.0"
VARIANT_MODEL = "ranker_v2.0"

DEFAULT_VARIANT_PERCENT = 10


def assign_model(
    student_id,
    variant_percent=DEFAULT_VARIANT_PERCENT
):
    """
    Deterministically assign a student to
    control or variant.

    Same student_id always receives the
    same model for the same traffic split.
    """

    if not student_id:
        raise ValueError(
            "student_id is required"
        )

    if not 0 <= variant_percent <= 100:
        raise ValueError(
            "variant_percent must be between 0 and 100"
        )

    key = str(student_id).encode(
        "utf-8"
    )

    hash_value = hashlib.sha256(
        key
    ).hexdigest()

    bucket = int(
        hash_value[:8],
        16
    ) % 100

    if bucket < variant_percent:
        return VARIANT_MODEL

    return CONTROL_MODEL


def assignment_details(
    student_id,
    variant_percent=DEFAULT_VARIANT_PERCENT
):
    """
    Return assignment information
    useful for experiment logging.
    """

    model = assign_model(
        student_id,
        variant_percent
    )

    return {
        "student_id": student_id,
        "model_version": model,
        "variant_percent": variant_percent,
        "control_model": CONTROL_MODEL,
        "variant_model": VARIANT_MODEL
    }


if __name__ == "__main__":

    print(
        "\n========== TASK 9 ASSIGNMENT TEST =========="
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
        "student_010"
    ]

    for student in students:

        print(
            assignment_details(
                student
            )
        )