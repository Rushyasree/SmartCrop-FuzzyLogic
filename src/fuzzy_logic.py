import random
import numpy as np

# Mapping of soil to possible crops
SOIL_CROP_MAP = {
    "Black Soil": ["Cotton", "Soybean", "Wheat", "Groundnut"],
    "Cinder Soil": ["Millets", "Barley", "Maize"],
    "Laterite Soil": ["Tea", "Coffee", "Cashew", "Rubber"],
    "Peat Soil": ["Rice", "Sugarcane", "Jute"],
    "Yellow Soil": ["Pulses", "Sunflower", "Peas", "Mustard"],
    "Red Soil": ["Groundnut", "Millets", "Castor", "Maize"],
    "Alluvial Soil": ["Rice", "Wheat", "Sugarcane", "Jute"],
    "Unknown Soil": ["Rice", "Wheat", "Maize", "Sugarcane"]
}


# -------------------------------------------------------------
# 1️⃣ Trapezoidal Membership Function
# -------------------------------------------------------------
def trapezoidal_membership(x, a, b, c, d):
    """
    Trapezoidal membership function.
    a, b, c, d define the trapezoid shape.
    Returns membership degree μ(x) between 0 and 1.
    """
    if x <= a or x >= d:
        return 0.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b <= x <= c:
        return 1.0
    elif c < x < d:
        return (d - x) / (d - c)
    else:
        return 0.0


# -------------------------------------------------------------
# 2️⃣ Fuzzify each input parameter using trapezoids
# -------------------------------------------------------------
def fuzzify_inputs(temp, humidity, ph, rainfall):
    fuzzy_sets = {
        "temperature": {
            "Low": (0, 10, 20, 25),
            "Medium": (20, 25, 30, 35),
            "High": (30, 35, 45, 50)
        },
        "humidity": {
            "Low": (0, 20, 30, 40),
            "Medium": (35, 45, 60, 70),
            "High": (65, 75, 90, 100)
        },
        "ph": {
            "Acidic": (0, 4, 5.5, 6),
            "Neutral": (5.5, 6, 7.5, 8),
            "Alkaline": (7.5, 8, 9, 10)
        },
        "rainfall": {
            "Low": (0, 200, 400, 600),
            "Medium": (500, 800, 1200, 1600),
            "High": (1500, 2000, 3000, 3500)
        }
    }

    fuzzy_values = {
        "temperature": {k: trapezoidal_membership(temp, *v) for k, v in fuzzy_sets["temperature"].items()},
        "humidity": {k: trapezoidal_membership(humidity, *v) for k, v in fuzzy_sets["humidity"].items()},
        "ph": {k: trapezoidal_membership(ph, *v) for k, v in fuzzy_sets["ph"].items()},
        "rainfall": {k: trapezoidal_membership(rainfall, *v) for k, v in fuzzy_sets["rainfall"].items()},
    }

    return fuzzy_values


# -------------------------------------------------------------
# 3️⃣ Aggregation + Defuzzification (Centroid Method)
# -------------------------------------------------------------
def centroid_defuzzification(fuzzy_values):
    """
    Aggregate all fuzzy degrees and defuzzify via centroid method.
    """
    # Combine all fuzzy memberships into a weighted score
    aggregated_score = 0
    weight_sum = 0

    for param in fuzzy_values.values():
        for level, membership in param.items():
            if level in ["Medium", "Neutral"]:
                weight = 1.0
            elif level in ["High", "Alkaline"]:
                weight = 0.9
            else:
                weight = 0.7
            aggregated_score += membership * weight
            weight_sum += membership
    if weight_sum == 0:
        return 0
    centroid_score = (aggregated_score / weight_sum) * 100  # Convert to 0–100 scale
    return round(centroid_score, 2)


# -------------------------------------------------------------
# 4️⃣ Main Fuzzy Crop Recommendation Function
# -------------------------------------------------------------
def fuzzy_crop_recommendation(temperature, humidity, rainfall, ph, soil_name):
    try:
        fuzzy_values = fuzzify_inputs(temperature, humidity, ph, rainfall)
        suitability_score = centroid_defuzzification(fuzzy_values)

        crops = SOIL_CROP_MAP.get(soil_name, SOIL_CROP_MAP["Unknown Soil"])
        crop_yields = {}

        for crop in crops:
            variation = random.uniform(-5, 5)
            yield_value = round(max(0, suitability_score + variation), 2)
            crop_yields[crop] = yield_value

        ranked_crops = sorted(crop_yields.items(), key=lambda x: x[1], reverse=True)
        top_crop = ranked_crops[0][0] if ranked_crops else "N/A"
        top_yield = ranked_crops[0][1] if ranked_crops else 0

        return {
            "soil_name": soil_name,
            "suitability_score": suitability_score,
            "top_crop": top_crop,
            "predicted_yield": f"{top_yield} tons/hectare",
            "recommended_crops": [
                {"name": crop, "predicted_yield": f"{yield_val} tons/hectare"}
                for crop, yield_val in ranked_crops
            ]
        }
    except Exception as e:
        return {
            "error": str(e),
            "soil_name": soil_name,
            "suitability_score": "N/A",
            "predicted_yield": "N/A",
            "recommended_crops": []
        }


# -------------------------------------------------------------
# ✅ Example Run
# -------------------------------------------------------------
if __name__ == "__main__":
    result = fuzzy_crop_recommendation(temperature=28, humidity=60, rainfall=1200, ph=6.5, soil_name="Black Soil")
    print(result)
