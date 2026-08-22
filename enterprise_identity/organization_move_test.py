"""
Task 18
SSO, SCIM & Enterprise Identity

Organization Move and Personalization Isolation Test
"""

from enterprise_identity.identity_config import (
    get_recruiter,
    get_recruiter_organization,
    move_recruiter,
)

from enterprise_identity.personalization import (
    get_personalized_context,
)


def test_initial_organization():

    recruiter_id = "recruiter_001"

    organization = get_recruiter_organization(
        recruiter_id
    )

    if organization != "org_alpha":
        raise RuntimeError(
            "Recruiter 001 should initially "
            "belong to org_alpha."
        )

    print(
        "Initial organization: PASS"
    )


def test_initial_personalization():

    recruiter_id = "recruiter_001"

    context = get_personalized_context(
        recruiter_id
    )

    if context[
        "organization_id"
    ] != "org_alpha":
        raise RuntimeError(
            "Initial personalization is "
            "not scoped to org_alpha."
        )

    if "New York" not in context[
        "preferred_locations"
    ]:
        raise RuntimeError(
            "Org Alpha location signal "
            "is missing."
        )

    if "python" not in context[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Org Alpha skill signal "
            "is missing."
        )

    print(
        "Initial personalization: PASS"
    )


def test_move_to_new_organization():

    recruiter_id = "recruiter_001"

    move_recruiter(
        recruiter_id,
        "org_beta",
        role="recruiter"
    )

    organization = get_recruiter_organization(
        recruiter_id
    )

    if organization != "org_beta":
        raise RuntimeError(
            "Recruiter was not moved "
            "to org_beta."
        )

    print(
        "Organization move: PASS"
    )


def test_new_organization_personalization():

    recruiter_id = "recruiter_001"

    context = get_personalized_context(
        recruiter_id
    )

    if context[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "Personalization did not switch "
            "to org_beta."
        )

    if "London" not in context[
        "preferred_locations"
    ]:
        raise RuntimeError(
            "Org Beta location signal "
            "is missing."
        )

    if "java" not in context[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Org Beta skill signal "
            "is missing."
        )

    print(
        "New organization personalization: PASS"
    )


def test_old_organization_signals_removed():

    recruiter_id = "recruiter_001"

    context = get_personalized_context(
        recruiter_id
    )

    locations = context[
        "preferred_locations"
    ]

    skills = context[
        "preferred_skills"
    ]

    if "New York" in locations:
        raise RuntimeError(
            "Old organization location "
            "signal leaked after move."
        )

    if "Boston" in locations:
        raise RuntimeError(
            "Old organization location "
            "signal leaked after move."
        )

    if "python" in skills:
        raise RuntimeError(
            "Old organization skill "
            "signal leaked after move."
        )

    if "machine learning" in skills:
        raise RuntimeError(
            "Old organization skill "
            "signal leaked after move."
        )

    print(
        "Old organization signal removal: PASS"
    )


def test_recruiter_specific_signal_preserved():

    recruiter_id = "recruiter_001"

    context = get_personalized_context(
        recruiter_id
    )

    if context[
        "preferred_experience"
    ] != 5:
        raise RuntimeError(
            "Recruiter-specific signal "
            "was incorrectly removed."
        )

    if context[
        "communication_style"
    ] != "technical":
        raise RuntimeError(
            "Recruiter-specific communication "
            "style was incorrectly changed."
        )

    print(
        "Recruiter-specific signal preservation: PASS"
    )


def test_role_signal_preserved():

    recruiter_id = "recruiter_001"

    context = get_personalized_context(
        recruiter_id
    )

    if context[
        "role"
    ] != "recruiter":
        raise RuntimeError(
            "Recruiter role changed unexpectedly."
        )

    if context[
        "candidate_view"
    ] != "standard":
        raise RuntimeError(
            "Role-specific candidate view "
            "changed unexpectedly."
        )

    if context[
        "explanation_level"
    ] != "detailed":
        raise RuntimeError(
            "Role-specific explanation level "
            "changed unexpectedly."
        )

    print(
        "Role signal preservation: PASS"
    )


def test_second_organization_isolation():

    recruiter_id = "recruiter_002"

    context = get_personalized_context(
        recruiter_id
    )

    if context[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "Recruiter 002 is not scoped "
            "to org_beta."
        )

    if "London" not in context[
        "preferred_locations"
    ]:
        raise RuntimeError(
            "Recruiter 002 lost Beta "
            "organization signals."
        )

    if "java" not in context[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Recruiter 002 lost Beta "
            "skill signals."
        )

    print(
        "Second organization isolation: PASS"
    )


def test_no_alpha_beta_signal_bleed():

    recruiter_001 = get_personalized_context(
        "recruiter_001"
    )

    recruiter_002 = get_personalized_context(
        "recruiter_002"
    )

    alpha_locations = {
        "New York",
        "Boston"
    }

    alpha_skills = {
        "python",
        "machine learning"
    }

    beta_locations = set(
        recruiter_001[
            "preferred_locations"
        ]
    )

    beta_skills = set(
        recruiter_001[
            "preferred_skills"
        ]
    )

    if alpha_locations.intersection(
        beta_locations
    ):
        raise RuntimeError(
            "Alpha location signals "
            "bled into Beta context."
        )

    if alpha_skills.intersection(
        beta_skills
    ):
        raise RuntimeError(
            "Alpha skill signals "
            "bled into Beta context."
        )

    if recruiter_002[
        "organization_id"
    ] != "org_beta":
        raise RuntimeError(
            "Recruiter 002 organization "
            "scope is incorrect."
        )

    print(
        "Cross-organization signal isolation: PASS"
    )


def main():

    print(
        "\n========== TASK 18 ORGANIZATION MOVE TEST =========="
    )

    test_initial_organization()

    test_initial_personalization()

    test_move_to_new_organization()

    test_new_organization_personalization()

    test_old_organization_signals_removed()

    test_recruiter_specific_signal_preserved()

    test_role_signal_preserved()

    test_second_organization_isolation()

    test_no_alpha_beta_signal_bleed()

    print(
        "\nInitial organization: PASS"
    )

    print(
        "Organization move: PASS"
    )

    print(
        "New organization personalization: PASS"
    )

    print(
        "Old organization signal removal: PASS"
    )

    print(
        "Recruiter signal preservation: PASS"
    )

    print(
        "Role signal preservation: PASS"
    )

    print(
        "Cross-organization isolation: PASS"
    )

    print(
        "\nTASK 18 ORGANIZATION MOVE: PASS"
    )


if __name__ == "__main__":
    main()