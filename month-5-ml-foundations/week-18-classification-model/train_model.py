"""
Week 18 - Train a simple classifier with scikit-learn.

Loads the built-in Breast Cancer Wisconsin dataset, splits it into train and
test sets, trains two classifiers (Logistic Regression and a Decision Tree),
and compares their accuracy. Self-contained and runnable with no external data.

Run:
    python3 train_model.py
"""

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


def load_data():
    """Load the dataset and return features, labels, and label names."""
    data = load_breast_cancer()
    return data.data, data.target, data.target_names


def split_data(X, y):
    """Hold out 25% of the data for testing.

    stratify=y keeps the class balance the same in train and test, and a fixed
    random_state makes the split reproducible.
    """
    return train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )


def train_logistic_regression(X_train, y_train):
    """Logistic Regression benefits from scaled features, so we pipeline it.

    We scale here manually (fit on train only) to avoid leaking test info.
    """
    scaler = StandardScaler().fit(X_train)
    model = LogisticRegression(max_iter=10000)
    model.fit(scaler.transform(X_train), y_train)
    return model, scaler


def train_decision_tree(X_train, y_train):
    """Decision trees don't need scaling. We cap depth to avoid overfitting."""
    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(X_train, y_train)
    return model


def main():
    X, y, target_names = load_data()
    X_train, X_test, y_train, y_test = split_data(X, y)

    print("=" * 55)
    print("Week 18 - Classification: Breast Cancer Wisconsin")
    print("=" * 55)
    print(f"Total samples : {len(X)}")
    print(f"Features      : {X.shape[1]}")
    print(f"Classes       : {list(target_names)}")
    print(f"Train / Test  : {len(X_train)} / {len(X_test)}")
    print("-" * 55)

    # Model 1: Logistic Regression (a linear model)
    logreg, scaler = train_logistic_regression(X_train, y_train)
    logreg_preds = logreg.predict(scaler.transform(X_test))
    logreg_acc = accuracy_score(y_test, logreg_preds)

    # Model 2: Decision Tree (a non-linear, rule-splitting model)
    tree = train_decision_tree(X_train, y_train)
    tree_preds = tree.predict(X_test)
    tree_acc = accuracy_score(y_test, tree_preds)

    print("Test accuracy:")
    print(f"  Logistic Regression : {logreg_acc:.4f}")
    print(f"  Decision Tree       : {tree_acc:.4f}")
    print("-" * 55)

    winner = "Logistic Regression" if logreg_acc >= tree_acc else "Decision Tree"
    print(f"Better on this split: {winner}")
    print("=" * 55)


if __name__ == "__main__":
    main()
