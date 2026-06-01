"""Train a MobileNetV2 plant disease classifier.

This script expects a directory layout like:

plant_disease/
  New Plant Diseases Dataset(Augmented)/
    New Plant Diseases Dataset(Augmented)/
      train/<class_name>/*.jpg
      valid/<class_name>/*.jpg
"""

import argparse
import json
import shutil
from pathlib import Path


def create_limited_dataset(source_dir, target_dir, max_images_per_class):
    """Create a small class-balanced subset for quick local training."""
    if not max_images_per_class:
        return source_dir

    source_dir = Path(source_dir)
    target_dir = Path(target_dir)
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for class_dir in sorted(path for path in source_dir.iterdir() if path.is_dir()):
        output_class_dir = target_dir / class_dir.name
        output_class_dir.mkdir(parents=True, exist_ok=True)
        images = [
            path for path in sorted(class_dir.iterdir())
            if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ][:max_images_per_class]
        for image in images:
            shutil.copy2(image, output_class_dir / image.name)

    return target_dir


def train(
    data_dir,
    output_path,
    labels_path,
    image_size=224,
    epochs=5,
    batch_size=32,
    max_images_per_class=None,
    imagenet_weights=True,
):
    import tensorflow as tf

    data_dir = Path(data_dir)
    train_dir = data_dir / "train"
    valid_dir = data_dir / "valid"
    output_path = Path(output_path)
    labels_path = Path(labels_path)

    if not train_dir.exists() or not valid_dir.exists():
        raise ValueError(f"Expected train and valid folders inside {data_dir}")

    if max_images_per_class:
        subset_root = Path("ml_models/disease_training_subset")
        train_dir = create_limited_dataset(train_dir, subset_root / "train", max_images_per_class)
        valid_dir = create_limited_dataset(valid_dir, subset_root / "valid", max(1, max_images_per_class // 4))

    valid_class_count = len([path for path in valid_dir.iterdir() if path.is_dir()]) if valid_dir.exists() else 0
    if valid_class_count >= 2:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            train_dir,
            image_size=(image_size, image_size),
            batch_size=batch_size,
            label_mode="categorical",
        )
        valid_ds = tf.keras.utils.image_dataset_from_directory(
            valid_dir,
            image_size=(image_size, image_size),
            batch_size=batch_size,
            label_mode="categorical",
            shuffle=False,
            class_names=train_ds.class_names,
        )
    else:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            train_dir,
            image_size=(image_size, image_size),
            batch_size=batch_size,
            label_mode="categorical",
            validation_split=0.2,
            subset="training",
            seed=42,
        )
        valid_ds = tf.keras.utils.image_dataset_from_directory(
            train_dir,
            image_size=(image_size, image_size),
            batch_size=batch_size,
            label_mode="categorical",
            validation_split=0.2,
            subset="validation",
            seed=42,
        )

    class_names = train_ds.class_names
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    valid_ds = valid_ds.prefetch(tf.data.AUTOTUNE)

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(image_size, image_size, 3),
        include_top=False,
        weights="imagenet" if imagenet_weights else None,
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(image_size, image_size, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(len(class_names), activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    history = model.fit(train_ds, validation_data=valid_ds, epochs=epochs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(output_path)
    labels_path.write_text(json.dumps({
        "labels": class_names,
        "image_size": image_size,
        "model": "MobileNetV2",
        "epochs": epochs,
        "max_images_per_class": max_images_per_class,
        "imagenet_weights": imagenet_weights,
        "final_accuracy": float(history.history["accuracy"][-1]),
        "final_val_accuracy": float(history.history["val_accuracy"][-1]),
    }, indent=2), encoding="utf-8")

    print(f"Saved disease model: {output_path}")
    print(f"Saved labels/metrics: {labels_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default="data/plant_disease/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)",
    )
    parser.add_argument("--output", default="ml_models/disease_detection_model.keras")
    parser.add_argument("--labels", default="ml_models/disease_labels.json")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--max-images-per-class", type=int, default=None)
    parser.add_argument("--no-imagenet-weights", action="store_true")
    args = parser.parse_args()
    train(
        args.data_dir,
        args.output,
        args.labels,
        args.image_size,
        args.epochs,
        args.batch_size,
        args.max_images_per_class,
        not args.no_imagenet_weights,
    )


if __name__ == "__main__":
    main()
