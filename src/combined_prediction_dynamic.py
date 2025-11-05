import os
import joblib
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.utils import load_img, img_to_array
from fuzzy_logic import fuzzy_crop_recommendation

# ----------------------------
# 1️⃣  FIXED PATHS
# ----------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# ----------------------------
# 2️⃣  LOAD MODELS
# ----------------------------
cnn_model_path = os.path.join(MODEL_DIR, "soil_cnn_model.h5")
crop_model_path = os.path.join(MODEL_DIR, "crop_model.pkl")
scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")

cnn_model = load_model(cnn_model_path)
crop_model = joblib.load(crop_model_path)
scaler = joblib.load(scaler_path)

# ----------------------------
# 3️⃣  HELPER FUNCTIONS
# ----------------------------
SOIL_TYPES = {
    "Class_0": "Sandy",
    "Class_1": "Loamy",
    "Class_2": "Clay",
    "Class_3": "Silty",
    "Class_4": "Clay Loam",
    "Class_5": "Peaty",
    "Class_6": "Saline",
}

def predict_soil_type(image_path):
    """Predict soil class using CNN"""
    try:
        img = load_img(image_path, target_size=(128, 128))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        prediction = cnn_model.predict(img_array)
        class_idx = np.argmax(prediction, axis=1)[0]
        soil_class = f"Class_{class_idx}"
        soil_name = SOIL_TYPES.get(soil_class, "Unknown Soil Type")
        return soil_class, soil_name
    except Exception as e:
        return "Error", str(e)

def predict_yield(features_df):
    """Predict crop yield using trained ML model"""
    try:
        # Match scaler input shape
        required_features = scaler.feature_names_in_
        features_df = features_df[required_features]
        scaled = scaler.transform(features_df)
        pred = crop_model.predict(scaled)
        return round(pred[0], 2)
    except Exception as e:
        return f"Error predicting yield: {e}"

def combined_prediction(image_path, input_features):
    """Combine CNN, ML, and fuzzy logic outputs"""
    soil_class, soil_name = predict_soil_type(image_path)
    predicted_yield = predict_yield(input_features)
    fuzzy_output, fuzzy_score = fuzzy_crop_recommendation(input_features)

    return {
        "soil_class": soil_class,
        "soil_name": soil_name,
        "predicted_yield": predicted_yield,
        "recommended_crops": fuzzy_output,
        "fuzzy_score": fuzzy_score,
    }

# ----------------------------
# 4️⃣  TEST (Run manually)
# ----------------------------
if __name__ == "__main__":
    sample_image = os.path.join(BASE_DIR, "data", "soil_images", "sample.jpg")

    # Example features (replace with real sensor or CSV input)
    sample_features = pd.DataFrame([{
        "rainfall": 0.68,
        "temperature": 0.52,
        "ph": 0.61,
        "nitrogen": 0.45,
        "phosphorus": 0.40,
    }])

    results = combined_prediction(sample_image, sample_features)
    print("\n🌾 SmartCrop Results")
    print("-----------------------------")
    print(f"Soil Type: {results['soil_class']}")
    print(f"Soil Name: {results['soil_name']}")
    print(f"Predicted Yield: {results['predicted_yield']} tons/hectare")
    print(f"Recommended Crops: {results['recommended_crops']}")
    print(f"Suitability Score: {results['fuzzy_score']}")
