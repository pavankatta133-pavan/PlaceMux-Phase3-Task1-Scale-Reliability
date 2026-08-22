"""
Task 18
SSO, SCIM & Enterprise Identity

Final End-to-End Integration Test
"""

from enterprise_identity.identity_config import (
    RECRUITERS,
    get_recruiter,
    get_recruiter_organization,
    move_recruiter,
)

from enterprise_identity.personalization import (
    get_personalized_context,
)

from enterprise_identity.sso_scim import (
    authenticate_sso,
    provision_recruiter,
    update_recruiter,
)


def test_identity_configuration():

    recruiter_001 = get_recruiter(
        "recruiter_001"
    )

    recruiter_002 = get_recruiter(
        "recruiter_002"
    )

    if recruiter_001[
        "organization_id"
    ] != "org_alpha":
        raise RuntimeError(
            "Recruiter 001 identity configuration "
            "is incorrect."
        )

    if recruiter_002[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "Recruiter 002 identity configuration "
            "is incorrect."
        )

    print(
        "Identity configuration: PASS"
    )


def test_organization_personalization():

    alpha = get_personalized_context(
        "recruiter_001"
    )

    beta = get_personalized_context(
        "recruiter_002"
    )

    if alpha[
        "organization_id"
    ] != "org_alpha":
        raise RuntimeError(
            "Alpha personalization is not "
            "organization scoped."
        )

    if beta[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "Beta personalization is not "
            "organization scoped."
        )

    if "python" not in alpha[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Alpha organization skill "
            "signal is missing."
        )

    if "java" not in beta[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Beta organization skill "
            "signal is missing."
        )

    print(
        "Organization-scoped personalization: PASS"
    )


def test_recruiter_personalization():

    alpha = get_personalized_context(
        "recruiter_001"
    )

    beta = get_personalized_context(
        "recruiter_002"
    )

    if alpha[
        "preferred_experience"
    ] != 5:
        raise RuntimeError(
            "Recruiter 001 personalization "
            "is incorrect."
        )

    if beta[
        "preferred_experience"
    ] != 3:
        raise RuntimeError(
            "Recruiter 002 personalization "
            "is incorrect."
        )

    if alpha[
        "communication_style"
    ] == beta[
        "communication_style"
    ]:
        raise RuntimeError(
            "Recruiter-specific personalization "
            "was not isolated."
        )

    print(
        "Recruiter-scoped personalization: PASS"
    )


def test_cross_organization_isolation():

    alpha = get_personalized_context(
        "recruiter_001"
    )

    beta = get_personalized_context(
        "recruiter_002"
    )

    alpha_locations = set(
        alpha[
            "preferred_locations"
        ]
    )

    beta_locations = set(
        beta[
            "preferred_locations"
        ]
    )

    alpha_skills = set(
        alpha[
            "preferred_skills"
        ]
    )

    beta_skills = set(
        beta[
            "preferred_skills"
        ]
    )

    if alpha_locations.intersection(
        beta_locations
    ):
        raise RuntimeError(
            "Organization location signals "
            "bled across organizations."
        )

    if alpha_skills.intersection(
        beta_skills
    ):
        raise RuntimeError(
            "Organization skill signals "
            "bled across organizations."
        )

    print(
        "Cross-organization isolation: PASS"
    )


def test_sso_authentication():

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
            "SSO returned the wrong organization."
        )

    print(
        "SSO authentication: PASS"
    )


def test_scim_provisioning():

    recruiter = provision_recruiter(
        recruiter_id="integration_user",
        email="integration@alpha.example.com",
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


def test_scim_move():

    recruiter = update_recruiter(
        recruiter_id="integration_user",
        email="integration@beta.example.com",
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
    ] != "integration@beta.example.com":
        raise RuntimeError(
            "SCIM email update failed."
        )

    print(
        "SCIM organization move: PASS"
    )


def test_personalization_after_scim_move():

    context = get_personalized_context(
        "integration_user"
    )

    if context[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "Personalization retained the "
            "old organization."
        )

    if "London" not in context[
        "preferred_locations"
    ]:
        raise RuntimeError(
            "Beta location personalization "
            "was not applied."
        )

    if "java" not in context[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Beta skill personalization "
            "was not applied."
        )

    print(
        "Post-SCIM personalization: PASS"
    )


def test_old_signals_removed():

    context = get_personalized_context(
        "integration_user"
    )

    old_locations = {
        "New York",
        "Boston"
    }

    old_skills = {
        "python",
        "machine learning"
    }

    current_locations = set(
        context[
            "preferred_locations"
        ]
    )

    current_skills = set(
        context[
            "preferred_skills"
        ]
    )

    if old_locations.intersection(
        current_locations
    ):
        raise RuntimeError(
            "Old organization location "
            "signals remained after the move."
        )

    if old_skills.intersection(
        current_skills
    ):
        raise RuntimeError(
            "Old organization skill "
            "signals remained after the move."
        )

    print(
        "Old organization signal cleanup: PASS"
    )


def test_sso_after_scim_move():

    result = authenticate_sso(
        "integration@beta.example.com",
        "org_beta"
    )

    if not result[
        "authenticated"
    ]:
        raise RuntimeError(
            "SSO failed after SCIM move."
        )

    if result[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "SSO retained stale organization "
            "context after SCIM move."
        )

    print(
        "SSO after SCIM move: PASS"
    )


def test_final_isolation():

    integration_context = (
        get_personalized_context(
            "integration_user"
        )
    )

    alpha_context = (
        get_personalized_context(
            "recruiter_001"
        )
    )

    if integration_context[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "Integration user is not scoped "
            "to org_beta."
        )

    if alpha_context[
        "organization_id"
    ] != "org_alpha":
        raise RuntimeError(
            "Alpha recruiter organization "
            "scope was corrupted."
        )

    if "python" not in alpha_context[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Alpha personalization was corrupted."
        )

    if "java" not in integration_context[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Beta personalization was corrupted."
        )

    print(
        "Final organization isolation: PASS"
    )


def main():

    print(
        "\n========== TASK 18 INTEGRATION TEST =========="
    )

    test_identity_configuration()

    test_organization_personalization()

    test_recruiter_personalization()

    test_cross_organization_isolation()

    test_sso_authentication()

    test_scim_provisioning()

    test_scim_move()

    test_personalization_after_scim_move()

    test_old_signals_removed()

    test_sso_after_scim_move()

    test_final_isolation()

    print(
        "\nIdentity configuration: PASS"
    )

    print(
        "Organization-scoped personalization: PASS"
    )

    print(
        "Recruiter-scoped personalization: PASS"
    )

    print(
        "Cross-organization isolation: PASS"
    )

    print(
        "SSO authentication: PASS"
    )

    print(
        "SCIM provisioning: PASS"
    )

    print(
        "SCIM organization move: PASS"
    )

    print(
        "Post-move personalization: PASS"
    )

    print(
        "Old signal cleanup: PASS"
    )

    print(
        "SSO/SCIM synchronization: PASS"
    )

    print(
        "Final tenant isolation: PASS"
    )

    print(
        "\nTASK 18 INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":
    main()