"""
Task 17
Public API, Webhooks & ATS Partner Integrations
API Configuration
"""

API_VERSION = "v1"

API_PREFIX = f"/api/{API_VERSION}"


PARTNERS = {
    "ats_alpha": {
        "name": "ATS Alpha",
        "api_key": "ats_alpha_key",
        "rate_limit": 5,
        "daily_quota": 100
    },
    "ats_beta": {
        "name": "ATS Beta",
        "api_key": "ats_beta_key",
        "rate_limit": 5,
        "daily_quota": 100
    }
}


def get_partner(partner_id):

    if partner_id not in PARTNERS:
        raise ValueError(
            f"Unknown partner: {partner_id}"
        )

    return PARTNERS[partner_id]


def authenticate_partner(api_key):

    for partner_id, partner in PARTNERS.items():

        if partner["api_key"] == api_key:
            return partner_id

    raise ValueError(
        "Invalid API key."
    )


def get_rate_limit(partner_id):

    return get_partner(
        partner_id
    )["rate_limit"]


def get_daily_quota(partner_id):

    return get_partner(
        partner_id
    )["daily_quota"]


def main():

    print(
        "\n========== TASK 17 API CONFIGURATION =========="
    )

    for partner_id, partner in PARTNERS.items():

        print(
            f"\nPartner: {partner_id}"
        )

        print(
            "Rate limit:",
            partner["rate_limit"]
        )

        print(
            "Daily quota:",
            partner["daily_quota"]
        )

    partner_id = authenticate_partner(
        "ats_alpha_key"
    )

    if partner_id != "ats_alpha":
        raise RuntimeError(
            "Partner authentication failed."
        )

    print(
        "\nPartner authentication: PASS"
    )

    try:
        authenticate_partner(
            "invalid_key"
        )
    except ValueError:
        print(
            "Invalid API key rejection: PASS"
        )
    else:
        raise RuntimeError(
            "Invalid API key was accepted."
        )

    print(
        "Partner configuration: PASS"
    )

    print(
        "\nTASK 17 API CONFIGURATION: PASS"
    )


if __name__ == "__main__":
    main()