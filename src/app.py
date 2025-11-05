import os
from flask import Flask, render_template, request
from fuzzy_logic import fuzzy_crop_recommendation
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, '..', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, '..', 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/predict', methods=['POST'])
def predict():
    try:
        temperature = float(request.form.get('temperature', 0))
        rainfall = float(request.form.get('rainfall', 0))
        humidity = float(request.form.get('humidity', 0))
        ph = float(request.form.get('ph', 7))
        soil_name = request.form.get('soil_name', 'Unknown Soil') 
        print(f"Received Inputs → Temp: {temperature}, Humidity: {humidity}, Rainfall: {rainfall}, pH: {ph}, Soil: {soil_name}")
        result = fuzzy_crop_recommendation(temperature, humidity, rainfall, ph, soil_name)
        suitability_score = result.get("suitability_score", "N/A")
        predicted_yield = result.get("predicted_yield", "N/A")
        recommended_crops = result.get("recommended_crops", [])
        best_crop = recommended_crops[0] if recommended_crops else "N/A"
        return render_template(
            'result.html',
            soil_name=soil_name,
            suitability_score=suitability_score,
            predicted_yield=predicted_yield,
            recommended_crops=recommended_crops,
            top_crop=best_crop
        )
    except Exception as e:
        return f"❌ Error processing request: {str(e)}"
if __name__ == '__main__':
    app.run(debug=True)
