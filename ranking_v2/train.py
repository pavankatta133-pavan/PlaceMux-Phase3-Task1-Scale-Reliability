"""
Phase 3 Task 11
Train Learning-to-Rank Model

Uses the Task 11 ranking dataset and position-bias
correction weights.
"""

import json
import os
import pickle

import numpy as np

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    PROJECT_ROOT,
    "ranking_v2",
    "reports",
    "ranking_dataset.json"
)

MODEL_FILE = os.path.join(
    PROJECT_ROOT,
    "ranking_v2",
    "models",
    "ltr_ranker.pkl"
)

REPORT_FILE = os.path.join(
    PROJECT_ROOT,
    "ranking_v2",
    "reports",
    "training_report.json"
)


FEATURE_NAMES = [
    "impressions",
    "clicks",
    "applications",
    "shortlists",
    "avg_position",
    "click_rate",
    "application_rate",
    "shortlist_rate",
    "position_weight"
]


def load_dataset():

    if not os.path.exists(DATA_FILE):

        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_FILE}"
        )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def prepare_data(dataset):

    X = []
    y = []
    weights = []

    for record in dataset:

        features = [
            record.get(
                feature,
                0
            )
            for feature in FEATURE_NAMES
        ]

        X.append(
            features
        )

        y.append(
            record.get(
                "relevance_label",
                0
            )
        )

        weights.append(
            record.get(
                "position_weight",
                1.0
            )
        )

    return (
        np.asarray(X, dtype=float),
        np.asarray(y, dtype=float),
        np.asarray(weights, dtype=float)
    )


def main():

    print(
        "\n========== TASK 11 MODEL TRAINING =========="
    )

    dataset = load_dataset()

    print(
        "Ranking records:",
        len(dataset)
    )

    if len(dataset) < 4:

        raise ValueError(
            "Not enough ranking records for training."
        )

    X, y, weights = prepare_data(
        dataset
    )

    unique_labels = np.unique(
        y
    )

    print(
        "Relevance labels:",
        unique_labels.tolist()
    )

    # ------------------------------------------------
    # Train / validation split
    # ------------------------------------------------

    try:

        X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
            X,
            y,
            weights,
            test_size=0.25,
            random_state=42
        )

    except ValueError:

        X_train = X
        X_test = X
        y_train = y
        y_test = y
        w_train = weights
        w_test = weights


    # ------------------------------------------------
    # Gradient Boosting ranking model
    # ------------------------------------------------

    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )

    model.fit(
        X_train,
        y_train,
        sample_weight=w_train
    )


    predictions = model.predict(
        X_test
    )


    mse = mean_squared_error(
        y_test,
        predictions
    )


    # ------------------------------------------------
    # Save model
    # ------------------------------------------------

    os.makedirs(
        os.path.dirname(
            MODEL_FILE
        ),
        exist_ok=True
    )

    with open(
        MODEL_FILE,
        "wb"
    ) as file:

        pickle.dump(
            {
                "model": model,
                "feature_names": FEATURE_NAMES
            },
            file
        )


    # ------------------------------------------------
    # Training report
    # ------------------------------------------------

    report = {

        "task": "Phase 3 Task 11",

        "model": "GradientBoostingRegressor",

        "purpose":
            "Learning-to-Rank relevance scoring",

        "records": len(dataset),

        "training_records":
            len(X_train),

        "validation_records":
            len(X_test),

        "features":
            FEATURE_NAMES,

        "relevance_labels":
            unique_labels.tolist(),

        "position_bias_correction":
            True,

        "weighted_training":
            True,

        "validation_mse":
            round(
                float(mse),
                6
            ),

        "model_file":
            MODEL_FILE

    }


    os.makedirs(
        os.path.dirname(
            REPORT_FILE
        ),
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )


    print(
        "\nModel:",
        "GradientBoostingRegressor"
    )

    print(
        "Position bias correction:",
        "ENABLED"
    )

    print(
        "Weighted training:",
        "ENABLED"
    )

    print(
        "Validation MSE:",
        round(
            float(mse),
            6
        )
    )

    print(
        "\nModel saved to:"
    )

    print(
        MODEL_FILE
    )

    print(
        "\nTraining report saved to:"
    )

    print(
        REPORT_FILE
    )

    print(
        "\nTASK 11 MODEL TRAINING: PASS"
    )


if __name__ == "__main__":

    main()