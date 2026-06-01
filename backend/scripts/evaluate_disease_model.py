"""Evaluate the trained plant disease classifier.

Creates:
- ml_models/disease_evaluation.json
- ml_models/disease_confusion_matrix.csv
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def collect_images(class_dir):
    return [
        path for path in sorted(class_dir.iterdir())
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def collect_validation_files(data_dir, class_names, validation_split=0.2, seed=42):
    valid_dir = data_dir / "valid"
    train_dir = data_dir / "train"
    valid_class_names = [
        path.name for path in sorted(valid_dir.iterdir())
        if valid_dir.exists() and path.is_dir()
    ]

    image_paths = []
    labels = []

    if valid_class_names == class_names:
        source = str(valid_dir)
        for class_index, class_name in enumerate(class_names):
            for image_path in collect_images(valid_dir / class_name):
                image_paths.append(str(image_path))
                labels.append(class_index)
        return image_paths, np.array(labels), source

    rng = np.random.default_rng(seed)
    source = f"{train_dir} stratified validation_split={validation_split} seed={seed}"
    for class_index, class_name in enumerate(class_names):
        class_images = collect_images(train_dir / class_name)
        if not class_images:
            continue
        validation_count = max(1, int(round(len(class_images) * validation_split)))
        selected_indices = sorted(
            rng.choice(len(class_images), size=validation_count, replace=False).tolist()
        )
        for image_index in selected_indices:
            image_paths.append(str(class_images[image_index]))
            labels.append(class_index)

    return image_paths, np.array(labels), source


def create_image_dataset(tf, image_paths, image_size, batch_size):
    path_ds = tf.data.Dataset.from_tensor_slices(image_paths)

    def load_image(image_path):
        image = tf.io.read_file(image_path)
        image = tf.image.decode_image(image, channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, [image_size, image_size])
        return tf.cast(image, tf.float32)

    return (
        path_ds
        .map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(batch_size)
        .prefetch(tf.data.AUTOTUNE)
    )


def evaluate(
    data_dir,
    model_path,
    labels_path,
    output_path,
    confusion_matrix_path,
    batch_size=32,
):
    import tensorflow as tf

    data_dir = Path(data_dir)
    train_dir = data_dir / "train"
    valid_dir = data_dir / "valid"
    model_path = Path(model_path)
    labels_path = Path(labels_path)
    output_path = Path(output_path)
    confusion_matrix_path = Path(confusion_matrix_path)

    if not train_dir.exists():
        raise ValueError(f"Expected training folder at {train_dir}")
    if not model_path.exists():
        raise ValueError(f"Model artifact not found: {model_path}")
    if not labels_path.exists():
        raise ValueError(f"Labels artifact not found: {labels_path}")

    metadata = json.loads(labels_path.read_text(encoding="utf-8"))
    class_names = metadata["labels"]
    image_size = int(metadata["image_size"])

    image_paths, true_indices, validation_source = collect_validation_files(
        data_dir,
        class_names,
    )
    if len(image_paths) == 0:
        raise ValueError("No validation images found for disease evaluation")

    model = tf.keras.models.load_model(model_path)
    valid_ds = create_image_dataset(tf, image_paths, image_size, batch_size)
    probabilities = model.predict(valid_ds, verbose=1)
    predicted_indices = np.argmax(probabilities, axis=1)

    report = classification_report(
        true_indices,
        predicted_indices,
        labels=list(range(len(class_names))),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(
        true_indices,
        predicted_indices,
        labels=list(range(len(class_names))),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    confusion_matrix_path.parent.mkdir(parents=True, exist_ok=True)

    evaluation = {
        "model": metadata.get("model", "unknown"),
        "image_size": image_size,
        "class_count": len(class_names),
        "sample_count": int(len(true_indices)),
        "validation_source": validation_source,
        "accuracy": float(np.mean(true_indices == predicted_indices)),
        "macro_avg": report["macro avg"],
        "weighted_avg": report["weighted avg"],
        "per_class": {
            class_name: report[class_name]
            for class_name in class_names
        },
    }
    output_path.write_text(json.dumps(evaluation, indent=2), encoding="utf-8")

    with confusion_matrix_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["actual\\predicted", *class_names])
        for class_name, row in zip(class_names, matrix):
            writer.writerow([class_name, *row.tolist()])

    print(f"Saved disease evaluation: {output_path}")
    print(f"Saved confusion matrix: {confusion_matrix_path}")
    print(f"Validation accuracy: {evaluation['accuracy']:.4f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default="data/plant_disease/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)",
    )
    parser.add_argument("--model", default="ml_models/disease_detection_model.keras")
    parser.add_argument("--labels", default="ml_models/disease_labels.json")
    parser.add_argument("--output", default="ml_models/disease_evaluation.json")
    parser.add_argument("--confusion-matrix", default="ml_models/disease_confusion_matrix.csv")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    evaluate(
        args.data_dir,
        args.model,
        args.labels,
        args.output,
        args.confusion_matrix,
        args.batch_size,
    )


if __name__ == "__main__":
    main()
