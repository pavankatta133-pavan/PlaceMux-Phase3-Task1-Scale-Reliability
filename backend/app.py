import os
import sys
import time
import uuid

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, request, jsonify

from post_launch_health.logger import log_prediction


app = Flask(__name__)

MODEL_VERSION = "phase3_matching_v1"

# Task 5 controlled failure injection.
# Normal operation = false.
# Reliability testing = set TASK5_FORCE_MODEL_FAILURE=true
FAILURE_INJECTION_ENABLED = (
    os.getenv(
        "TASK5_FORCE_MODEL_FAILURE",
        "false"
    ).lower() == "true"
)


def calculate_match_score(
    student_skills,
    job_skills
):
    """
    Calculate the percentage of required job skills
    that are present in the student's skill profile.
    """

    if not student_skills or not job_skills:
        return 0.0

    student_set = {
        skill.lower().strip()
        for skill in student_skills
    }

    job_set = {
        skill.lower().strip()
        for skill in job_skills
    }

    matched_skills = (
        student_set.intersection(job_set)
    )

    score = (
        len(matched_skills)
        / len(job_set)
    ) * 100

    return round(score, 2)


@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "project":
            "Sprint A - Scale & Reliability",

        "phase":
            "Phase 3",

        "task":
            "Task 5 - Reliability Sign-off & Scale Integration",

        "model_version":
            MODEL_VERSION,

        "status":
            "Live",

        "failure_injection":
            FAILURE_INJECTION_ENABLED
    })


@app.route(
    "/api/post-launch/predict",
    methods=["POST"]
)
def predict():

    start_time = time.perf_counter()

    data = request.get_json(
        silent=True
    )

    # ---------------------------------------------------------
    # Request validation
    # ---------------------------------------------------------

    if not data:

        return jsonify({
            "status":
                "error",

            "message":
                "JSON request body is required",

            "recommendation_available":
                False
        }), 400

    student_id = data.get(
        "student_id"
    )

    job_id = data.get(
        "job_id"
    )

    student_skills = data.get(
        "student_skills",
        []
    )

    job_skills = data.get(
        "job_skills",
        []
    )

    if not student_id or not job_id:

        return jsonify({
            "status":
                "error",

            "message":
                "student_id and job_id are required",

            "recommendation_available":
                False
        }), 400

    # ---------------------------------------------------------
    # Validate skills
    # ---------------------------------------------------------

    if not isinstance(student_skills, list):

        return jsonify({
            "status":
                "error",

            "error_code":
                "INVALID_STUDENT_SKILLS",

            "message":
                "student_skills must be a list.",

            "recommendation_available":
                False
        }), 400

    if not isinstance(job_skills, list):

        return jsonify({
            "status":
                "error",

            "error_code":
                "INVALID_JOB_SKILLS",

            "message":
                "job_skills must be a list.",

            "recommendation_available":
                False
        }), 400

    request_id = str(
        uuid.uuid4()
    )

    # ---------------------------------------------------------
    # TASK 5 - Controlled failure injection
    # ---------------------------------------------------------
    #
    # This is enabled ONLY when:
    #
    # $env:TASK5_FORCE_MODEL_FAILURE="true"
    #
    # Normal production/test operation remains unchanged.
    # ---------------------------------------------------------

    if FAILURE_INJECTION_ENABLED:

        latency = (
            time.perf_counter()
            - start_time
        ) * 1000

        latency = round(
            latency,
            2
        )

        # Log the synthetic failure so that the
        # observability layer records the event.
        try:

            log_prediction(
                request_id=request_id,
                student_id=student_id,
                job_id=job_id,
                predicted_score=0.0,
                rank=0,
                model_version=MODEL_VERSION,
                latency_ms=latency,
                prediction_status="failure"
            )

        except Exception:
            # Logging failure must not hide the
            # intended synthetic failure response.
            pass

        return jsonify({

            "status":
                "fallback",

            "request_id":
                request_id,

            "student_id":
                student_id,

            "job_id":
                job_id,

            "predicted_score":
                None,

            "rank":
                None,

            "model_version":
                MODEL_VERSION,

            "latency_ms":
                latency,

            "error_code":
                "SYNTHETIC_MODEL_FAILURE",

            "message":
                "Synthetic model failure injected "
                "for Task 5 reliability testing.",

            "recommendation_available":
                False,

            "fallback":
                True
        }), 503

    # ---------------------------------------------------------
    # Normal prediction path
    # ---------------------------------------------------------

    score = calculate_match_score(
        student_skills,
        job_skills
    )

    rank = (
        1
        if score >= 70
        else 2
    )

    latency = (
        time.perf_counter()
        - start_time
    ) * 1000

    latency = round(
        latency,
        2
    )

    # ---------------------------------------------------------
    # Prediction logging
    # ---------------------------------------------------------

    log_prediction(
        request_id=request_id,
        student_id=student_id,
        job_id=job_id,
        predicted_score=score,
        rank=rank,
        model_version=MODEL_VERSION,
        latency_ms=latency,
        prediction_status="success"
    )

    # ---------------------------------------------------------
    # Normal successful response
    # ---------------------------------------------------------

    return jsonify({

        "status":
            "success",

        "request_id":
            request_id,

        "student_id":
            student_id,

        "job_id":
            job_id,

        "predicted_score":
            score,

        "rank":
            rank,

        "model_version":
            MODEL_VERSION,

        "latency_ms":
            latency,

        "recommendation_available":
            True,

        "fallback":
            False,

        "explanation":
            "The recommendation score is based "
            "on the percentage of required job "
            "skills present in the student profile."
    })


@app.route(
    "/api/post-launch/explanation",
    methods=["POST"]
)
def recommendation_explanation():

    data = request.get_json(
        silent=True
    )

    # ---------------------------------------------------------
    # Check request body
    # ---------------------------------------------------------

    if not data:

        return jsonify({

            "status":
                "error",

            "error_code":
                "INVALID_REQUEST",

            "message":
                "Request body is required.",

            "recommendation_available":
                False
        }), 400

    # ---------------------------------------------------------
    # Check required fields
    # ---------------------------------------------------------

    required_fields = [
        "student_id",
        "job_id",
        "student_skills",
        "job_skills"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:

        return jsonify({

            "status":
                "error",

            "error_code":
                "MISSING_FIELDS",

            "message":
                "Required fields are missing.",

            "missing_fields":
                missing_fields,

            "recommendation_available":
                False
        }), 400

    # ---------------------------------------------------------
    # Read input values
    # ---------------------------------------------------------

    student_id = data.get(
        "student_id"
    )

    job_id = data.get(
        "job_id"
    )

    student_skills = data.get(
        "student_skills"
    )

    job_skills = data.get(
        "job_skills"
    )

    # ---------------------------------------------------------
    # Validate student skills
    # ---------------------------------------------------------

    if not isinstance(
        student_skills,
        list
    ):

        return jsonify({

            "status":
                "error",

            "error_code":
                "INVALID_STUDENT_SKILLS",

            "message":
                "student_skills must be a list.",

            "recommendation_available":
                False
        }), 400

    # ---------------------------------------------------------
    # Validate job skills
    # ---------------------------------------------------------

    if not isinstance(
        job_skills,
        list
    ):

        return jsonify({

            "status":
                "error",

            "error_code":
                "INVALID_JOB_SKILLS",

            "message":
                "job_skills must be a list.",

            "recommendation_available":
                False
        }), 400

    # ---------------------------------------------------------
    # Convert skills to sets
    # ---------------------------------------------------------

    student_skills = {
        skill.lower().strip()
        for skill in student_skills
    }

    job_skills = {
        skill.lower().strip()
        for skill in job_skills
    }

    # ---------------------------------------------------------
    # Find matching skills
    # ---------------------------------------------------------

    matched_skills = sorted(
        student_skills.intersection(
            job_skills
        )
    )

    # ---------------------------------------------------------
    # Find missing skills
    # ---------------------------------------------------------

    missing_skills = sorted(
        job_skills.difference(
            student_skills
        )
    )

    # ---------------------------------------------------------
    # Calculate recommendation score
    # ---------------------------------------------------------

    if len(job_skills) > 0:

        score = (
            len(matched_skills)
            / len(job_skills)
        ) * 100

    else:

        score = 0

    score = round(
        score,
        2
    )

    # ---------------------------------------------------------
    # Determine recommendation level
    # ---------------------------------------------------------

    if score >= 80:

        recommendation_level = (
            "Highly Recommended"
        )

    elif score >= 50:

        recommendation_level = (
            "Recommended"
        )

    elif score > 0:

        recommendation_level = (
            "Low Match"
        )

    else:

        recommendation_level = (
            "Not Recommended"
        )

    # ---------------------------------------------------------
    # Return explanation
    # ---------------------------------------------------------

    return jsonify({

        "status":
            "success",

        "student_id":
            student_id,

        "job_id":
            job_id,

        "predicted_score":
            score,

        "recommendation":
            recommendation_level,

        "recommendation_available":
            True,

        "explanation": {

            "matched_skills":
                matched_skills,

            "missing_skills":
                missing_skills,

            "matched_skill_count":
                len(matched_skills),

            "required_skill_count":
                len(job_skills),

            "reason":
                (
                    "Recommendation score is based "
                    "on the percentage of required job "
                    "skills matched by the student."
                )
        },

        "model_version":
            MODEL_VERSION
    })


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )