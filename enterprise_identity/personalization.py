"""
Task 18
SSO, SCIM & Enterprise Identity

Organization- and Recruiter-Scoped Personalization
"""

from enterprise_identity.identity_config import (
    get_recruiter,
)


ORGANIZATION_SIGNALS = {
    "org_alpha": {
        "preferred_locations": [
            "New York",
            "Boston"
        ],
        "preferred_skills": [
            "python",
            "machine learning"
        ],
        "industry": "technology"
    },
    "org_beta": {
        "preferred_locations": [
            "London",
            "Manchester"
        ],
        "preferred_skills": [
            "java",
            "cloud"
        ],
        "industry": "enterprise"
    }
}


RECRUITER_SIGNALS = {
    "recruiter_001": {
        "preferred_experience": 5,
        "communication_style": "technical"
    },
    "recruiter_002": {
        "preferred_experience": 3,
        "communication_style": "business"
    }
}


DEFAULT_RECRUITER_SIGNALS = {
    "preferred_experience": 3,
    "communication_style": "business"
}


ROLE_SIGNALS = {
    "recruiter": {
        "candidate_view": "standard",
        "explanation_level": "detailed"
    },
    "hiring_manager": {
        "candidate_view": "leadership",
        "explanation_level": "summary"
    }
}


def get_organization_signals(
    organization_id
):
    if organization_id not in ORGANIZATION_SIGNALS:
        raise ValueError(
            f"No personalization signals "
            f"for organization: {organization_id}"
        )

    return ORGANIZATION_SIGNALS[
        organization_id
    ].copy()


def get_recruiter_signals(
    recruiter_id
):
    """
    Return recruiter-specific signals.

    Existing recruiters use their stored
    personalization profile.

    Newly provisioned SCIM users receive
    safe default recruiter signals.
    """

    if recruiter_id in RECRUITER_SIGNALS:
        return RECRUITER_SIGNALS[
            recruiter_id
        ].copy()

    if recruiter_id not in {
        "recruiter_001",
        "recruiter_002"
    }:
        return DEFAULT_RECRUITER_SIGNALS.copy()

    raise ValueError(
        f"No recruiter signals for: {recruiter_id}"
    )


def get_role_signals(
    role
):
    if role not in ROLE_SIGNALS:
        raise ValueError(
            f"Unknown role: {role}"
        )

    return ROLE_SIGNALS[
        role
    ].copy()


def get_personalization(
    recruiter_id
):
    """
    Build personalization from the recruiter's
    CURRENT organization and role.

    Organization context is resolved at request
    time, preventing stale organization signals
    from following a recruiter after an org move.
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

    organization_signals = (
        get_organization_signals(
            organization_id
        )
    )

    recruiter_signals = (
        get_recruiter_signals(
            recruiter_id
        )
    )

    role_signals = (
        get_role_signals(
            role
        )
    )

    return {
        "recruiter_id": recruiter_id,
        "organization_id": organization_id,
        "role": role,
        "organization": organization_signals,
        "recruiter": recruiter_signals,
        "role_signals": role_signals
    }


def get_preferred_locations(
    recruiter_id
):
    personalization = get_personalization(
        recruiter_id
    )

    return personalization[
        "organization"
    ][
        "preferred_locations"
    ]


def get_preferred_skills(
    recruiter_id
):
    personalization = get_personalization(
        recruiter_id
    )

    return personalization[
        "organization"
    ][
        "preferred_skills"
    ]


def get_personalized_context(
    recruiter_id
):
    personalization = get_personalization(
        recruiter_id
    )

    return {
        "organization_id": personalization[
            "organization_id"
        ],
        "role": personalization[
            "role"
        ],
        "preferred_locations": personalization[
            "organization"
        ][
            "preferred_locations"
        ],
        "preferred_skills": personalization[
            "organization"
        ][
            "preferred_skills"
        ],
        "preferred_experience": personalization[
            "recruiter"
        ][
            "preferred_experience"
        ],
        "communication_style": personalization[
            "recruiter"
        ][
            "communication_style"
        ],
        "candidate_view": personalization[
            "role_signals"
        ][
            "candidate_view"
        ],
        "explanation_level": personalization[
            "role_signals"
        ][
            "explanation_level"
        ]
    }


def test_org_alpha_personalization():

    context = get_personalized_context(
        "recruiter_001"
    )

    if context[
        "organization_id"
    ] != "org_alpha":
        raise RuntimeError(
            "Recruiter 001 is not scoped "
            "to org_alpha."
        )

    if "New York" not in context[
        "preferred_locations"
    ]:
        raise RuntimeError(
            "Org Alpha location signal missing."
        )

    if "python" not in context[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Org Alpha skill signal missing."
        )

    print(
        "Org Alpha personalization: PASS"
    )


def test_org_beta_personalization():

    context = get_personalized_context(
        "recruiter_002"
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
            "Org Beta location signal missing."
        )

    if "java" not in context[
        "preferred_skills"
    ]:
        raise RuntimeError(
            "Org Beta skill signal missing."
        )

    print(
        "Org Beta personalization: PASS"
    )


def test_recruiter_specific_signals():

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
            "Recruiter 001 signal incorrect."
        )

    if beta[
        "preferred_experience"
    ] != 3:
        raise RuntimeError(
            "Recruiter 002 signal incorrect."
        )

    if alpha[
        "communication_style"
    ] == beta[
        "communication_style"
    ]:
        raise RuntimeError(
            "Recruiter-specific signals "
            "were not differentiated."
        )

    print(
        "Recruiter-specific personalization: PASS"
    )


def test_role_signals():

    context = get_personalized_context(
        "recruiter_001"
    )

    if context[
        "candidate_view"
    ] != "standard":
        raise RuntimeError(
            "Recruiter role view is incorrect."
        )

    if context[
        "explanation_level"
    ] != "detailed":
        raise RuntimeError(
            "Recruiter explanation level "
            "is incorrect."
        )

    print(
        "Role-based personalization: PASS"
    )


def test_no_cross_org_signals():

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
            "are bleeding across organizations."
        )

    if alpha_skills.intersection(
        beta_skills
    ):
        raise RuntimeError(
            "Organization skill signals "
            "are bleeding across organizations."
        )

    print(
        "Cross-organization signal isolation: PASS"
    )


def main():

    print(
        "\n========== TASK 18 PERSONALIZATION =========="
    )

    test_org_alpha_personalization()

    test_org_beta_personalization()

    test_recruiter_specific_signals()

    test_role_signals()

    test_no_cross_org_signals()

    print(
        "\nOrganization-scoped signals: PASS"
    )

    print(
        "Recruiter-scoped signals: PASS"
    )

    print(
        "Role-scoped signals: PASS"
    )

    print(
        "Cross-organization isolation: PASS"
    )

    print(
        "\nTASK 18 PERSONALIZATION: PASS"
    )


if __name__ == "__main__":
    main()