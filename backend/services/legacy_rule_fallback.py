"""Legacy pH/moisture crop fallback.

The production crop recommendation path uses the trained NPK/weather model.
This module only supports older/simple requests that provide pH and moisture
without NPK, temperature, humidity, and rainfall.
"""


def _crop_reasons(crop, soil_ph, moisture):
    """Return short explanations for why a crop matched the simple input."""
    reasons = []

    if crop == "Rice":
        reasons.append("pH is close to the neutral range preferred by rice")
        reasons.append("moisture level supports a high-water crop")
    elif crop == "Wheat":
        reasons.append("pH is suitable for neutral to slightly alkaline soils")
        reasons.append("moisture level fits wheat's lower water requirement")
    elif crop == "Maize":
        reasons.append("pH and moisture are within maize's flexible growing range")
    elif crop == "Sugarcane":
        reasons.append("acidic soil and high moisture favor sugarcane")
    elif crop == "Barley":
        reasons.append("soil and moisture conditions support a drought-tolerant crop")
    elif crop == "Cotton":
        reasons.append("alkaline soil and moderate moisture are suitable for cotton")

    if soil_ph < 5.5:
        reasons.append("soil is acidic; consider lime if growing neutral-soil crops")
    elif soil_ph > 8.0:
        reasons.append("soil is alkaline; monitor micronutrient availability")

    if moisture < 25:
        reasons.append("low moisture increases irrigation planning importance")
    elif moisture > 75:
        reasons.append("high moisture may increase disease risk in sensitive crops")

    return reasons[:3]


def explain_legacy_recommendations(soil_ph, moisture):
    """Return API-ready fallback recommendations for pH/moisture-only input."""
    predictions = predict_legacy_crop(soil_ph, moisture)
    return [
        {
            "rank": index + 1,
            "crop": crop,
            "confidence": score,
            "reasons": _crop_reasons(crop, soil_ph, moisture),
        }
        for index, (crop, score) in enumerate(predictions)
    ]


def predict_legacy_crop(soil_ph, moisture):
    """
    Predict suitable crops from pH and moisture only.

    This is a legacy fallback for incomplete requests. Use the trained crop
    model whenever NPK, temperature, humidity, pH, and rainfall are available.
    """
    if not (3.0 <= soil_ph <= 10.0):
        raise ValueError(f"Soil pH must be between 3.0 and 10.0, got {soil_ph}")
    if not (0 <= moisture <= 100):
        raise ValueError(f"Moisture must be between 0 and 100, got {moisture}")

    recommendations = []

    if 6.0 < soil_ph < 7.5 and moisture > 50:
        recommendations.append(("Rice", 0.95))
    elif 5.5 <= soil_ph <= 7.5 and 40 <= moisture <= 80:
        recommendations.append(("Rice", 0.80))

    if soil_ph >= 7.5 and moisture < 50:
        recommendations.append(("Wheat", 0.95))
    elif 6.5 <= soil_ph <= 8.5 and 20 <= moisture < 60:
        recommendations.append(("Wheat", 0.85))

    if 6.0 <= soil_ph <= 7.5 and 30 <= moisture <= 70:
        recommendations.append(("Maize", 0.90))
    elif 5.5 <= soil_ph <= 8.0 and 25 <= moisture <= 75:
        recommendations.append(("Maize", 0.75))

    if soil_ph < 5.5 and moisture > 60:
        recommendations.append(("Sugarcane", 0.92))
    elif 5.0 <= soil_ph <= 6.0 and moisture > 50:
        recommendations.append(("Sugarcane", 0.80))

    if 5.5 <= soil_ph <= 6.5 and moisture < 40:
        recommendations.append(("Barley", 0.90))
    elif 5.0 <= soil_ph <= 7.5 and moisture < 50:
        recommendations.append(("Barley", 0.70))

    if soil_ph > 8.0 and 30 <= moisture <= 60:
        recommendations.append(("Cotton", 0.92))
    elif soil_ph > 7.5 and 25 <= moisture <= 70:
        recommendations.append(("Cotton", 0.80))

    recommendations.sort(key=lambda item: item[1], reverse=True)

    if not recommendations:
        recommendations = [("Maize", 0.50)]

    return recommendations[:3]
