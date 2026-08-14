"""
Phase 3 Task 10
Failure Path Test

Verifies that a clearly unsafe variant
results in DO NOT SHIP.
"""

from experimentation.guardrails import evaluate_guardrails


def main():

    print(
        "\n========== TASK 10 FAILURE TEST =========="
    )

    # Healthy control
    control_impressions = 1000
    control_actions = 800

    # Intentionally poor variant
    variant_impressions = 1000
    variant_actions = 300

    result = evaluate_guardrails(
        control_impressions=control_impressions,
        control_relevant_actions=control_actions,
        variant_impressions=variant_impressions,
        variant_relevant_actions=variant_actions,
        min_sample_size=100
    )

    control_rate = (
        control_actions
        / control_impressions
    )

    variant_rate = (
        variant_actions
        / variant_impressions
    )

    lift = (
        (
            variant_rate
            - control_rate
        )
        / control_rate
    ) * 100

    print(
        "\nControl Rate:",
        round(
            control_rate * 100,
            2
        ),
        "%"
    )

    print(
        "Variant Rate:",
        round(
            variant_rate * 100,
            2
        ),
        "%"
    )

    print(
        "Measured Lift:",
        round(
            lift,
            2
        ),
        "%"
    )

    print(
        "\nGuardrail Decision:",
        result["decision"]
    )

    print(
        "Experiment Halted:",
        result["experiment_halted"]
    )

    if (
        result["decision"] == "HALT"
        and
        result["experiment_halted"] is True
    ):

        print(
            "\nTASK 10 FAILURE TEST: PASS"
        )

    else:

        print(
            "\nTASK 10 FAILURE TEST: FAIL"
        )


if __name__ == "__main__":

    main()