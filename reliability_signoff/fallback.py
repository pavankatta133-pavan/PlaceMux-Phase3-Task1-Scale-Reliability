from datetime import datetime


def generate_fallback_response(student_id, job_id, reason):
    """
    Return a safe response when the recommendation service
    cannot produce a normal prediction.
    """

    return {
        "status": "fallback",
        "recommendation_available": False,
        "student_id": student_id,
        "job_id": job_id,
        "predicted_score": None,
        "recommendation": None,
        "fallback_reason": reason,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }