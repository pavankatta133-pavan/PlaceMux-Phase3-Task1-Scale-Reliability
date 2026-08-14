"""
Phase 3 Task 9
Experiment Guardrails
"""

import json
import os


DEFAULT_MIN_SAMPLE_SIZE = 50

DEFAULT_MAX_NEGATIVE_LIFT_PERCENT = -5.0

DEFAULT_MIN_RELEVANT_ACTION_RATE = 0.50


def calculate_rate(
    relevant_actions,
    impressions
):
    """Calculate relevant action rate."""

    if impressions <= 0:
        return 0.0

    return (
        relevant_actions / impressions
    )


def calculate_lift(
    control_rate,
    variant_rate
):
    """Calculate percentage lift."""

    if control_rate <= 0:
        return 0.0

    return (
        (
            variant_rate - control_rate
        )
        / control_rate
    ) * 100


def evaluate_guardrails(
    control_impressions,
    control_relevant_actions,
    variant_impressions,
    variant_relevant_actions,
    min_sample_size=DEFAULT_MIN_SAMPLE_SIZE,
    max_negative_lift_percent=DEFAULT_MAX_NEGATIVE_LIFT_PERCENT,
    min_relevant_action_rate=DEFAULT_MIN_RELEVANT_ACTION_RATE
):
    """
    Compare control and variant metrics.

    The experiment is halted when:

    1. Enough traffic has been observed.
    2. Variant lift is worse than the allowed threshold.
    3. Variant relevance rate falls below the minimum safety level.
    """

    control_rate = calculate_rate(
        control_relevant_actions,
        control_impressions
    )

    variant_rate = calculate_rate(
        variant_relevant_actions,
        variant_impressions
    )

    lift = calculate_lift(
        control_rate,
        variant_rate
    )

    enough_control_data = (
        control_impressions
        >= min_sample_size
    )

    enough_variant_data = (
        variant_impressions
        >= min_sample_size
    )

    sample_size_ready = (
        enough_control_data
        and enough_variant_data
    )

    negative_lift_trigger = (
        lift < max_negative_lift_percent
    )

    relevance_trigger = (
        variant_rate
        < min_relevant_action_rate
    )

    if not sample_size_ready:

        decision = "CONTINUE"

        reason = (
            "Insufficient sample size "
            "for guardrail decision."
        )

    elif (
        negative_lift_trigger
        or relevance_trigger
    ):

        decision = "HALT"

        reasons = []

        if negative_lift_trigger:

            reasons.append(
                "variant lift below allowed threshold"
            )

        if relevance_trigger:

            reasons.append(
                "variant relevant-action rate below safety threshold"
            )

        reason = "; ".join(
            reasons
        )

    else:

        decision = "PASS"

        reason = (
            "Variant is within guardrail limits."
        )

    return {

        "control": {

            "impressions":
                control_impressions,

            "relevant_actions":
                control_relevant_actions,

            "relevant_action_rate":
                round(
                    control_rate,
                    4
                )
        },

        "variant": {

            "impressions":
                variant_impressions,

            "relevant_actions":
                variant_relevant_actions,

            "relevant_action_rate":
                round(
                    variant_rate,
                    4
                )
        },

        "lift_percent":
            round(
                lift,
                2
            ),

        "thresholds": {

            "min_sample_size":
                min_sample_size,

            "max_negative_lift_percent":
                max_negative_lift_percent,

            "min_relevant_action_rate":
                min_relevant_action_rate
        },

        "sample_size_ready":
            sample_size_ready,

        "decision":
            decision,

        "reason":
            reason,

        "experiment_halted":
            decision == "HALT"
    }


def save_guardrail_report(
    report,
    output_file
):
    """Save guardrail decision."""

    os.makedirs(
        os.path.dirname(
            output_file
        ),
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )


if __name__ == "__main__":

    print(
        "\n========== TASK 9 GUARDRAIL TEST =========="
    )

    # -----------------------------------------
    # Safe experiment
    # -----------------------------------------

    safe_result = evaluate_guardrails(
        control_impressions=100,
        control_relevant_actions=80,
        variant_impressions=100,
        variant_relevant_actions=82
    )

    print(
        "\nSAFE EXPERIMENT:"
    )

    print(
        json.dumps(
            safe_result,
            indent=2
        )
    )


    # -----------------------------------------
    # Intentionally bad variant
    # -----------------------------------------

    bad_result = evaluate_guardrails(
        control_impressions=100,
        control_relevant_actions=80,
        variant_impressions=100,
        variant_relevant_actions=30
    )

    print(
        "\nBAD VARIANT:"
    )

    print(
        json.dumps(
            bad_result,
            indent=2
        )
    )


    # -----------------------------------------
    # Validate guardrail behavior
    # -----------------------------------------

    if (
        safe_result["decision"] == "PASS"
        and
        bad_result["decision"] == "HALT"
    ):

        print(
            "\nGUARDRAIL TEST: PASS"
        )

    else:

        print(
            "\nGUARDRAIL TEST: FAIL"
        )