"""
Task 17
Public API, Webhooks & ATS Partner Integrations

Partner Rate Limiting and Quotas
"""

from public_api.api_config import (
    get_partner,
    authenticate_partner
)


class RateLimitExceeded(Exception):
    """Raised when the partner exceeds its rate limit."""


class QuotaExceeded(Exception):
    """Raised when the partner exceeds its daily quota."""


class RateLimiter:

    def __init__(self):
        self.requests = {}
        self.daily_usage = {}

    def _ensure_partner(self, partner_id):

        get_partner(partner_id)

        if partner_id not in self.requests:
            self.requests[partner_id] = 0

        if partner_id not in self.daily_usage:
            self.daily_usage[partner_id] = 0

    def check_request(self, partner_id):

        self._ensure_partner(
            partner_id
        )

        partner = get_partner(
            partner_id
        )

        if (
            self.requests[partner_id]
            >= partner["rate_limit"]
        ):
            raise RateLimitExceeded(
                f"Rate limit exceeded for "
                f"{partner_id}."
            )

        if (
            self.daily_usage[partner_id]
            >= partner["daily_quota"]
        ):
            raise QuotaExceeded(
                f"Daily quota exceeded for "
                f"{partner_id}."
            )

    def record_request(self, partner_id):

        self.check_request(
            partner_id
        )

        self.requests[partner_id] += 1
        self.daily_usage[partner_id] += 1

    def get_usage(self, partner_id):

        self._ensure_partner(
            partner_id
        )

        partner = get_partner(
            partner_id
        )

        return {
            "partner_id": partner_id,
            "requests": self.requests[partner_id],
            "rate_limit": partner["rate_limit"],
            "daily_usage": self.daily_usage[
                partner_id
            ],
            "daily_quota": partner["daily_quota"]
        }

    def reset_rate_window(self):

        for partner_id in self.requests:
            self.requests[partner_id] = 0

    def reset_daily_quota(self):

        for partner_id in self.daily_usage:
            self.daily_usage[partner_id] = 0


def create_limiter():

    return RateLimiter()


def test_rate_limit():

    limiter = create_limiter()

    partner_id = authenticate_partner(
        "ats_alpha_key"
    )

    limit = get_partner(
        partner_id
    )["rate_limit"]

    for _ in range(limit):

        limiter.record_request(
            partner_id
        )

    usage = limiter.get_usage(
        partner_id
    )

    if usage["requests"] != limit:
        raise RuntimeError(
            "Rate-limit usage was not recorded correctly."
        )

    try:

        limiter.record_request(
            partner_id
        )

    except RateLimitExceeded:

        print(
            "Rate limit enforcement: PASS"
        )

    else:

        raise RuntimeError(
            "Rate limit was not enforced."
        )


def test_quota_limit():

    limiter = create_limiter()

    partner_id = authenticate_partner(
        "ats_beta_key"
    )

    partner = get_partner(
        partner_id
    )

    # For testing, use the configured quota
    # and temporarily simulate quota exhaustion.
    limiter.daily_usage[
        partner_id
    ] = partner["daily_quota"]

    try:

        limiter.record_request(
            partner_id
        )

    except QuotaExceeded:

        print(
            "Daily quota enforcement: PASS"
        )

    else:

        raise RuntimeError(
            "Daily quota was not enforced."
        )


def test_partner_isolation():

    limiter = create_limiter()

    alpha = authenticate_partner(
        "ats_alpha_key"
    )

    beta = authenticate_partner(
        "ats_beta_key"
    )

    limiter.record_request(
        alpha
    )

    alpha_usage = limiter.get_usage(
        alpha
    )

    beta_usage = limiter.get_usage(
        beta
    )

    if alpha_usage["requests"] != 1:
        raise RuntimeError(
            "Alpha usage was not recorded."
        )

    if beta_usage["requests"] != 0:
        raise RuntimeError(
            "Alpha usage leaked into Beta."
        )

    print(
        "Per-partner usage isolation: PASS"
    )


def test_rate_window_reset():

    limiter = create_limiter()

    partner_id = authenticate_partner(
        "ats_alpha_key"
    )

    limiter.record_request(
        partner_id
    )

    if limiter.get_usage(
        partner_id
    )["requests"] != 1:

        raise RuntimeError(
            "Request was not recorded."
        )

    limiter.reset_rate_window()

    if limiter.get_usage(
        partner_id
    )["requests"] != 0:

        raise RuntimeError(
            "Rate window did not reset."
        )

    print(
        "Rate-window reset: PASS"
    )


def main():

    print(
        "\n========== TASK 17 RATE LIMITING =========="
    )

    test_rate_limit()

    test_quota_limit()

    test_partner_isolation()

    test_rate_window_reset()

    print(
        "\nRate limiting: PASS"
    )

    print(
        "Daily quota enforcement: PASS"
    )

    print(
        "Partner usage isolation: PASS"
    )

    print(
        "Rate-window reset: PASS"
    )

    print(
        "\nTASK 17 RATE LIMITING: PASS"
    )


if __name__ == "__main__":
    main()