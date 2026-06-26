"""
Week 19 - Thorough model evaluation report.

Trains a classifier and produces a full evaluation:
  * accuracy / precision / recall / F1
  * confusion matrix
  * cross-validation (cross_val_score) on top of a single train/test split
  * an overfitting vs. underfitting demonstration by varying model complexity

Everything prints as a clean text report. Self-contained and runnable.

Run:
    python3 evaluate_model.py
"""

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


def core_metrics(model, X_train, X_test, y_train, y_test):
    """Train on the training set, report metrics on the held-out test set."""
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print("CORE METRICS (held-out test set)")
    print("-" * 55)
    print(f"  Accuracy  : {accuracy_score(y_test, preds):.4f}")
    print(f"  Precision : {precision_score(y_test, preds):.4f}")
    print(f"  Recall    : {recall_score(y_test, preds):.4f}")
    print(f"  F1 score  : {f1_score(y_test, preds):.4f}")
    print()

    cm = confusion_matrix(y_test, preds)
    tn, fp, fn, tp = cm.ravel()
    print("  Confusion matrix:")
    print(f"                 pred 0   pred 1")
    print(f"      actual 0 [ {tn:5d}   {fp:5d} ]   (TN, FP)")
    print(f"      actual 1 [ {fn:5d}   {tp:5d} ]   (FN, TP)")
    print()


def cross_validation_report(model, X, y, folds=5):
    """A single split can be lucky. Cross-validation averages over k folds."""
    scores = cross_val_score(model, X, y, cv=folds, scoring="accuracy")
    print(f"CROSS-VALIDATION ({folds}-fold accuracy)")
    print("-" * 55)
    print(f"  Per-fold : {[round(s, 4) for s in scores]}")
    print(f"  Mean     : {scores.mean():.4f}")
    print(f"  Std dev  : {scores.std():.4f}")
    print()


def complexity_curve(X_train, X_test, y_train, y_test):
    """Show under/overfitting by sweeping decision-tree depth.

    Shallow tree   -> underfits (low train AND test accuracy).
    Very deep tree -> overfits  (high train, lower test; big gap).
    """
    print("OVERFITTING vs. UNDERFITTING (decision tree depth sweep)")
    print("-" * 55)
    print(f"  {'depth':>6} {'train_acc':>11} {'test_acc':>10} {'gap':>8}")
    for depth in [1, 2, 3, 5, 10, None]:
        model = DecisionTreeClassifier(max_depth=depth, random_state=42)
        model.fit(X_train, y_train)
        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))
        gap = train_acc - test_acc
        label = "none" if depth is None else str(depth)
        print(f"  {label:>6} {train_acc:>11.4f} {test_acc:>10.4f} {gap:>8.4f}")
    print()
    print("  Reading it: small depth -> both scores low = UNDERFIT.")
    print("  Large depth -> train ~1.0 but test lags, big gap = OVERFIT.")
    print("  The best depth is where test accuracy peaks before the gap grows.")
    print()


def main():
    data = load_breast_cancer()
    X, y = data.data, data.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print("=" * 55)
    print("Week 19 - Model Evaluation Report")
    print("Dataset: Breast Cancer Wisconsin")
    print(f"Train / Test samples: {len(X_train)} / {len(X_test)}")
    print("=" * 55)
    print()

    # A moderately-sized tree as the main model under evaluation.
    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    core_metrics(model, X_train, X_test, y_train, y_test)

    # Cross-validate a fresh model of the same type on the full dataset.
    cross_validation_report(
        DecisionTreeClassifier(max_depth=4, random_state=42), X, y
    )

    complexity_curve(X_train, X_test, y_train, y_test)

    print("=" * 55)
    print("Summary: accuracy alone hides errors - precision/recall/F1 and the")
    print("confusion matrix show WHICH mistakes happen. Cross-validation checks")
    print("the score is stable, and the depth sweep locates the sweet spot")
    print("between underfitting and overfitting.")
    print("=" * 55)


if __name__ == "__main__":
    main()
