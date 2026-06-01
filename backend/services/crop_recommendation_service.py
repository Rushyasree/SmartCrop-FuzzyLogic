"""
Crop recommendation service.

This module keeps recommendation business logic out of Flask route handlers.
The trained crop model is preferred; a legacy pH/moisture fallback remains for
older clients that do not send NPK/weather features.
"""

from services.legacy_rule_fallback import (
    explain_legacy_recommendations,
    predict_legacy_crop,
)
from services.ml_crop_model import has_complete_ml_features, predict_with_baseline
from services.trained_crop_model import (
    has_complete_trained_features,
    model_metadata,
    predict_with_trained_model,
)


def get_crop_recommendation(soil_ph, moisture, **optional_features):
    """
    Return raw and API-ready crop recommendations for validated soil inputs.

    Raises:
        ValueError: If the underlying recommendation engine rejects inputs.
    """
    ml_inputs = {
        "soil_ph": soil_ph,
        "ph": soil_ph,
        "moisture": moisture,
        "N": optional_features.get("nitrogen"),
        "P": optional_features.get("phosphorus"),
        "K": optional_features.get("potassium"),
        **optional_features,
    }

    if has_complete_trained_features(ml_inputs):
        trained_predictions = predict_with_trained_model(ml_inputs)
        if trained_predictions:
            metadata = model_metadata() or {}
            return {
                "raw_predictions": [(item["crop"], item["confidence"]) for item in trained_predictions],
                "predictions": trained_predictions,
                "model": {
                    "name": metadata.get("name", "trained_crop_recommender"),
                    "version": metadata.get("version", "1.0.0"),
                    "input_features": metadata.get("features", [
                        "N",
                        "P",
                        "K",
                        "temperature",
                        "humidity",
                        "ph",
                        "rainfall"
                    ]),
                    "accuracy": metadata.get("accuracy"),
                    "sample_count": metadata.get("sample_count"),
                    "class_count": metadata.get("class_count"),
                }
            }

    if has_complete_ml_features(ml_inputs):
        predictions = predict_with_baseline(ml_inputs)
        return {
            "raw_predictions": [(item["crop"], item["confidence"]) for item in predictions],
            "predictions": predictions,
            "model": {
                "name": "npk_weather_baseline",
                "version": "0.1.0",
                "input_features": [
                    "nitrogen",
                    "phosphorus",
                    "potassium",
                    "temperature",
                    "humidity",
                    "soil_ph",
                    "rainfall"
                ],
                "note": "Deterministic ML baseline profile scorer; replace with trained artifact for production."
            }
        }

    raw_predictions = predict_legacy_crop(soil_ph, moisture)
    explained_predictions = explain_legacy_recommendations(soil_ph, moisture)

    return {
        "raw_predictions": raw_predictions,
        "predictions": explained_predictions,
        "model": {
            "name": "legacy_ph_moisture_fallback",
            "version": "1.0.0",
            "input_features": ["soil_ph", "moisture"],
            "note": "Legacy fallback used only when trained model features are incomplete."
        }
    }
