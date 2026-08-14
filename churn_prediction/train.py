"""
Phase 3 Task 8
Churn Prediction Model Training
"""

import json
import os
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


DATASET_FILE = os.path.join(
    PROJECT_ROOT,
    "churn_prediction",
    "reports",
    "churn_dataset.json"
)


MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "churn_prediction",
    "models"
)


MODEL_FILE = os.path.join(
    MODEL_DIR,
    "churn_model.pkl"
)


REPORT_FILE = os.path.join(
    PROJECT_ROOT,
    "churn_prediction",
    "reports",
    "churn_training_report.json"
)


def load_dataset():

    if not os.path.exists(DATASET_FILE):

        raise FileNotFoundError(
            f"Dataset not found: {DATASET_FILE}"
        )

    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print(
        "\n========== TASK 8 MODEL TRAINING =========="
    )


    # -----------------------------------------
    # Load existing dataset
    # -----------------------------------------

    dataset = load_dataset()


    print(
        "Dataset records:",
        len(dataset)
    )


    # -----------------------------------------
    # Features
    #
    # We intentionally exclude engagement_score
    # because churn_label is derived from it.
    # This avoids direct target leakage.
    # -----------------------------------------

    feature_names = [
        "impressions",
        "clicks",
        "applications",
        "shortlists",
        "ctr",
        "application_rate",
        "shortlist_rate"
    ]


    X = []

    y = []


    for record in dataset:

        X.append([
            record[name]
            for name in feature_names
        ])

        y.append(
            record["churn_label"]
        )


    churn_count = sum(y)

    engaged_count = (
        len(y) - churn_count
    )


    print(
        "At-risk samples:",
        churn_count
    )

    print(
        "Engaged samples:",
        engaged_count
    )


    # -----------------------------------------
    # Validate classes
    # -----------------------------------------

    if len(set(y)) < 2:

        raise ValueError(
            "Training requires both churn and "
            "non-churn classes."
        )


    if churn_count < 2:

        raise ValueError(
            "At least 2 churn/at-risk samples "
            "are required for stratified training."
        )


    # -----------------------------------------
    # Train/test split
    # -----------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.30,
            random_state=42,
            stratify=y
        )
    )


    print(
        "Training records:",
        len(X_train)
    )

    print(
        "Testing records:",
        len(X_test)
    )


    # -----------------------------------------
    # Random Forest model
    # -----------------------------------------

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        class_weight="balanced"
    )


    model.fit(
        X_train,
        y_train
    )


    # -----------------------------------------
    # Predictions
    # -----------------------------------------

    predictions = model.predict(
        X_test
    )


    probabilities = model.predict_proba(
        X_test
    )[:, 1]


    # -----------------------------------------
    # Metrics
    # -----------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )


    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )


    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )


    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )


    # ROC-AUC requires both classes
    # to be present in the test set.

    if len(set(y_test)) == 2:

        roc_auc = roc_auc_score(
            y_test,
            probabilities
        )

    else:

        roc_auc = None


    print(
        "\n========== MODEL METRICS =========="
    )


    print(
        "Accuracy:",
        round(accuracy, 4)
    )

    print(
        "Precision:",
        round(precision, 4)
    )

    print(
        "Recall:",
        round(recall, 4)
    )

    print(
        "F1 Score:",
        round(f1, 4)
    )

    print(
        "ROC-AUC:",
        roc_auc
    )


    # -----------------------------------------
    # Save model
    # -----------------------------------------

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )


    with open(
        MODEL_FILE,
        "wb"
    ) as file:

        pickle.dump(
            model,
            file
        )


    # -----------------------------------------
    # Save training report
    # -----------------------------------------

    report = {

        "task": "Phase 3 Task 8 - Churn Prediction",

        "dataset_records":
            len(dataset),

        "training_records":
            len(X_train),

        "testing_records":
            len(X_test),

        "churn_samples":
            churn_count,

        "engaged_samples":
            engaged_count,

        "features":
            feature_names,

        "model":
            "RandomForestClassifier",

        "metrics": {

            "accuracy":
                round(accuracy, 4),

            "precision":
                round(precision, 4),

            "recall":
                round(recall, 4),

            "f1_score":
                round(f1, 4),

            "roc_auc":
                (
                    round(roc_auc, 4)
                    if roc_auc is not None
                    else None
                )
        },

        "limitation":
            "The dataset contains only 11 users and "
            "2 at-risk samples, so evaluation metrics "
            "are indicative rather than statistically robust."
    }


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
        "\nTASK 8 MODEL TRAINING: PASS"
    )


if __name__ == "__main__":

    main()