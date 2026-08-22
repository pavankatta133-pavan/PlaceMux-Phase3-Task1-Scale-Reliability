"""
Task 18
SSO, SCIM & Enterprise Identity

SSO Authentication and SCIM Provisioning
"""

from enterprise_identity.identity_config import (
    ORGANIZATIONS,
    RECRUITERS,
    get_organization,
    get_recruiter,
    move_recruiter,
)


class SSOAuthenticationError(Exception):
    """Raised when SSO authentication fails."""


class SCIMProvisioningError(Exception):
    """Raised when SCIM provisioning fails."""


def authenticate_sso(
    email,
    organization_id
):
    """
    Simulate enterprise SSO authentication.

    The email domain must match the configured
    organization domain.
    """

    organization = get_organization(
        organization_id
    )

    domain = organization[
        "domain"
    ]

    expected_suffix = (
        "@"
        + domain
    )

    if not email.endswith(
        expected_suffix
    ):
        raise SSOAuthenticationError(
            "Email domain does not match "
            "the organization."
        )

    for recruiter_id, recruiter in RECRUITERS.items():

        if recruiter.get(
            "email"
        ) == email:

            if recruiter[
                "organization_id"
            ] != organization_id:

                raise SSOAuthenticationError(
                    "Recruiter organization "
                    "does not match SSO organization."
                )

            return {
                "authenticated": True,
                "recruiter_id": recruiter_id,
                "organization_id": organization_id,
                "role": recruiter["role"]
            }

    raise SSOAuthenticationError(
        "Recruiter is not provisioned."
    )


def provision_recruiter(
    recruiter_id,
    email,
    organization_id,
    role="recruiter"
):
    """
    Simulate SCIM user provisioning.

    The user is created or updated inside the
    requested organization.
    """

    get_organization(
        organization_id
    )

    if "@" not in email:
        raise SCIMProvisioningError(
            "A valid email address is required."
        )

    expected_domain = ORGANIZATIONS[
        organization_id
    ][
        "domain"
    ]

    if not email.endswith(
        "@"
        + expected_domain
    ):
        raise SCIMProvisioningError(
            "Email domain does not match "
            "the organization."
        )

    if recruiter_id in RECRUITERS:

        move_recruiter(
            recruiter_id,
            organization_id,
            role
        )

        recruiter = get_recruiter(
            recruiter_id
        )

    else:

        recruiter = {
            "name": recruiter_id,
            "email": email,
            "organization_id": organization_id,
            "role": role
        }

        RECRUITERS[
            recruiter_id
        ] = recruiter

    recruiter[
        "email"
    ] = email

    recruiter[
        "organization_id"
    ] = organization_id

    recruiter[
        "role"
    ] = role

    return recruiter


def deprovision_recruiter(
    recruiter_id
):
    """
    Remove a recruiter from the active
    enterprise identity directory.
    """

    if recruiter_id not in RECRUITERS:
        raise SCIMProvisioningError(
            "Recruiter is not provisioned."
        )

    del RECRUITERS[
        recruiter_id
    ]

    return True


def update_recruiter(
    recruiter_id,
    email=None,
    organization_id=None,
    role=None
):
    """
    Update an existing provisioned recruiter.
    """

    recruiter = get_recruiter(
        recruiter_id
    )

    if organization_id is not None:

        get_organization(
            organization_id
        )

        expected_domain = ORGANIZATIONS[
            organization_id
        ][
            "domain"
        ]

        if email is None:
            email = recruiter.get(
                "email",
                ""
            )

        if not email.endswith(
            "@"
            + expected_domain
        ):
            raise SCIMProvisioningError(
                "Email domain does not match "
                "the new organization."
            )

        move_recruiter(
            recruiter_id,
            organization_id,
            role or recruiter["role"]
        )

        recruiter = get_recruiter(
            recruiter_id
        )

    if email is not None:
        recruiter[
            "email"
        ] = email

    if role is not None:
        recruiter[
            "role"
        ] = role

    return recruiter


def test_sso_success():

    RECRUITERS[
        "recruiter_001"
    ][
        "email"
    ] = "recruiter1@alpha.example.com"

    result = authenticate_sso(
        "recruiter1@alpha.example.com",
        "org_alpha"
    )

    if not result[
        "authenticated"
    ]:
        raise RuntimeError(
            "SSO authentication failed."
        )

    if result[
        "organization_id"
    ] != "org_alpha":
        raise RuntimeError(
            "Incorrect SSO organization."
        )

    print(
        "SSO authentication: PASS"
    )


def test_sso_wrong_domain():

    try:

        authenticate_sso(
            "recruiter1@beta.example.com",
            "org_alpha"
        )

    except SSOAuthenticationError:

        print(
            "SSO organization-domain validation: PASS"
        )

    else:

        raise RuntimeError(
            "SSO accepted an incorrect organization domain."
        )


def test_scim_provisioning():

    recruiter = provision_recruiter(
        recruiter_id="recruiter_003",
        email="recruiter3@alpha.example.com",
        organization_id="org_alpha",
        role="recruiter"
    )

    if recruiter[
        "organization_id"
    ] != "org_alpha":
        raise RuntimeError(
            "SCIM provisioning assigned "
            "the wrong organization."
        )

    if recruiter[
        "role"
    ] != "recruiter":
        raise RuntimeError(
            "SCIM provisioning assigned "
            "the wrong role."
        )

    print(
        "SCIM provisioning: PASS"
    )


def test_scim_update():

    recruiter = update_recruiter(
        recruiter_id="recruiter_003",
        role="hiring_manager"
    )

    if recruiter[
        "role"
    ] != "hiring_manager":
        raise RuntimeError(
            "SCIM role update failed."
        )

    print(
        "SCIM attribute update: PASS"
    )


def test_scim_organization_move():

    recruiter = update_recruiter(
        recruiter_id="recruiter_003",
        email="recruiter3@beta.example.com",
        organization_id="org_beta",
        role="recruiter"
    )

    if recruiter[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "SCIM organization move failed."
        )

    if recruiter[
        "email"
    ] != "recruiter3@beta.example.com":
        raise RuntimeError(
            "SCIM email update failed."
        )

    print(
        "SCIM organization move: PASS"
    )


def test_scim_invalid_domain():

    try:

        provision_recruiter(
            recruiter_id="recruiter_004",
            email="recruiter4@alpha.example.com",
            organization_id="org_beta",
            role="recruiter"
        )

    except SCIMProvisioningError:

        print(
            "SCIM domain validation: PASS"
        )

    else:

        raise RuntimeError(
            "SCIM accepted a mismatched organization domain."
        )


def test_deprovisioning():

    provision_recruiter(
        recruiter_id="recruiter_005",
        email="recruiter5@alpha.example.com",
        organization_id="org_alpha",
        role="recruiter"
    )

    deprovision_recruiter(
        "recruiter_005"
    )

    if "recruiter_005" in RECRUITERS:
        raise RuntimeError(
            "SCIM deprovisioning failed."
        )

    print(
        "SCIM deprovisioning: PASS"
    )


def test_sso_after_scim_move():

    result = authenticate_sso(
        "recruiter3@beta.example.com",
        "org_beta"
    )

    if not result[
        "authenticated"
    ]:
        raise RuntimeError(
            "SSO failed after SCIM organization move."
        )

    if result[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "SSO retained stale organization context."
        )

    print(
        "SSO after SCIM organization move: PASS"
    )


def main():

    print(
        "\n========== TASK 18 SSO + SCIM =========="
    )

    test_sso_success()

    test_sso_wrong_domain()

    test_scim_provisioning()

    test_scim_update()

    test_scim_organization_move()

    test_scim_invalid_domain()

    test_deprovisioning()

    test_sso_after_scim_move()

    print(
        "\nSSO authentication: PASS"
    )

    print(
        "SSO organization validation: PASS"
    )

    print(
        "SCIM provisioning: PASS"
    )

    print(
        "SCIM attribute update: PASS"
    )

    print(
        "SCIM organization move: PASS"
    )

    print(
        "SCIM domain validation: PASS"
    )

    print(
        "SCIM deprovisioning: PASS"
    )

    print(
        "SSO/SCIM synchronization: PASS"
    )

    print(
        "\nTASK 18 SSO + SCIM: PASS"
    )


if __name__ == "__main__":
    main()