# combined_prediction_dynamic.py

import os
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.utils import load_img, img_to_array
import joblib
from fuzzy_logic import fuzzy_crop_recommendation

# ----------------------------
# 1. Load Models (Absolute relative to project root)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

soil_model_path = os.path.join(MODEL_DIR, "soil_cnn_model.h5")
yield_model_path = os.path.join(MODEL_DIR, "crop_model.pkl")

soil_model = load_model(soil_model_path)
yield_model = joblib.load(yield_model_path)

# ----------------------------
# Crop Recommendation Map
# ----------------------------
soil_crop_map = {
    "Black Soil": ["Cotton", "Wheat", "Soybean"],
    "Cinder Soil": ["Maize", "Millets", "Sugarcane"],
    "Laterite Soil": ["Tea", "Coffee", "Cashew"],
    "Peat Soil": ["Rice", "Vegetables", "Sugarcane"],
    "Yellow Soil": ["Groundnut", "Wheat", "Barley"]
}

# ----------------------------
# 2. Functions
# ----------------------------
def predict_soil_type(img_path):
    """Predict soil type from image"""
    img = load_img(img_path, target_size=(128, 128))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = soil_model.predict(img_array)
    class_idx = np.argmax(prediction)
    class_label = list(soil_model.class_indices.keys())[class_idx]
    return class_label


def predict_crop_yield(numeric_data):
    """Predict crop yield using trained ML model"""
    df = pd.DataFrame([numeric_data])

    model_features = yield_model.feature_names_in_ if hasattr(yield_model, "feature_names_in_") else df.columns
    for col in model_features:
        if col not in df.columns:
            df[col] = 0  # fill missing

    df = df[model_features]
    yield_pred = yield_model.predict(df)[0]
    return yield_pred


def recommend_crops(soil_type, rainfall, temperature, pesticides):
    """Combine soil-based and fuzzy-based recommendations"""
    base_recommendations = soil_crop_map.get(soil_type, [])
    fuzzy_recommendations = fuzzy_crop_recommendation(rainfall, temperature, pesticides)
    combined = list(set(base_recommendations + fuzzy_recommendations))
    return combined


# ----------------------------
# 3. Main Function
# ----------------------------
def main():
    folder_path = input("Enter folder path containing soil images: ").strip()

    numeric_features = ["rainfall", "temperature", "pesticides"]
    numeric_data = {}

    print("\nEnter numeric values for the following features (press Enter to skip / default=0):")
    for feature in numeric_features:
        val = input(f"{feature}: ").strip()
        if val:
            try:
                numeric_data[feature] = float(val)
            except ValueError:
                print(f"Invalid value for {feature}, using 0.")
                numeric_data[feature] = 0
        else:
            numeric_data[feature] = 0

    print("\n--- Prediction Results ---")
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(folder_path, filename)
            try:
                soil_type = predict_soil_type(img_path)
                crop_yield = predict_crop_yield(numeric_data)
                crop_list = recommend_crops(
                    soil_type,
                    numeric_data["rainfall"],
                    numeric_data["temperature"],
                    numeric_data["pesticides"],
                )

                print(f"\nImage: {filename}")
                print(f"Soil Type: {soil_type}")
                print(f"Predicted Crop Yield: {crop_yield:.2f} hg/ha")
                print(f"Recommended Crops: {', '.join(crop_list)}")
            except Exception as e:
                print(f"\nImage: {filename} --> Prediction failed: {e}")


if __name__ == "__main__":
    main()
