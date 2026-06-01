"""Validate disease inference against loose demo/test images.

This script is intended for images outside the class-folder training layout,
such as data/plant_disease/test/test/*.JPG.

Creates:
- ml_models/disease_field_validation.json
- ml_models/disease_field_validation.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from disease_model import detect_disease


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
EXPECTED_LABEL_HINTS = {
    "AppleCedarRust": "Apple___Cedar_apple_rust",
    "AppleScab": "Apple___Apple_scab",
    "CornCommonRust": "Corn_(maize)___Common_rust_",
    "PotatoEarlyBlight": "Potato___Early_blight",
    "PotatoHealthy": "Potato___healthy",
    "TomatoEarlyBlight": "Tomato___Early_blight",
    "TomatoHealthy": "Tomato___healthy",
    "TomatoYellowCurlVirus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
}


def expected_label_from_filename(filename):
    stem = Path(filename).stem
    for prefix, label in EXPECTED_LABEL_HINTS.items():
        if stem.startswith(prefix):
            return label
    return None


def validate_images(input_dir, output_path, csv_path):
    input_dir = Path(input_dir)
    output_path = Path(output_path)
    csv_path = Path(csv_path)

    if not input_dir.exists():
        raise ValueError(f"Input image directory not found: {input_dir}")

    image_paths = [
        path for path in sorted(input_dir.iterdir())
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    if not image_paths:
        raise ValueError(f"No supported image files found in {input_dir}")

    rows = []
    correct = 0
    labeled_count = 0

    for image_path in image_paths:
        expected_label = expected_label_from_filename(image_path.name)
        result = detect_disease(str(image_path))
        predicted_label = result.get("raw_label")
        is_correct = expected_label is not None and predicted_label == expected_label

        if expected_label is not None:
            labeled_count += 1
            if is_correct:
                correct += 1

        rows.append({
            "file": image_path.name,
            "expected_label": expected_label,
            "predicted_label": predicted_label,
            "disease": result.get("disease"),
            "confidence": result.get("confidence", 0.0),
            "is_low_confidence": result.get("is_low_confidence"),
            "warning": result.get("warning"),
            "top_predictions": result.get("top_predictions", []),
            "status": result.get("status"),
            "correct": is_correct if expected_label is not None else None,
            "message": result.get("message"),
        })

    accuracy = (correct / labeled_count) if labeled_count else None
    failures = [row for row in rows if row["correct"] is False]
    summary = {
        "input_dir": str(input_dir),
        "image_count": len(image_paths),
        "labeled_count": labeled_count,
        "correct_count": correct,
        "accuracy": accuracy,
        "failure_count": len(failures),
        "failures": failures,
        "results": rows,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "file",
            "expected_label",
            "predicted_label",
            "disease",
            "confidence",
            "is_low_confidence",
            "warning",
            "status",
            "correct",
            "message",
        ])
        writer.writeheader()
        writer.writerows([
            {key: value for key, value in row.items() if key != "top_predictions"}
            for row in rows
        ])

    print(f"Saved field validation JSON: {output_path}")
    print(f"Saved field validation CSV: {csv_path}")
    if accuracy is None:
        print("Accuracy: not available because no expected labels were inferred")
    else:
        print(f"Accuracy: {accuracy:.4f} ({correct}/{labeled_count})")
    if failures:
        print("Failures:")
        for row in failures:
            print(f"- {row['file']}: expected {row['expected_label']}, got {row['predicted_label']} ({row['confidence']})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data/plant_disease/test/test")
    parser.add_argument("--output", default="ml_models/disease_field_validation.json")
    parser.add_argument("--csv", default="ml_models/disease_field_validation.csv")
    args = parser.parse_args()

    validate_images(args.input_dir, args.output, args.csv)


if __name__ == "__main__":
    main()
