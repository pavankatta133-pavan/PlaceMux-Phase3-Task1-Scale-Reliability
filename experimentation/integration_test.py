"""
Phase 3 Task 9
Experiment Integration Test
"""

from experimentation.guardrails import (
    evaluate_guardrails
)


def main():

    print(
        "\n========== TASK 9 INTEGRATION TEST =========="
    )

    # Safe scenario
    safe = evaluate_guardrails(
        control_impressions=100,
        control_relevant_actions=80,
        variant_impressions=100,
        variant_relevant_actions=82
    )

    print(
        "\nSafe scenario:"
    )

    print(
        "Decision:",
        safe["decision"]
    )


    # Bad variant scenario
    bad = evaluate_guardrails(
        control_impressions=100,
        control_relevant_actions=80,
        variant_impressions=100,
        variant_relevant_actions=30
    )

    print(
        "\nBad variant scenario:"
    )

    print(
        "Decision:",
        bad["decision"]
    )

    print(
        "Experiment halted:",
        bad["experiment_halted"]
    )


    if (
        safe["decision"] == "PASS"
        and
        bad["decision"] == "HALT"
        and
        bad["experiment_halted"] is True
    ):

        print(
            "\nTASK 9 INTEGRATION TEST: PASS"
        )

    else:

        print(
            "\nTASK 9 INTEGRATION TEST: FAIL"
        )


if __name__ == "__main__":

    main()