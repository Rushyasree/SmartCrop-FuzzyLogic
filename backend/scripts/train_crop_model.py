"""Train the Crop Zen crop recommendation model.

Expected CSV columns:
N, P, K, temperature, humidity, ph, rainfall, label
"""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
LABEL = "label"


def train(dataset_path, output_path, metrics_path):
    dataset_path = Path(dataset_path)
    output_path = Path(output_path)
    metrics_path = Path(metrics_path)

    data = pd.read_csv(dataset_path)
    missing_columns = [column for column in [*FEATURES, LABEL] if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing columns: {missing_columns}")

    x = data[FEATURES]
    y = data[LABEL].astype(str)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=250,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        )),
    ])
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    labels = list(pipeline.named_steps["model"].classes_)
    artifact = {
        "model": pipeline,
        "labels": labels,
        "metadata": {
            "name": "random_forest_crop_recommender",
            "version": "1.0.0",
            "features": FEATURES,
            "dataset": str(dataset_path),
            "accuracy": round(float(accuracy), 4),
            "sample_count": int(len(data)),
            "class_count": int(len(labels)),
        },
    }
    joblib.dump(artifact, output_path)

    metrics = {
        "accuracy": round(float(accuracy), 4),
        "sample_count": int(len(data)),
        "class_count": int(len(labels)),
        "labels": labels,
        "classification_report": report,
    }
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Saved model: {output_path}")
    print(f"Saved metrics: {metrics_path}")
    print(f"Accuracy: {accuracy:.4f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default="data/crop_recommendation.csv/Crop_recommendation.csv",
        help="Path to crop recommendation CSV",
    )
    parser.add_argument(
        "--output",
        default="ml_models/crop_recommendation_model.joblib",
        help="Path for trained model artifact",
    )
    parser.add_argument(
        "--metrics",
        default="ml_models/crop_recommendation_metrics.json",
        help="Path for metrics JSON",
    )
    args = parser.parse_args()
    train(args.dataset, args.output, args.metrics)


if __name__ == "__main__":
    main()
