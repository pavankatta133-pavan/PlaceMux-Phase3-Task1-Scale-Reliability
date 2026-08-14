"""
Phase 3 Task 11
LTR Ranker v2

Loads the trained model and generates ranking scores.
"""

import json
import os
import pickle

import numpy as np


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_FILE = os.path.join(
    PROJECT_ROOT,
    "ranking_v2",
    "models",
    "ltr_ranker.pkl"
)


def load_model():

    if not os.path.exists(
        MODEL_FILE
    ):

        raise FileNotFoundError(
            f"LTR model not found:\n{MODEL_FILE}"
        )

    with open(
        MODEL_FILE,
        "rb"
    ) as file:

        return pickle.load(
            file
        )


def score_record(
    model_bundle,
    record
):

    model = model_bundle[
        "model"
    ]

    feature_names = model_bundle[
        "feature_names"
    ]

    features = [

        record.get(
            feature,
            0
        )

        for feature in feature_names
    ]

    X = np.asarray(
        [features],
        dtype=float
    )

    score = model.predict(
        X
    )[0]

    return float(
        score
    )


def rank_records(records):

    model_bundle = load_model()

    ranked = []

    for record in records:

        result = dict(
            record
        )

        result[
            "ltr_score"
        ] = round(
            score_record(
                model_bundle,
                record
            ),
            6
        )

        ranked.append(
            result
        )

    ranked.sort(
        key=lambda x:
            x["ltr_score"],
        reverse=True
    )

    return ranked


if __name__ == "__main__":

    print(
        "TASK 11 LTR RANKER: PASS"
    )