from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline


DATA_PATH = Path("data/dataset.csv")
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
CONFUSION_MATRIX_PATH = MODEL_DIR / "confusion_matrix.csv"
RANDOM_STATE = 42


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = {"text", "label"}
    if not required_columns.issubset(df.columns):
        raise ValueError("CSV phải có 2 cột: text, label")

    cleaned_df = df.loc[:, ["text", "label"]].copy()
    cleaned_df["text"] = cleaned_df["text"].astype(str).str.strip()
    cleaned_df["label"] = cleaned_df["label"].astype(str).str.strip()
    cleaned_df = cleaned_df[(cleaned_df["text"] != "") & (cleaned_df["label"] != "")]

    if cleaned_df["label"].nunique() < 2:
        raise ValueError("Cần ít nhất 2 nhãn khác nhau để huấn luyện mô hình.")

    return cleaned_df.reset_index(drop=True)


def build_split_params(y: pd.Series, requested_test_size: float = 0.2) -> tuple[int, pd.Series | None]:
    num_samples = len(y)
    num_classes = y.nunique()
    label_counts = y.value_counts()

    if num_samples < 2:
        raise ValueError("Cần ít nhất 2 mẫu để train/test split.")

    requested_test_samples = max(1, int(round(num_samples * requested_test_size)))
    fallback_test_samples = min(requested_test_samples, num_samples - 1)

    can_stratify = label_counts.min() >= 2 and num_samples >= num_classes * 2
    if not can_stratify:
        print("Không đủ dữ liệu để chia stratify, sẽ split không stratify.")
        return fallback_test_samples, None

    safe_test_samples = max(requested_test_samples, num_classes)
    max_test_samples = num_samples - num_classes
    if safe_test_samples > max_test_samples:
        print("Không thể giữ stratify với kích thước dữ liệu hiện tại, sẽ split không stratify.")
        return fallback_test_samples, None

    return safe_test_samples, y


def build_vectorizer() -> FeatureUnion:
    word_vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 3),
        min_df=2,
        max_features=25000,
        lowercase=True,
        sublinear_tf=True,
    )
    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=30000,
        lowercase=True,
        sublinear_tf=True,
    )

    return FeatureUnion(
        [
            ("word_tfidf", word_vectorizer),
            ("char_tfidf", char_vectorizer),
        ]
    )


def build_classifier() -> LogisticRegression:
    return LogisticRegression(
        max_iter=2000,
        solver="lbfgs",
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )


def sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in report.items():
        if isinstance(value, dict):
            sanitized[key] = {
                metric_name: round(float(metric_value), 4)
                for metric_name, metric_value in value.items()
            }
        else:
            sanitized[key] = round(float(value), 4)
    return sanitized


def run_cross_validation(X: pd.Series, y: pd.Series) -> dict[str, Any]:
    cv_splits = min(5, int(y.value_counts().min()))
    if cv_splits < 2:
        return {}

    cv_pipeline = Pipeline(
        [
            ("vectorizer", build_vectorizer()),
            ("classifier", build_classifier()),
        ]
    )
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_validate(
        cv_pipeline,
        X,
        y,
        cv=cv,
        scoring={"accuracy": "accuracy", "macro_f1": "f1_macro"},
        return_train_score=False,
    )

    return {
        "cv_folds": cv_splits,
        "cv_accuracy_mean": round(float(cv_scores["test_accuracy"].mean()), 4),
        "cv_accuracy_std": round(float(cv_scores["test_accuracy"].std()), 4),
        "cv_macro_f1_mean": round(float(cv_scores["test_macro_f1"].mean()), 4),
        "cv_macro_f1_std": round(float(cv_scores["test_macro_f1"].std()), 4),
    }


def main() -> None:
    configure_stdout()

    df = validate_dataframe(pd.read_csv(DATA_PATH))
    X = df["text"]
    y = df["label"]
    labels = sorted(y.unique())
    label_distribution = y.value_counts().sort_index()

    print(f"Tổng số mẫu: {len(df)}")
    print("Phân bố nhãn:")
    print(label_distribution.to_string())

    test_size, stratify = build_split_params(y)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    vectorizer = build_vectorizer()
    classifier = build_classifier()

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    classifier.fit(X_train_vec, y_train)
    y_pred = classifier.predict(X_test_vec)

    test_accuracy = round(float(accuracy_score(y_test, y_pred)), 4)
    test_macro_f1 = round(float(f1_score(y_test, y_pred, average="macro")), 4)
    report_text = classification_report(y_test, y_pred, zero_division=0)
    report_dict = sanitize_report(
        classification_report(y_test, y_pred, zero_division=0, output_dict=True)
    )

    confusion = confusion_matrix(y_test, y_pred, labels=labels)
    confusion_df = pd.DataFrame(
        confusion,
        index=[f"true_{label}" for label in labels],
        columns=[f"pred_{label}" for label in labels],
    )

    cv_metrics = run_cross_validation(X, y)

    print("\nĐánh giá holdout:")
    print(f"Accuracy: {test_accuracy}")
    print(f"Macro F1: {test_macro_f1}")
    print("\nClassification Report:\n")
    print(report_text)
    print("Confusion Matrix:\n")
    print(confusion_df.to_string())

    if cv_metrics:
        print("\nCross-validation:")
        print(
            f"- {cv_metrics['cv_folds']}-fold accuracy: "
            f"{cv_metrics['cv_accuracy_mean']} ± {cv_metrics['cv_accuracy_std']}"
        )
        print(
            f"- {cv_metrics['cv_folds']}-fold macro F1: "
            f"{cv_metrics['cv_macro_f1_mean']} ± {cv_metrics['cv_macro_f1_std']}"
        )

    final_vectorizer = build_vectorizer()
    final_classifier = build_classifier()
    final_X = final_vectorizer.fit_transform(X)
    final_classifier.fit(final_X, y)

    metrics_payload: dict[str, Any] = {
        "dataset_size": int(len(df)),
        "train_size": int(len(y_train)),
        "test_size": int(len(y_test)),
        "labels": labels,
        "label_distribution": {label: int(count) for label, count in label_distribution.items()},
        "test_accuracy": test_accuracy,
        "test_macro_f1": test_macro_f1,
        "classification_report": report_dict,
    }
    metrics_payload.update(cv_metrics)

    MODEL_DIR.mkdir(exist_ok=True)
    confusion_df.to_csv(CONFUSION_MATRIX_PATH, encoding="utf-8-sig")
    with METRICS_PATH.open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics_payload, metrics_file, ensure_ascii=False, indent=2)

    joblib.dump(
        {
            "model": final_classifier,
            "vectorizer": final_vectorizer,
            "labels": labels,
            "metrics": metrics_payload,
        },
        MODEL_PATH,
    )

    print(f"\nĐã lưu model tại: {MODEL_PATH}")
    print(f"Đã lưu metrics tại: {METRICS_PATH}")
    print(f"Đã lưu confusion matrix tại: {CONFUSION_MATRIX_PATH}")


if __name__ == "__main__":
    main()
