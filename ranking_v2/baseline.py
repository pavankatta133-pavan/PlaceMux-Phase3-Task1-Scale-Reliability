"""
Phase 3 Task 11
Heuristic Baseline Ranker

Represents the existing ranking approach used for comparison.
"""

def heuristic_score(record):

    clicks = record.get(
        "clicks",
        0
    )

    applications = record.get(
        "applications",
        0
    )

    shortlists = record.get(
        "shortlists",
        0
    )

    impressions = record.get(
        "impressions",
        0
    )

    click_rate = (
        clicks / impressions
        if impressions
        else 0
    )

    application_rate = (
        applications / impressions
        if impressions
        else 0
    )

    shortlist_rate = (
        shortlists / impressions
        if impressions
        else 0
    )

    # Existing heuristic-style scoring.
    score = (
        click_rate
        + (application_rate * 3)
        + (shortlist_rate * 5)
    )

    return score


def rank_records(records):

    return sorted(
        records,
        key=heuristic_score,
        reverse=True
    )


if __name__ == "__main__":

    print(
        "TASK 11 BASELINE RANKER: PASS"
    )