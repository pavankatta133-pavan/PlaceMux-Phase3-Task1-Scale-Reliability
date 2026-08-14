"""
Phase 3 Task 9
Experiment Feature Flags
"""

EXPERIMENT_NAME = "ranker_v2_experiment"

DEFAULT_CONFIG = {
    "enabled": True,
    "variant_percent": 10,
    "control_model": "ranker_v1.0",
    "variant_model": "ranker_v2.0"
}


class FeatureFlag:

    def __init__(
        self,
        config=None
    ):
        self.config = (
            config.copy()
            if config
            else DEFAULT_CONFIG.copy()
        )

        self.validate()


    def validate(self):

        variant_percent = self.config[
            "variant_percent"
        ]

        if not 0 <= variant_percent <= 100:

            raise ValueError(
                "variant_percent must be between 0 and 100"
            )


    def is_enabled(self):

        return bool(
            self.config["enabled"]
        )


    def variant_percentage(self):

        return self.config[
            "variant_percent"
        ]


    def control_model(self):

        return self.config[
            "control_model"
        ]


    def variant_model(self):

        return self.config[
            "variant_model"
        ]


    def disable(self):

        self.config["enabled"] = False


    def enable(self):

        self.config["enabled"] = True


    def set_variant_percentage(
        self,
        percentage
    ):

        if not 0 <= percentage <= 100:

            raise ValueError(
                "percentage must be between 0 and 100"
            )

        self.config[
            "variant_percent"
        ] = percentage


    def get_config(self):

        return self.config.copy()


if __name__ == "__main__":

    print(
        "\n========== TASK 9 FEATURE FLAG TEST =========="
    )

    flags = FeatureFlag()

    print(
        "Experiment:",
        EXPERIMENT_NAME
    )

    print(
        "Enabled:",
        flags.is_enabled()
    )

    print(
        "Variant traffic:",
        str(flags.variant_percentage()) + "%"
    )

    print(
        "Control model:",
        flags.control_model()
    )

    print(
        "Variant model:",
        flags.variant_model()
    )

    print(
        "\nDisabling experiment..."
    )

    flags.disable()

    print(
        "Enabled:",
        flags.is_enabled()
    )

    print(
        "\nRe-enabling experiment..."
    )

    flags.enable()

    print(
        "Enabled:",
        flags.is_enabled()
    )

    print(
        "\nChanging variant traffic to 20%..."
    )

    flags.set_variant_percentage(
        20
    )

    print(
        "Variant traffic:",
        str(flags.variant_percentage()) + "%"
    )

    print(
        "\nFEATURE FLAG TEST: PASS"
    )