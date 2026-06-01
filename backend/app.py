"""
Crop Zen Backend API
AI-Powered Agricultural Advisory Platform
"""

import os
import logging
import uuid
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pydantic import ValidationError

from api_docs import register_api_docs_routes
from disease_model import detect_disease
from database import init_db, get_db_context, print_db_config
from models import User, Farm, Prediction
from routes.auth_routes import register_user_routes, token_required
from routes.farm_routes import register_farm_routes
from routes.prediction_routes import register_prediction_routes
from routes.soil_routes import register_soil_data_routes
from schemas.crop_schema import CropPredictionRequest
from security import rate_limit, validate_production_secret
from services.crop_recommendation_service import get_crop_recommendation

# ============================================================================
# CONFIGURATION
# ============================================================================

LOG_FOLDER = os.getenv('LOG_FOLDER', 'logs')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
FRONTEND_DIST = os.getenv('FRONTEND_DIST', '')
MAX_FILE_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 5 * 1024 * 1024))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_IMAGE_SIGNATURES = {
    'jpg': (b'\xff\xd8\xff',),
    'jpeg': (b'\xff\xd8\xff',),
    'png': (b'\x89PNG\r\n\x1a\n',),
    'gif': (b'GIF87a', b'GIF89a'),
}

os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_FOLDER, 'crop_zen.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
validate_production_secret()


def utc_now():
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@app.before_request
def ensure_test_database():
    """Keep route tests isolated even when fixtures drop all tables."""
    if app.config.get('TESTING'):
        init_db(quiet=True)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

# Initialize database on startup
try:
    print_db_config()
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization warning: {e}")
    logger.info("This is expected if PostgreSQL is not yet running.")
    logger.info("To fix: 1. Install PostgreSQL locally")
    logger.info("        2. Create database: createdb crop_zen")
    logger.info("        3. Run: python setup_alembic.py")

# Register authentication routes
register_user_routes(app)

# Register data persistence routes
register_farm_routes(app)
register_soil_data_routes(app)
register_prediction_routes(app)
register_api_docs_routes(app)

def get_cors_origins():
    """Return allowed frontend origins from FRONTEND_URL or FRONTEND_URLS."""
    configured = os.getenv('FRONTEND_URLS') or os.getenv('FRONTEND_URL', 'http://localhost:3000')
    origins = [origin.strip() for origin in configured.split(',') if origin.strip()]
    origins.append("http://localhost")
    return origins


# ============================================================================
# CORS CONFIGURATION
# ============================================================================
CORS(app, resources={
    r"/api/*": {
        "origins": get_cors_origins(),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# File upload configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if uploaded file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_image_extension(file):
    """Detect allowed image type from file signature, then reset stream position."""
    header = file.stream.read(16)
    file.stream.seek(0)

    for extension, signatures in ALLOWED_IMAGE_SIGNATURES.items():
        if any(header.startswith(signature) for signature in signatures):
            return extension

    return None

def save_uploaded_file(file):
    """
    Safely save uploaded file
    
    Returns:
        str: File path if successful, None otherwise
    """
    try:
        if not file or file.filename == '':
            return None
        
        if not allowed_file(file.filename):
            logger.warning(f"Rejected file with invalid extension: {file.filename}")
            return None

        detected_extension = detect_image_extension(file)
        if detected_extension is None:
            logger.warning(f"Rejected file with invalid image signature: {file.filename}")
            return None
        
        if file.content_length is not None and file.content_length > MAX_FILE_SIZE:
            logger.warning(f"Rejected file exceeding size limit: {file.filename}")
            return None
        
        # Create secure filename with timestamp and random suffix to avoid collisions.
        filename = secure_filename(file.filename)
        name, _ = os.path.splitext(filename)
        timestamp = utc_now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{uuid.uuid4().hex[:12]}_{name}.{detected_extension}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"File uploaded successfully: {filename}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        return None


def extract_prediction_inputs():
    """Extract crop recommendation inputs from JSON or form-data requests."""
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        soil_ph_raw = payload.get('soil_ph', payload.get('soilPH'))
        moisture_raw = payload.get('moisture')
        optional_payload = payload
    else:
        soil_ph_raw = request.form.get('soilPH')
        moisture_raw = request.form.get('moisture')
        optional_payload = request.form

    if soil_ph_raw is None or moisture_raw is None:
        return None, "Missing required fields: soil_ph/soilPH and moisture are required."

    try:
        data = {
            "soil_ph": float(soil_ph_raw),
            "moisture": float(moisture_raw)
        }
        optional_fields = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "rainfall"]
        for field in optional_fields:
            raw_value = optional_payload.get(field)
            if raw_value not in (None, ""):
                data[field] = float(raw_value)
        return data, None
    except (ValueError, TypeError):
        return None, "Invalid input format. Soil and weather values must be numbers."

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": utc_now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
@rate_limit(max_requests=30, window_seconds=60)
def predict():
    """
    Predict recommended crops based on soil conditions
    
    POST Parameters:
        - soil_ph (float): Soil pH (3.0-10.0)
        - moisture (float): Soil moisture (0-100%)
        - image (file, optional): Crop image for disease detection
    
    Returns:
        JSON with recommendations and disease detection
    """
    try:
        logger.info("Received prediction request")
        
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return '', 200
        
        prediction_inputs, input_error = extract_prediction_inputs()
        if input_error:
            logger.warning(input_error)
            return jsonify({
                "status": "error",
                "message": input_error,
                "data": None
            }), 400
        
        # Validate using Pydantic schema
        try:
            crop_request = CropPredictionRequest(**prediction_inputs)
        except ValidationError as e:
            logger.warning(f"Validation error: {e.errors()}")
            return jsonify({
                "status": "error",
                "message": "Validation failed",
                "errors": [{"field": err['loc'][0], "message": err['msg']} for err in e.errors()],
                "data": None
            }), 400
        
        # Process image if uploaded
        image_path = None
        disease_result = None
        
        if 'image' in request.files:
            image_path = save_uploaded_file(request.files['image'])
            if image_path:
                disease_result = detect_disease(image_path)
                logger.info(f"Disease detection result: {disease_result['status']}")
            else:
                logger.warning("Image upload failed or file not allowed")
        
        # Get crop predictions
        try:
            recommendation = get_crop_recommendation(**crop_request.model_dump())
            logger.info(f"Crop prediction successful: {recommendation['raw_predictions']}")
        except ValueError as e:
            logger.error(f"Prediction error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Prediction failed: {str(e)}",
                "data": None
            }), 400
        
        # Format response
        response_data = {
            "status": "success",
            "timestamp": utc_now().isoformat(),
            "input": {
                **crop_request.model_dump(exclude_none=True)
            },
            "predictions": recommendation["predictions"],
            "model": recommendation["model"],
            "disease_detection": disease_result if disease_result else {
                "status": "skipped",
                "message": "No image provided"
            }
        }
        
        logger.info("Prediction request completed successfully")
        return jsonify(response_data), 200
        
    except RequestEntityTooLarge:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in predict endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred",
            "error_id": utc_now().timestamp(),
            "data": None
        }), 500

@app.route('/api/crops', methods=['GET'])
def get_crops():
    """Get list of supported crops"""
    crops = [
        {"name": "Rice", "min_ph": 6.0, "max_ph": 7.5, "water_needs": "High"},
        {"name": "Wheat", "min_ph": 7.5, "max_ph": 8.5, "water_needs": "Low"},
        {"name": "Maize", "min_ph": 6.0, "max_ph": 7.5, "water_needs": "Moderate"},
        {"name": "Sugarcane", "min_ph": 5.0, "max_ph": 6.0, "water_needs": "Very High"},
        {"name": "Barley", "min_ph": 5.5, "max_ph": 6.5, "water_needs": "Low"},
        {"name": "Cotton", "min_ph": 7.5, "max_ph": 8.5, "water_needs": "Moderate"}
    ]
    return jsonify({
        "status": "success",
        "count": len(crops),
        "crops": crops
    }), 200


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the React build when backend and frontend share one deployment."""
    if path.startswith('api/'):
        return not_found(None)

    if not FRONTEND_DIST:
        return jsonify({
            "status": "success",
            "message": "Crop Zen backend is running",
            "docs": "/api/docs"
        }), 200

    requested_path = os.path.join(FRONTEND_DIST, path)
    if path and os.path.isfile(requested_path):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, 'index.html')

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "path": request.path
    }), 404

@app.errorhandler(RequestEntityTooLarge)
def payload_too_large(error):
    """Handle oversized uploads with a JSON API response."""
    return jsonify({
        "status": "error",
        "message": f"Uploaded file is too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB."
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Crop Zen Backend")
    logger.info("=" * 60)
    
    # Use gunicorn in production: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('PORT') or os.getenv('FLASK_PORT', 5000))
    app.run(debug=debug_mode, host=host, port=port)

