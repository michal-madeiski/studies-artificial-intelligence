import numpy as np
from itertools import product
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
)
from data_prepare import prepare_data
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt


def get_best_params_for_bayes(X_train, X_val, y_train, y_val):
    best_f1 = -1
    best_params = {}
    best_model = None

    nb_smoothing_range = np.logspace(-12, -1, num=12)

    for vs in nb_smoothing_range:
        model = GaussianNB(var_smoothing=vs)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_val)
        f1 = f1_score(y_val, y_pred, average="weighted")

        if f1 > best_f1:
            best_f1 = f1
            best_params = {"var_smoothing": vs}
            best_model = model

    return best_params, best_model


def get_best_params_for_decision_tree(X_train, X_val, y_train, y_val):
    best_f1 = -1
    best_params = {}
    best_model = None

    depths = [None, 3, 5, 10, 15, 20]
    splits = [2, 5, 10, 20]
    criterions = ["gini", "entropy"]

    for depth, split, criterion in product(depths, splits, criterions):
        model = DecisionTreeClassifier(
            max_depth=depth,
            min_samples_split=split,
            criterion=criterion,
            random_state=42,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_val)
        f1 = f1_score(y_val, y_pred, average="weighted")

        if f1 > best_f1:
            best_f1 = f1
            best_params = {
                "max_depth": depth,
                "min_samples_split": split,
                "criterion": criterion,
            }
            best_model = model

    return best_params, best_model


def evaluate_classification(model, X_eval, y_eval, model_name, dataset_name):
    y_pred = model.predict(X_eval)

    acc = accuracy_score(y_eval, y_pred)
    f1 = f1_score(y_eval, y_pred, average="weighted")
    precision = precision_score(y_eval, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_eval, y_pred, average="weighted", zero_division=0)

    print(f"========== {model_name} | {dataset_name} dataset ==========")
    print(f" Accuracy:  {acc:.4f}")
    print(f" F1-Score:  {f1:.4f}")
    print(f" Precision: {precision:.4f}")
    print(f" Recall:    {recall:.4f}")
    disp = ConfusionMatrixDisplay(confusion_matrix(y_eval, y_pred))
    disp.plot(cmap="Blues")
    plt.title(f"Confusion Matrix - {model_name} | {dataset_name} dataset")
    plt.show()


def run_classification_evaluation(X_train, X_val, y_train, y_val, dataset_name=""):
    print("-" * 100)
    nb_params, nb_model = get_best_params_for_bayes(X_train, X_val, y_train, y_val)
    print(f"Best params for Naive Bayes: {nb_params['var_smoothing']:.2e}")
    evaluate_classification(nb_model, X_val, y_val, "Naive Bayes", dataset_name)

    dt_params, dt_model = get_best_params_for_decision_tree(
        X_train, X_val, y_train, y_val
    )
    print(
        f"\nBest params for Decision Tree: depth={dt_params['max_depth']}, "
        f"min_samples_split={dt_params['min_samples_split']}, "
        f"criterion={dt_params['criterion']}"
    )
    evaluate_classification(dt_model, X_val, y_val, "Decision Tree", dataset_name)
    print("-" * 100)


if __name__ == "__main__":
    datasets = prepare_data("data/cirrhosis.csv")

    y_train = datasets["y_train"]
    y_val = datasets["y_val"]

    X_train_base, X_val_base = datasets["base"]
    X_train_standardized, X_val_standardized = datasets["standardized"]
    X_train_pca, X_val_pca = datasets["pca"]

    run_classification_evaluation(X_train_base, X_val_base, y_train, y_val, "Base")
    run_classification_evaluation(
        X_train_standardized, X_val_standardized, y_train, y_val, "Standardized"
    )
    run_classification_evaluation(X_train_pca, X_val_pca, y_train, y_val, "PCA")
