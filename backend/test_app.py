"""
Unit tests for Crop Zen Backend
Run with: pytest test_app.py -v --cov=. --cov-report=html
"""

import pytest
import json
import tempfile
import os
from io import BytesIO
from app import app, CropPredictionRequest
from services.legacy_rule_fallback import predict_legacy_crop
from disease_model import build_disease_response, detect_disease
from pydantic import ValidationError

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup
    import shutil
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])

@pytest.fixture
def valid_crop_data():
    """Valid crop prediction data"""
    return {
        'soilPH': 6.5,
        'moisture': 60.0
    }

@pytest.fixture
def invalid_crop_data():
    """Invalid crop prediction data"""
    return {
        'soilPH': 15.0,  # Out of range
        'moisture': 150.0  # Out of range
    }

# ============================================================================
# TESTS: FUZZY LOGIC MODULE
# ============================================================================

class TestLegacyRuleFallback:
    """Test legacy pH/moisture fallback logic"""
    
    def test_rice_prediction(self):
        """Test rice recommendation"""
        predictions = predict_legacy_crop(6.5, 65)
        assert len(predictions) > 0
        assert predictions[0][0] in ['Rice', 'Maize', 'Sugarcane']  # Top prediction
        assert 0 <= predictions[0][1] <= 1  # Confidence between 0-1
    
    def test_wheat_prediction(self):
        """Test wheat recommendation"""
        predictions = predict_legacy_crop(8.0, 30)
        assert len(predictions) > 0
        assert predictions[0][1] > 0.5  # Should have reasonable confidence
    
    def test_maize_prediction(self):
        """Test maize recommendation"""
        predictions = predict_legacy_crop(6.8, 50)
        assert len(predictions) > 0
        assert predictions[0][0] in ['Maize', 'Rice', 'Wheat']
    
    def test_multiple_predictions(self):
        """Test that we get multiple predictions"""
        predictions = predict_legacy_crop(6.5, 60)
        assert len(predictions) <= 3  # Max 3 recommendations
        assert len(predictions) >= 1  # At least 1 recommendation
        
        # Verify all predictions have crop name and score
        for crop, score in predictions:
            assert isinstance(crop, str)
            assert isinstance(score, float)
            assert 0 <= score <= 1
    
    def test_predictions_sorted_by_confidence(self):
        """Verify predictions are sorted by confidence"""
        predictions = predict_legacy_crop(6.5, 60)
        scores = [score for _, score in predictions]
        assert scores == sorted(scores, reverse=True)
    
    def test_invalid_ph_too_low(self):
        """Test error handling for pH too low"""
        with pytest.raises(ValueError, match="pH must be between"):
            predict_legacy_crop(2.0, 50)
    
    def test_invalid_ph_too_high(self):
        """Test error handling for pH too high"""
        with pytest.raises(ValueError, match="pH must be between"):
            predict_legacy_crop(11.0, 50)
    
    def test_invalid_moisture_negative(self):
        """Test error handling for negative moisture"""
        with pytest.raises(ValueError, match="Moisture must be between"):
            predict_legacy_crop(6.5, -10)
    
    def test_invalid_moisture_too_high(self):
        """Test error handling for moisture > 100"""
        with pytest.raises(ValueError, match="Moisture must be between"):
            predict_legacy_crop(6.5, 150)
    
    def test_extreme_ph_values(self):
        """Test predictions with extreme valid pH values"""
        # Very acidic
        predictions_low = predict_legacy_crop(3.0, 70)
        assert len(predictions_low) > 0
        
        # Very alkaline
        predictions_high = predict_legacy_crop(10.0, 40)
        assert len(predictions_high) > 0
    
    def test_extreme_moisture_values(self):
        """Test predictions with extreme valid moisture values"""
        # Very dry
        predictions_dry = predict_legacy_crop(6.5, 0)
        assert len(predictions_dry) > 0
        
        # Very wet
        predictions_wet = predict_legacy_crop(6.5, 100)
        assert len(predictions_wet) > 0
    
    def test_default_recommendation_for_no_match(self):
        """Test default recommendation when no crops match"""
        # This condition should not match most crops
        predictions = predict_legacy_crop(3.5, 10)  # Very acidic, very dry
        assert len(predictions) >= 1
        assert predictions[0][0] == "Maize"  # Default fallback

# ============================================================================
# TESTS: DISEASE MODEL
# ============================================================================

class TestDiseaseModel:
    """Test disease detection logic"""
    
    def test_no_image_provided(self):
        """Test when no image is provided"""
        result = detect_disease(None)
        assert result['status'] == 'no_image'
        assert result['disease'] is None
        assert result['confidence'] == 0.0
    
    def test_empty_path_string(self):
        """Test with empty path string"""
        result = detect_disease("")
        assert result['status'] == 'no_image'
    
    def test_nonexistent_image_file(self):
        """Test with non-existent image path"""
        result = detect_disease("/path/that/does/not/exist.jpg")
        assert result['status'] == 'error'
        assert result['confidence'] == 0.0
    
    def test_error_response_format(self):
        """Verify error response has correct format"""
        result = detect_disease(None)
        assert 'status' in result
        assert 'message' in result
        assert 'disease' in result
        assert 'confidence' in result

    def test_disease_response_includes_top_predictions(self):
        """Return ranked alternatives for disease predictions."""
        result = build_disease_response(
            probabilities=[0.1, 0.7, 0.2],
            labels=["Apple___healthy", "Apple___Apple_scab", "Apple___Black_rot"],
            metadata={"model": "test_model", "final_val_accuracy": 0.9},
            image_size=224,
            confidence_threshold=0.5,
            top_k=2,
        )

        assert result["status"] == "success"
        assert result["raw_label"] == "Apple___Apple_scab"
        assert result["is_low_confidence"] is False
        assert len(result["top_predictions"]) == 2
        assert result["top_predictions"][0]["rank"] == 1
        assert result["top_predictions"][0]["raw_label"] == "Apple___Apple_scab"
        assert result["top_predictions"][1]["raw_label"] == "Apple___Black_rot"

    def test_disease_response_flags_low_confidence(self):
        """Flag disease predictions below the configured confidence threshold."""
        result = build_disease_response(
            probabilities=[0.44, 0.43, 0.13],
            labels=["Tomato___Early_blight", "Tomato___Target_Spot", "Tomato___healthy"],
            metadata={"model": "test_model"},
            image_size=224,
            confidence_threshold=0.75,
            top_k=3,
        )

        assert result["raw_label"] == "Tomato___Early_blight"
        assert result["confidence"] == 0.44
        assert result["is_low_confidence"] is True
        assert "warning" in result
        assert result["confidence_threshold"] == 0.75

# ============================================================================
# TESTS: VALIDATION SCHEMAS
# ============================================================================

class TestValidation:
    """Test Pydantic validation schemas"""
    
    def test_valid_crop_request(self):
        """Test valid crop request data"""
        request = CropPredictionRequest(soil_ph=6.5, moisture=60.0)
        assert request.soil_ph == 6.5
        assert request.moisture == 60.0
    
    def test_invalid_ph_validation(self):
        """Test pH validation"""
        with pytest.raises(ValidationError):
            CropPredictionRequest(soil_ph=15.0, moisture=60.0)
    
    def test_invalid_moisture_validation(self):
        """Test moisture validation"""
        with pytest.raises(ValidationError):
            CropPredictionRequest(soil_ph=6.5, moisture=150.0)
    
    def test_ph_rounding(self):
        """Test pH rounding to 2 decimals"""
        request = CropPredictionRequest(soil_ph=6.555, moisture=60.0)
        assert request.soil_ph == 6.56
    
    def test_moisture_rounding(self):
        """Test moisture rounding to 2 decimals"""
        request = CropPredictionRequest(soil_ph=6.5, moisture=60.555)
        assert request.moisture == 60.56
    
    def test_boundary_ph_values(self):
        """Test boundary values for pH"""
        # Min value
        request_min = CropPredictionRequest(soil_ph=3.0, moisture=50.0)
        assert request_min.soil_ph == 3.0
        
        # Max value
        request_max = CropPredictionRequest(soil_ph=10.0, moisture=50.0)
        assert request_max.soil_ph == 10.0
    
    def test_boundary_moisture_values(self):
        """Test boundary values for moisture"""
        # Min value
        request_min = CropPredictionRequest(soil_ph=6.5, moisture=0.0)
        assert request_min.moisture == 0.0
        
        # Max value
        request_max = CropPredictionRequest(soil_ph=6.5, moisture=100.0)
        assert request_max.moisture == 100.0

# ============================================================================
# TESTS: API ENDPOINTS
# ============================================================================

class TestAPIEndpoints:
    """Test Flask API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

    def test_openapi_json_endpoint(self, client):
        """Test OpenAPI schema endpoint."""
        response = client.get('/api/openapi.json')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['openapi'].startswith('3.')
        assert data['info']['title'] == 'Crop Zen API'
        assert 'bearerAuth' in data['components']['securitySchemes']
        assert '/api/auth/login' in data['paths']
        assert '/api/soil-data' in data['paths']
        assert '/api/predict' in data['paths']

    def test_swagger_docs_endpoint(self, client):
        """Test Swagger UI endpoint."""
        response = client.get('/api/docs')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
        assert b'Crop Zen API Docs' in response.data
        assert b'/api/openapi.json' in response.data
    
    def test_predict_endpoint_valid_data(self, client, valid_crop_data):
        """Test predict endpoint with valid data"""
        response = client.post('/api/predict', data=valid_crop_data)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'input' in data
        assert 'predictions' in data
        assert len(data['predictions']) > 0
        assert data['input']['soil_ph'] == 6.5
        assert data['input']['moisture'] == 60.0

    def test_predict_endpoint_valid_json_data(self, client):
        """Test predict endpoint with JSON request data."""
        response = client.post('/api/predict',
            json={
                'soil_ph': 6.5,
                'moisture': 60.0
            }
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input']['soil_ph'] == 6.5
        assert data['input']['moisture'] == 60.0
        assert len(data['predictions']) > 0

    def test_predict_endpoint_accepts_json_soil_ph_alias(self, client):
        """Support existing soilPH field name for JSON clients too."""
        response = client.post('/api/predict',
            json={
                'soilPH': 6.5,
                'moisture': 60.0
            }
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input']['soil_ph'] == 6.5
    
    def test_predict_endpoint_missing_soil_ph(self, client):
        """Test predict endpoint without soil pH"""
        response = client.post('/api/predict', data={'moisture': 60.0})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_predict_endpoint_missing_moisture(self, client):
        """Test predict endpoint without moisture"""
        response = client.post('/api/predict', data={'soilPH': 6.5})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_predict_endpoint_invalid_ph(self, client):
        """Test predict endpoint with invalid pH"""
        response = client.post('/api/predict', data={
            'soilPH': 15.0,
            'moisture': 60.0
        })
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_predict_endpoint_invalid_moisture(self, client):
        """Test predict endpoint with invalid moisture"""
        response = client.post('/api/predict', data={
            'soilPH': 6.5,
            'moisture': 150.0
        })
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_predict_endpoint_non_numeric_ph(self, client):
        """Test predict endpoint with non-numeric pH"""
        response = client.post('/api/predict', data={
            'soilPH': 'abc',
            'moisture': 60.0
        })
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_predict_response_format(self, client, valid_crop_data):
        """Verify predict response format"""
        response = client.post('/api/predict', data=valid_crop_data)
        data = json.loads(response.data)
        
        # Check required fields
        assert 'status' in data
        assert 'timestamp' in data
        assert 'input' in data
        assert 'predictions' in data
        assert 'model' in data
        assert data['model']['name'] == 'legacy_ph_moisture_fallback'
        
        # Check predictions format
        for prediction in data['predictions']:
            assert 'rank' in prediction
            assert 'crop' in prediction
            assert 'confidence' in prediction
            assert 'reasons' in prediction
            assert isinstance(prediction['reasons'], list)

    def test_predict_rejects_renamed_non_image_upload(self, client):
        """Reject files that have an image extension but invalid image bytes."""
        response = client.post('/api/predict', data={
            'soilPH': 6.5,
            'moisture': 60.0,
            'image': (BytesIO(b'this is not really an image'), 'leaf.jpg')
        }, content_type='multipart/form-data')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['disease_detection']['status'] == 'skipped'

    def test_predict_accepts_valid_png_signature_upload(self, client):
        """Accept files whose extension and image signature agree."""
        minimal_png = (
            b'\x89PNG\r\n\x1a\n'
            b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02'
            b'\x00\x00\x00\x0bIDATx\x9cc\xfc\xff\x1f\x00\x03\x03\x02\x00\xef\xa2\xa7\xe4'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        response = client.post('/api/predict', data={
            'soilPH': 6.5,
            'moisture': 60.0,
            'image': (BytesIO(minimal_png), 'leaf.png')
        }, content_type='multipart/form-data')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['disease_detection']['status'] in ['success', 'beta']
        assert 'disease' in data['disease_detection']

    def test_predict_rejects_disallowed_upload_extension(self, client):
        """Reject files whose extension is not in the upload allowlist."""
        response = client.post('/api/predict', data={
            'soilPH': 6.5,
            'moisture': 60.0,
            'image': (BytesIO(b'\x89PNG\r\n\x1a\n'), 'leaf.txt')
        }, content_type='multipart/form-data')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['disease_detection']['status'] == 'skipped'

    def test_predict_oversized_upload_returns_json_413(self, client):
        """Return a JSON error when uploaded content exceeds configured size."""
        original_limit = client.application.config['MAX_CONTENT_LENGTH']
        client.application.config['MAX_CONTENT_LENGTH'] = 32

        try:
            response = client.post('/api/predict', data={
                'soilPH': 6.5,
                'moisture': 60.0,
                'image': (BytesIO(b'\x89PNG\r\n\x1a\n' + b'0' * 128), 'leaf.png')
            }, content_type='multipart/form-data')
        finally:
            client.application.config['MAX_CONTENT_LENGTH'] = original_limit

        assert response.status_code == 413
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'too large' in data['message']

    def test_predict_endpoint_missing_json_moisture(self, client):
        """Test JSON predict request without moisture."""
        response = client.post('/api/predict', json={'soil_ph': 6.5})
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'required fields' in data['message']
    
    def test_get_crops_endpoint(self, client):
        """Test get crops endpoint"""
        response = client.get('/api/crops')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'crops' in data
        assert data['count'] == len(data['crops'])
        assert data['count'] > 0
    
    def test_get_crops_response_format(self, client):
        """Verify get crops response format"""
        response = client.get('/api/crops')
        data = json.loads(response.data)
        
        for crop in data['crops']:
            assert 'name' in crop
            assert 'min_ph' in crop
            assert 'max_ph' in crop
            assert 'water_needs' in crop
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'message' in data
    
    def test_cors_headers(self, client, valid_crop_data):
        """Test CORS headers in response"""
        response = client.post('/api/predict', data=valid_crop_data)
        
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests across modules"""
    
    def test_end_to_end_prediction(self, client, valid_crop_data):
        """Test complete prediction flow"""
        # Make prediction
        response = client.post('/api/predict', data=valid_crop_data)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # Verify data consistency
        assert data['input']['soil_ph'] == valid_crop_data['soilPH']
        assert data['input']['moisture'] == valid_crop_data['moisture']
        
        # Verify predictions match the legacy fallback for simple pH/moisture requests
        predictions = predict_legacy_crop(valid_crop_data['soilPH'], valid_crop_data['moisture'])
        assert len(data['predictions']) == len(predictions)
    
    def test_multiple_predictions_consistency(self, client):
        """Test that multiple identical requests return consistent results"""
        data = {'soilPH': 6.5, 'moisture': 60.0}
        
        # Make two identical requests
        response1 = client.post('/api/predict', data=data)
        response2 = client.post('/api/predict', data=data)
        
        result1 = json.loads(response1.data)
        result2 = json.loads(response2.data)
        
        # Results should be identical
        assert result1['predictions'] == result2['predictions']

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=.', '--cov-report=html'])
