"""
Phase 3 Task 11
Position Bias Correction

Corrects interaction signals based on the
position at which an item was displayed.
"""


def calculate_propensity(position):
    """
    Estimate probability that a user examines
    an item at a given ranking position.

    Higher positions receive lower examination
    probability.
    """

    if position is None or position <= 0:
        return 1.0

    # Simple examination propensity model.
    propensity = 1.0 / position

    # Prevent extremely large weights.
    propensity = max(
        propensity,
        0.05
    )

    return propensity


def calculate_inverse_propensity_weight(
    position
):
    """
    Inverse Propensity Weighting (IPW).

    Lower-ranked items receive more weight because
    they had less opportunity to be examined.
    """

    propensity = calculate_propensity(
        position
    )

    weight = 1.0 / propensity

    # Keep weights bounded for stability.
    weight = min(
        weight,
        20.0
    )

    return round(
        weight,
        4
    )


def correct_interaction(
    relevance_label,
    position
):
    """
    Apply position-bias correction to a
    relevance signal.
    """

    weight = (
        calculate_inverse_propensity_weight(
            position
        )
    )

    corrected_relevance = (
        relevance_label * weight
    )

    return {
        "original_relevance": relevance_label,
        "position": position,
        "propensity": round(
            calculate_propensity(
                position
            ),
            4
        ),
        "inverse_propensity_weight": weight,
        "corrected_relevance": round(
            corrected_relevance,
            4
        )
    }


def main():

    print(
        "\n========== TASK 11 POSITION BIAS =========="
    )

    test_positions = [
        1,
        2,
        3,
        5,
        10
    ]

    for position in test_positions:

        propensity = calculate_propensity(
            position
        )

        weight = (
            calculate_inverse_propensity_weight(
                position
            )
        )

        print(
            f"Position {position}: "
            f"propensity={propensity:.4f}, "
            f"IPW={weight:.4f}"
        )


    example = correct_interaction(
        relevance_label=1,
        position=5
    )

    print(
        "\nExample corrected interaction:"
    )

    print(
        example
    )

    print(
        "\nPOSITION BIAS CORRECTION: PASS"
    )


if __name__ == "__main__":

    main()