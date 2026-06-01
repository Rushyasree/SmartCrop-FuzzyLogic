import logging
import os
import json
from functools import lru_cache

logger = logging.getLogger(__name__)

DISEASE_MODEL_PATH = os.getenv("DISEASE_MODEL_PATH", "ml_models/disease_detection_model.keras")
DISEASE_LABELS_PATH = os.getenv("DISEASE_LABELS_PATH", "ml_models/disease_labels.json")
DISEASE_CONFIDENCE_THRESHOLD = float(os.getenv("DISEASE_CONFIDENCE_THRESHOLD", "0.75"))
DISEASE_TOP_K = int(os.getenv("DISEASE_TOP_K", "3"))


@lru_cache(maxsize=1)
def load_disease_artifacts():
    """Load TensorFlow disease model and labels if available."""
    if not os.path.exists(DISEASE_MODEL_PATH) or not os.path.exists(DISEASE_LABELS_PATH):
        return None

    try:
        import tensorflow as tf
    except ImportError:
        logger.warning("TensorFlow is not installed; disease inference unavailable")
        return None

    with open(DISEASE_LABELS_PATH, "r", encoding="utf-8") as labels_file:
        metadata = json.load(labels_file)

    model = tf.keras.models.load_model(DISEASE_MODEL_PATH)
    return {
        "tf": tf,
        "model": model,
        "labels": metadata["labels"],
        "image_size": int(metadata.get("image_size", 224)),
        "metadata": metadata,
    }


def format_disease_label(label):
    """Convert dataset class names into readable disease labels."""
    return label.replace("___", " - ").replace("_", " ")


def treatment_hint(label):
    """Return a lightweight treatment hint for common disease groups."""
    normalized = label.lower()
    if "healthy" in normalized:
        return "No disease treatment needed. Continue monitoring leaf health."
    if "blight" in normalized:
        return "Remove affected leaves, improve airflow, and consult an agronomist about copper-based fungicide."
    if "rust" in normalized:
        return "Avoid overhead irrigation and consult local guidance for rust-control fungicide."
    if "scab" in normalized:
        return "Improve sanitation, remove infected debris, and use resistant varieties when possible."
    if "mildew" in normalized:
        return "Improve spacing and airflow; consider sulfur or approved fungicide guidance."
    return "Confirm with a local agricultural expert before treatment."


def build_disease_response(probabilities, labels, metadata, image_size, confidence_threshold=None, top_k=None):
    """Build a stable disease inference response from model probabilities."""
    confidence_threshold = (
        DISEASE_CONFIDENCE_THRESHOLD
        if confidence_threshold is None
        else confidence_threshold
    )
    top_k = DISEASE_TOP_K if top_k is None else top_k
    ranked = sorted(
        enumerate(probabilities),
        key=lambda item: float(item[1]),
        reverse=True,
    )[:max(1, min(top_k, len(labels)))]

    top_index = int(ranked[0][0])
    confidence = float(ranked[0][1])
    raw_label = labels[top_index]
    is_low_confidence = confidence < confidence_threshold
    top_predictions = [
        {
            "rank": rank,
            "raw_label": labels[int(index)],
            "disease": format_disease_label(labels[int(index)]),
            "confidence": round(float(score), 4),
        }
        for rank, (index, score) in enumerate(ranked, start=1)
    ]

    response = {
        "status": "success",
        "message": "Disease inference completed",
        "disease": format_disease_label(raw_label),
        "confidence": round(confidence, 4),
        "raw_label": raw_label,
        "confidence_threshold": confidence_threshold,
        "is_low_confidence": is_low_confidence,
        "top_predictions": top_predictions,
        "treatment_recommended": treatment_hint(raw_label),
        "model": {
            "name": metadata.get("model", "plant_disease_classifier"),
            "image_size": image_size,
            "class_count": len(labels),
            "final_val_accuracy": metadata.get("final_val_accuracy"),
        }
    }

    if is_low_confidence:
        response["warning"] = (
            "Low confidence prediction. Capture a clearer leaf image and confirm with an agricultural expert."
        )

    return response


def detect_disease(image_path):
    """
    Detect plant diseases from uploaded images.

    Args:
        image_path (str): Path to the uploaded image

    Returns:
        dict: Disease detection results with confidence scores
    """
    try:
        if not image_path:
            return {
                "status": "no_image",
                "message": "No image provided",
                "disease": None,
                "confidence": 0.0
            }
        
        # Verify file exists
        if not os.path.exists(image_path):
            logger.warning(f"Image file not found: {image_path}")
            return {
                "status": "error",
                "message": "Image file not found",
                "disease": None,
                "confidence": 0.0
            }
        
        logger.info(f"Processing image for disease detection: {image_path}")

        artifacts = load_disease_artifacts()
        if artifacts:
            tf = artifacts["tf"]
            image_size = artifacts["image_size"]
            image = tf.keras.utils.load_img(image_path, target_size=(image_size, image_size))
            image_array = tf.keras.utils.img_to_array(image)
            image_array = tf.expand_dims(image_array, axis=0)
            probabilities = artifacts["model"].predict(image_array, verbose=0)[0]
            return build_disease_response(
                probabilities,
                artifacts["labels"],
                artifacts["metadata"],
                image_size,
            )

        return {
            "status": "beta",
            "message": "Disease detection is currently a beta placeholder.",
            "disease": "No disease detected (Model in development)",
            "confidence": 0.0,
            "note": "Do not use this result for farm treatment decisions until a real image model is integrated."
        }
        
    except Exception as e:
        logger.error(f"Error in disease detection: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Disease detection failed: {str(e)}",
            "disease": None,
            "confidence": 0.0
        }

