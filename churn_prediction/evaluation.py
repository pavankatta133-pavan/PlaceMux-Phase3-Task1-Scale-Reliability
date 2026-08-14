"""
Phase 3 Task 8
Churn Prediction Model Evaluation
"""

import json
import os
import pickle

import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score
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


MODEL_FILE = os.path.join(
    PROJECT_ROOT,
    "churn_prediction",
    "models",
    "churn_model.pkl"
)


REPORT_FILE = os.path.join(
    PROJECT_ROOT,
    "churn_prediction",
    "reports",
    "churn_evaluation.json"
)


PR_CURVE_FILE = os.path.join(
    PROJECT_ROOT,
    "churn_prediction",
    "reports",
    "precision_recall_curve.png"
)


def load_dataset():

    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_model():

    with open(
        MODEL_FILE,
        "rb"
    ) as file:

        return pickle.load(file)


def main():

    print(
        "\n========== TASK 8 MODEL EVALUATION =========="
    )


    # -----------------------------------------
    # Load dataset
    # -----------------------------------------

    dataset = load_dataset()

    model = load_model()


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


    print(
        "Records evaluated:",
        len(dataset)
    )


    # -----------------------------------------
    # Predictions
    # -----------------------------------------

    predictions = model.predict(
        X
    )


    probabilities = model.predict_proba(
        X
    )[:, 1]


    # -----------------------------------------
    # Classification metrics
    # -----------------------------------------

    accuracy = accuracy_score(
        y,
        predictions
    )


    precision = precision_score(
        y,
        predictions,
        zero_division=0
    )


    recall = recall_score(
        y,
        predictions,
        zero_division=0
    )


    f1 = f1_score(
        y,
        predictions,
        zero_division=0
    )


    if len(set(y)) == 2:

        roc_auc = roc_auc_score(
            y,
            probabilities
        )

    else:

        roc_auc = None


    average_precision = (
        average_precision_score(
            y,
            probabilities
        )
    )


    # -----------------------------------------
    # Precision-Recall curve
    # -----------------------------------------

    precision_curve, recall_curve, thresholds = (
        precision_recall_curve(
            y,
            probabilities
        )
    )


    os.makedirs(
        os.path.dirname(
            PR_CURVE_FILE
        ),
        exist_ok=True
    )


    plt.figure(
        figsize=(7, 5)
    )

    plt.plot(
        recall_curve,
        precision_curve
    )

    plt.xlabel(
        "Recall"
    )

    plt.ylabel(
        "Precision"
    )

    plt.title(
        "Churn Prediction Precision-Recall Curve"
    )

    plt.grid(
        True
    )

    plt.tight_layout()

    plt.savefig(
        PR_CURVE_FILE
    )

    plt.close()


    # -----------------------------------------
    # Baseline
    #
    # Predict every user as non-churn.
    # -----------------------------------------

    baseline_predictions = [
        0 for _ in y
    ]


    baseline_accuracy = accuracy_score(
        y,
        baseline_predictions
    )


    baseline_recall = recall_score(
        y,
        baseline_predictions,
        zero_division=0
    )


    # -----------------------------------------
    # Lift
    # -----------------------------------------

    if baseline_accuracy > 0:

        accuracy_lift = (
            (accuracy - baseline_accuracy)
            / baseline_accuracy
        ) * 100

    else:

        accuracy_lift = 0


    # -----------------------------------------
    # Print results
    # -----------------------------------------

    print(
        "\n========== EVALUATION METRICS =========="
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
        (
            round(roc_auc, 4)
            if roc_auc is not None
            else "N/A"
        )
    )


    print(
        "Average Precision:",
        round(
            average_precision,
            4
        )
    )


    print(
        "\n========== BASELINE =========="
    )


    print(
        "Baseline Accuracy:",
        round(
            baseline_accuracy,
            4
        )
    )


    print(
        "Model Accuracy Lift:",
        round(
            accuracy_lift,
            2
        ),
        "%"
    )


    print(
        "Baseline Recall:",
        round(
            baseline_recall,
            4
        )
    )


    # -----------------------------------------
    # Save report
    # -----------------------------------------

    report = {

        "task":
            "Phase 3 Task 8 - Churn Prediction Evaluation",

        "dataset_records":
            len(dataset),

        "at_risk_users":
            sum(y),

        "engaged_users":
            len(y) - sum(y),

        "model":
            "RandomForestClassifier",

        "metrics": {

            "accuracy":
                round(
                    accuracy,
                    4
                ),

            "precision":
                round(
                    precision,
                    4
                ),

            "recall":
                round(
                    recall,
                    4
                ),

            "f1_score":
                round(
                    f1,
                    4
                ),

            "roc_auc":
                (
                    round(
                        roc_auc,
                        4
                    )
                    if roc_auc is not None
                    else None
                ),

            "average_precision":
                round(
                    average_precision,
                    4
                )
        },

        "baseline": {

            "strategy":
                "Predict all users as engaged",

            "accuracy":
                round(
                    baseline_accuracy,
                    4
                ),

            "recall":
                round(
                    baseline_recall,
                    4
                )
        },

        "lift": {

            "accuracy_lift_percent":
                round(
                    accuracy_lift,
                    2
                )
        },

        "artifacts": {

            "model":
                MODEL_FILE,

            "precision_recall_curve":
                PR_CURVE_FILE
        },

        "limitation":
            "The dataset contains only 11 users and 2 at-risk samples. "
            "Therefore, evaluation results are indicative and should "
            "not be considered statistically robust."
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
        "\nPrecision-Recall curve saved to:"
    )

    print(
        PR_CURVE_FILE
    )


    print(
        "\nEvaluation report saved to:"
    )

    print(
        REPORT_FILE
    )


    print(
        "\nTASK 8 MODEL EVALUATION: PASS"
    )


if __name__ == "__main__":

    main()