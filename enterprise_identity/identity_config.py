"""
Task 18
SSO, SCIM & Enterprise Identity

Organization and Recruiter Identity Configuration
"""

ORGANIZATIONS = {
    "org_alpha": {
        "name": "Organization Alpha",
        "domain": "alpha.example.com"
    },
    "org_beta": {
        "name": "Organization Beta",
        "domain": "beta.example.com"
    }
}


RECRUITERS = {
    "recruiter_001": {
        "name": "Recruiter One",
        "organization_id": "org_alpha",
        "role": "recruiter"
    },
    "recruiter_002": {
        "name": "Recruiter Two",
        "organization_id": "org_beta",
        "role": "recruiter"
    }
}


def get_organization(
    organization_id
):
    """
    Return organization configuration.
    """

    if organization_id not in ORGANIZATIONS:
        raise ValueError(
            f"Unknown organization: "
            f"{organization_id}"
        )

    return ORGANIZATIONS[
        organization_id
    ]


def get_recruiter(
    recruiter_id
):
    """
    Return recruiter identity.
    """

    if recruiter_id not in RECRUITERS:
        raise ValueError(
            f"Unknown recruiter: "
            f"{recruiter_id}"
        )

    return RECRUITERS[
        recruiter_id
    ]


def get_recruiter_organization(
    recruiter_id
):
    """
    Return the recruiter's current organization.
    """

    recruiter = get_recruiter(
        recruiter_id
    )

    return recruiter[
        "organization_id"
    ]


def get_recruiter_role(
    recruiter_id
):
    """
    Return the recruiter's current role.
    """

    recruiter = get_recruiter(
        recruiter_id
    )

    return recruiter[
        "role"
    ]


def move_recruiter(
    recruiter_id,
    organization_id,
    role="recruiter"
):
    """
    Move a recruiter to another organization.

    The organization and role are updated together
    so personalization can be recalculated from
    the recruiter's current identity context.
    """

    get_organization(
        organization_id
    )

    recruiter = get_recruiter(
        recruiter_id
    )

    recruiter[
        "organization_id"
    ] = organization_id

    recruiter[
        "role"
    ] = role

    return recruiter


def validate_identity(
    recruiter_id
):
    """
    Validate that a recruiter has a valid
    organization and role.
    """

    recruiter = get_recruiter(
        recruiter_id
    )

    organization_id = recruiter[
        "organization_id"
    ]

    role = recruiter[
        "role"
    ]

    get_organization(
        organization_id
    )

    if not role:
        raise ValueError(
            "Recruiter role is required."
        )

    return True


def main():

    print(
        "\n========== TASK 18 IDENTITY CONFIGURATION =========="
    )

    for organization_id in ORGANIZATIONS:

        organization = get_organization(
            organization_id
        )

        print(
            "Organization:",
            organization["name"]
        )

    for recruiter_id in RECRUITERS:

        recruiter = get_recruiter(
            recruiter_id
        )

        print(
            "Recruiter:",
            recruiter_id,
            "| Organization:",
            recruiter["organization_id"],
            "| Role:",
            recruiter["role"]
        )

        validate_identity(
            recruiter_id
        )

    print(
        "\nOrganization configuration: PASS"
    )

    print(
        "Recruiter identity configuration: PASS"
    )

    print(
        "Role configuration: PASS"
    )

    print(
        "Identity validation: PASS"
    )

    print(
        "\nTASK 18 IDENTITY CONFIGURATION: PASS"
    )


if __name__ == "__main__":
    main()