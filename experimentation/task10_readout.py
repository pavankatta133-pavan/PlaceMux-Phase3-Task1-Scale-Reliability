"""
Phase 3 Task 10
Honest Experiment Readout

Calculates:
- Effect size
- Relative lift
- Statistical significance
- Confidence interval
- Guardrails
- SHIP / DO NOT SHIP decision
"""

import json
import math
import os


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PREREG_FILE = os.path.join(
    PROJECT_ROOT,
    "experimentation",
    "preregistration.json"
)

EVENT_FILE = os.path.join(
    PROJECT_ROOT,
    "experimentation",
    "reports",
    "task10_experiment_events.jsonl"
)

REPORT_FILE = os.path.join(
    PROJECT_ROOT,
    "experimentation",
    "reports",
    "task10_readout.json"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_events():

    events = []

    with open(
        EVENT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if line:

                events.append(
                    json.loads(line)
                )

    return events


def calculate_metrics(events):

    result = {}

    for group in [
        "control",
        "variant"
    ]:

        rows = [
            event
            for event in events
            if event["group"] == group
        ]

        impressions = sum(
            event["impressions"]
            for event in rows
        )

        relevant_actions = sum(
            event["relevant_actions"]
            for event in rows
        )

        rate = (
            relevant_actions
            / impressions
            if impressions
            else 0
        )

        result[group] = {

            "users":
                len(rows),

            "impressions":
                impressions,

            "relevant_actions":
                relevant_actions,

            "rate":
                rate
        }

    return result


def normal_cdf(x):

    return (
        0.5
        * (
            1
            + math.erf(
                x / math.sqrt(2)
            )
        )
    )


def two_proportion_z_test(
    control_success,
    control_total,
    variant_success,
    variant_total
):

    p1 = (
        control_success
        / control_total
    )

    p2 = (
        variant_success
        / variant_total
    )

    pooled = (
        (
            control_success
            + variant_success
        )
        /
        (
            control_total
            + variant_total
        )
    )

    standard_error = math.sqrt(
        pooled
        * (1 - pooled)
        * (
            (1 / control_total)
            + (1 / variant_total)
        )
    )

    if standard_error == 0:

        return {
            "z_score": 0,
            "p_value": 1
        }

    z_score = (
        p2 - p1
    ) / standard_error

    p_value = (
        2
        * (
            1
            - normal_cdf(
                abs(z_score)
            )
        )
    )

    return {
        "z_score":
            z_score,

        "p_value":
            p_value
    }


def confidence_interval(
    control_rate,
    variant_rate,
    control_total,
    variant_total
):

    difference = (
        variant_rate
        - control_rate
    )

    standard_error = math.sqrt(

        (
            control_rate
            * (1 - control_rate)
            / control_total
        )

        +

        (
            variant_rate
            * (1 - variant_rate)
            / variant_total
        )
    )

    margin = (
        1.96
        * standard_error
    )

    return {

        "lower":
            difference - margin,

        "upper":
            difference + margin
    }


def main():

    print(
        "\n========== TASK 10 READOUT =========="
    )

    prereg = load_json(
        PREREG_FILE
    )

    events = load_events()

    metrics = calculate_metrics(
        events
    )

    control = metrics[
        "control"
    ]

    variant = metrics[
        "variant"
    ]

    control_rate = control[
        "rate"
    ]

    variant_rate = variant[
        "rate"
    ]

    absolute_effect = (
        variant_rate
        - control_rate
    )

    relative_lift = (

        (
            variant_rate
            - control_rate
        )
        / control_rate
        * 100

        if control_rate > 0
        else 0
    )

    significance = (
        two_proportion_z_test(

            control[
                "relevant_actions"
            ],

            control[
                "impressions"
            ],

            variant[
                "relevant_actions"
            ],

            variant[
                "impressions"
            ]
        )
    )

    ci = confidence_interval(

        control_rate,
        variant_rate,

        control[
            "impressions"
        ],

        variant[
            "impressions"
        ]
    )

    p_value = significance[
        "p_value"
    ]

    alpha = prereg[
        "significance_level"
    ]

    minimum_lift = prereg[
        "minimum_lift_percent"
    ]

    minimum_sample = prereg[
        "minimum_sample_size_per_group"
    ]

    minimum_rate = prereg[
        "guardrail"
    ][
        "minimum_relevant_action_rate"
    ]

    maximum_negative_lift = prereg[
        "guardrail"
    ][
        "maximum_negative_lift_percent"
    ]

    sample_ready = (

        control[
            "impressions"
        ] >= minimum_sample

        and

        variant[
            "impressions"
        ] >= minimum_sample
    )

    statistically_significant = (
        p_value < alpha
    )

    lift_pass = (
        relative_lift
        >= minimum_lift
    )

    safety_pass = (
        variant_rate
        >= minimum_rate
    )

    negative_lift_guardrail = (
        relative_lift
        < maximum_negative_lift
    )

    guardrails_pass = (
        safety_pass
        and
        not negative_lift_guardrail
    )

    ship = (

        sample_ready

        and

        statistically_significant

        and

        lift_pass

        and

        guardrails_pass
    )

    decision = (
        "SHIP"
        if ship
        else
        "DO NOT SHIP"
    )

    if decision == "SHIP":

        reason = (
            "Variant achieved the "
            "pre-registered lift target, "
            "statistical significance, "
            "sample-size requirement, "
            "and passed guardrails."
        )

    else:

        reasons = []

        if not sample_ready:

            reasons.append(
                "minimum sample size not reached"
            )

        if not statistically_significant:

            reasons.append(
                "result is not statistically significant"
            )

        if not lift_pass:

            reasons.append(
                "variant lift is below the "
                "pre-registered target"
            )

        if not guardrails_pass:

            reasons.append(
                "variant failed safety guardrails"
            )

        reason = "; ".join(
            reasons
        )

    report = {

        "experiment_id":
            prereg[
                "experiment_id"
            ],

        "hypothesis":
            prereg[
                "hypothesis"
            ],

        "primary_metric":
            prereg[
                "primary_metric"
            ],

        "control":
            {
                "impressions":
                    control[
                        "impressions"
                    ],

                "relevant_actions":
                    control[
                        "relevant_actions"
                    ],

                "relevant_action_rate":
                    round(
                        control_rate,
                        4
                    )
            },

        "variant":
            {
                "impressions":
                    variant[
                        "impressions"
                    ],

                "relevant_actions":
                    variant[
                        "relevant_actions"
                    ],

                "relevant_action_rate":
                    round(
                        variant_rate,
                        4
                    )
            },

        "effect_size":
            {
                "absolute_difference":
                    round(
                        absolute_effect,
                        4
                    ),

                "relative_lift_percent":
                    round(
                        relative_lift,
                        2
                    )
            },

        "statistical_significance":
            {
                "z_score":
                    round(
                        significance[
                            "z_score"
                        ],
                        4
                    ),

                "p_value":
                    round(
                        p_value,
                        6
                    ),

                "alpha":
                    alpha,

                "statistically_significant":
                    statistically_significant
            },

        "confidence_interval_95_percent":
            {
                "lower":
                    round(
                        ci[
                            "lower"
                        ],
                        4
                    ),

                "upper":
                    round(
                        ci[
                            "upper"
                        ],
                        4
                    )
            },

        "guardrails":
            {
                "sample_size_ready":
                    sample_ready,

                "minimum_lift_pass":
                    lift_pass,

                "safety_rate_pass":
                    safety_pass,

                "negative_lift_detected":
                    negative_lift_guardrail,

                "guardrails_pass":
                    guardrails_pass
            },

        "decision":
            decision,

        "reason":
            reason,

        "honest_readout":
            True
    }

    os.makedirs(
        os.path.dirname(
            REPORT_FILE
        ),
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

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
        "Absolute Effect:",
        round(
            absolute_effect * 100,
            2
        ),
        "%"
    )

    print(
        "Relative Lift:",
        round(
            relative_lift,
            2
        ),
        "%"
    )

    print(
        "P-value:",
        round(
            p_value,
            6
        )
    )

    print(
        "95% CI:",
        round(
            ci["lower"] * 100,
            2
        ),
        "to",
        round(
            ci["upper"] * 100,
            2
        ),
        "%"
    )

    print(
        "\nStatistically Significant:",
        statistically_significant
    )

    print(
        "Guardrails Pass:",
        guardrails_pass
    )

    print(
        "\nFINAL DECISION:",
        decision
    )

    print(
        "Reason:",
        reason
    )

    print(
        "\nReadout saved to:"
    )

    print(
        REPORT_FILE
    )

    print(
        "\nTASK 10 READOUT: PASS"
    )


if __name__ == "__main__":

    main()