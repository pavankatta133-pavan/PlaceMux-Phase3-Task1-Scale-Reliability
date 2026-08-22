"""
Task 16
Enterprise Multi-Tenancy & RBAC
Tenant Configuration

Per-tenant thresholds and weights are stored as configuration,
not implemented as code forks.
"""

TENANT_CONFIG = {
    "tenant_alpha": {
        "name": "Enterprise Alpha",
        "matching": {
            "threshold": 0.70,
            "weights": {
                "skills": 0.60,
                "experience": 0.25,
                "education": 0.15
            }
        }
    },
    "tenant_beta": {
        "name": "Enterprise Beta",
        "matching": {
            "threshold": 0.85,
            "weights": {
                "skills": 0.40,
                "experience": 0.40,
                "education": 0.20
            }
        }
    }
}


def get_tenant_config(tenant_id):
    """
    Return configuration for a tenant.

    Unknown tenants are rejected rather than receiving
    another tenant's configuration.
    """

    if tenant_id not in TENANT_CONFIG:
        raise ValueError(
            f"Unknown tenant: {tenant_id}"
        )

    return TENANT_CONFIG[tenant_id]


def get_matching_config(tenant_id):
    """
    Return only the matching configuration for a tenant.
    """

    config = get_tenant_config(
        tenant_id
    )

    return config["matching"]


def validate_tenant_config(tenant_id):
    """
    Validate threshold and matching weights.
    """

    matching = get_matching_config(
        tenant_id
    )

    threshold = matching["threshold"]
    weights = matching["weights"]

    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "Threshold must be between 0 and 1."
        )

    required_weights = {
        "skills",
        "experience",
        "education"
    }

    if set(weights.keys()) != required_weights:
        raise ValueError(
            "Invalid matching weight configuration."
        )

    total_weight = sum(
        weights.values()
    )

    if abs(total_weight - 1.0) > 1e-9:
        raise ValueError(
            "Matching weights must sum to 1.0."
        )

    for feature, weight in weights.items():

        if not 0.0 <= weight <= 1.0:
            raise ValueError(
                f"Invalid weight for {feature}."
            )

    return True


def validate_all_tenants():
    """
    Validate every configured tenant.
    """

    for tenant_id in TENANT_CONFIG:

        validate_tenant_config(
            tenant_id
        )

    return True


def main():

    print(
        "\n========== TASK 16 TENANT CONFIGURATION =========="
    )

    validate_all_tenants()

    for tenant_id in TENANT_CONFIG:

        config = get_matching_config(
            tenant_id
        )

        print(
            f"\nTenant: {tenant_id}"
        )

        print(
            "Threshold:",
            config["threshold"]
        )

        print(
            "Weights:",
            config["weights"]
        )

    alpha = get_matching_config(
        "tenant_alpha"
    )

    beta = get_matching_config(
        "tenant_beta"
    )

    if alpha == beta:
        raise RuntimeError(
            "Tenant configurations must differ."
        )

    print(
        "\nTenant-specific configuration: PASS"
    )

    print(
        "Configuration validation: PASS"
    )

    print(
        "No code forks required: PASS"
    )

    print(
        "\nTASK 16 TENANT CONFIGURATION: PASS"
    )


if __name__ == "__main__":
    main()