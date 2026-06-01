"""Lightweight crop recommendation baseline using NPK and weather features."""

from math import exp


FEATURES = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "soil_ph", "rainfall"]

CROP_PROFILES = {
    "Rice": {
        "nitrogen": 90, "phosphorus": 42, "potassium": 43,
        "temperature": 24, "humidity": 82, "soil_ph": 6.4, "rainfall": 220,
    },
    "Wheat": {
        "nitrogen": 78, "phosphorus": 48, "potassium": 40,
        "temperature": 20, "humidity": 55, "soil_ph": 7.2, "rainfall": 75,
    },
    "Maize": {
        "nitrogen": 82, "phosphorus": 45, "potassium": 42,
        "temperature": 26, "humidity": 65, "soil_ph": 6.7, "rainfall": 95,
    },
    "Cotton": {
        "nitrogen": 62, "phosphorus": 38, "potassium": 62,
        "temperature": 30, "humidity": 55, "soil_ph": 7.6, "rainfall": 70,
    },
    "Sugarcane": {
        "nitrogen": 110, "phosphorus": 55, "potassium": 95,
        "temperature": 28, "humidity": 75, "soil_ph": 6.0, "rainfall": 180,
    },
    "Barley": {
        "nitrogen": 58, "phosphorus": 34, "potassium": 35,
        "temperature": 18, "humidity": 48, "soil_ph": 6.2, "rainfall": 55,
    },
}

FEATURE_SCALE = {
    "nitrogen": 120,
    "phosphorus": 80,
    "potassium": 120,
    "temperature": 18,
    "humidity": 60,
    "soil_ph": 4,
    "rainfall": 250,
}


def has_complete_ml_features(inputs):
    """Return whether all baseline ML features are present."""
    return all(inputs.get(feature) is not None for feature in FEATURES)


def _similarity_score(inputs, profile):
    distance = 0
    for feature in FEATURES:
        scale = FEATURE_SCALE[feature]
        distance += ((inputs[feature] - profile[feature]) / scale) ** 2
    return exp(-distance)


def predict_with_baseline(inputs):
    """
    Score crops against agronomic profiles.

    This is intentionally lightweight and deterministic, so it works in local
    demos even before a trained scikit-learn artifact is available.
    """
    scores = [
        (crop, _similarity_score(inputs, profile))
        for crop, profile in CROP_PROFILES.items()
    ]
    scores.sort(key=lambda item: item[1], reverse=True)

    top_score = scores[0][1] or 1
    predictions = []
    for rank, (crop, score) in enumerate(scores[:3], start=1):
        confidence = min(round(score / top_score * 0.96, 2), 0.96)
        profile = CROP_PROFILES[crop]
        reasons = [
            f"NPK/weather profile is close to {crop.lower()} requirements.",
            f"pH target around {profile['soil_ph']} and rainfall target around {profile['rainfall']} mm.",
        ]
        predictions.append({
            "rank": rank,
            "crop": crop,
            "confidence": confidence,
            "reasons": reasons,
        })

    return predictions
