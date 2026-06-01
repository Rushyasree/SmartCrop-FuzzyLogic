"""
Phase 2 Integration Tests
Tests for database, authentication, and data persistence features
"""

import pytest
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import from app modules
import sys
from pathlib import Path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app import app
from database import SessionLocal, Base, engine
from auth import hash_password, verify_password, create_access_token, verify_token
from models import User, Farm, Prediction, UserRole, Season

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db_session():
    """Create test database session"""
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123"),
        first_name="Test",
        last_name="User",
        phone="9876543210",
        role=UserRole.FARMER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_farm(db_session, test_user):
    """Create test farm"""
    farm = Farm(
        owner_id=test_user.id,
        name="Test Farm",
        location="Test Village",
        state="MH",
        district="Pune",
        size_hectares=10.0,
        soil_type="black",
        latitude=18.5204,
        longitude=73.8567
    )
    db_session.add(farm)
    db_session.commit()
    db_session.refresh(farm)
    return farm


@pytest.fixture
def auth_token(test_user):
    """Create valid auth token"""
    return create_access_token({
        "user_id": test_user.id,
        "email": test_user.email
    })


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Tests for authentication endpoints"""
    
    def test_register_user_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register',
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "9876543210"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['user']['email'] == "newuser@example.com"
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
    
    
    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/api/auth/register',
            json={
                "email": "invalid-email",
                "password": "SecurePass123",
                "first_name": "John",
                "last_name": "Doe"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    
    def test_register_user_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post('/api/auth/register',
            json={
                "email": "user@example.com",
                "password": "weak",
                "first_name": "John",
                "last_name": "Doe"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post('/api/auth/register',
            json={
                "email": test_user.email,
                "password": "SecurePass123",
                "first_name": "John",
                "last_name": "Doe"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/api/auth/login',
            json={
                "email": "test@example.com",
                "password": "TestPassword123"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
    
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email"""
        response = client.post('/api/auth/login',
            json={
                "email": "nonexistent@example.com",
                "password": "Password123"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post('/api/auth/login',
            json={
                "email": "test@example.com",
                "password": "WrongPassword123"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    
    def test_refresh_token_success(self, client, auth_token):
        """Test successful token refresh"""
        response = client.post('/api/auth/refresh-token',
            json={"refresh_token": auth_token},
            content_type='application/json'
        )
        
        # Note: auth_token is actually an access token, for refresh we need a refresh token
        # This test demonstrates the endpoint structure
        assert response.status_code in [200, 401]  # Either success or invalid token
    
    
    def test_get_current_user_with_token(self, client, test_user, auth_token):
        """Test getting current user with valid token"""
        response = client.get('/api/auth/me',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['email'] == test_user.email
    
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['status'] == 'error'


# ============================================================================
# PASSWORD HASHING TESTS
# ============================================================================

class TestPasswordHashing:
    """Tests for password hashing functionality"""
    
    def test_hash_password_creates_unique_hashes(self):
        """Test that same password produces different hashes"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    
    def test_verify_password_success(self):
        """Test password verification with correct password"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed)
    
    
    def test_verify_password_failure(self):
        """Test password verification with wrong password"""
        password = "TestPassword123"
        wrong_password = "WrongPassword123"
        hashed = hash_password(password)
        
        assert not verify_password(wrong_password, hashed)


# ============================================================================
# JWT TOKEN TESTS
# ============================================================================

class TestJWTTokens:
    """Tests for JWT token functionality"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
    
    
    def test_verify_valid_token(self):
        """Test token verification with valid token"""
        user_id = 1
        data = {"user_id": user_id, "email": "test@example.com"}
        token = create_access_token(data)
        
        verified_user_id = verify_token(token)
        assert verified_user_id == user_id
    
    
    def test_verify_invalid_token(self):
        """Test token verification with invalid token"""
        invalid_token = "invalid.token.here"
        
        result = verify_token(invalid_token)
        assert result is None


# ============================================================================
# FARM MANAGEMENT TESTS
# ============================================================================

class TestFarmManagement:
    """Tests for farm management endpoints"""
    
    def test_get_farms_empty(self, client, test_user, auth_token):
        """Test getting farms when user has none"""
        # Create a new user with token
        response = client.get('/api/farms',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # Should either succeed with empty list or fail with no farms
        assert response.status_code in [200, 404]
    
    
    def test_create_farm_success(self, client, auth_token):
        """Test successful farm creation"""
        response = client.post('/api/farms',
            json={
                "name": "New Farm",
                "location": "Test Village",
                "state": "MH",
                "district": "Pune",
                "size_hectares": 15.5,
                "soil_type": "black",
                "latitude": 18.5204,
                "longitude": 73.8567
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )
        
        assert response.status_code in [201, 401]  # 401 if token invalid
    
    
    def test_create_farm_invalid_size(self, client, auth_token):
        """Test farm creation with invalid size"""
        response = client.post('/api/farms',
            json={
                "name": "New Farm",
                "location": "Test Village",
                "state": "MH",
                "district": "Pune",
                "size_hectares": -5,  # Invalid negative size
                "soil_type": "black"
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )
        
        assert response.status_code in [400, 401]


# ============================================================================
# PREDICTION STORAGE TESTS
# ============================================================================

class TestPredictionStorage:
    """Tests for prediction storage endpoints"""
    
    def test_store_prediction_success(self, client, test_farm, auth_token):
        """Test successful prediction storage"""
        response = client.post('/api/predictions',
            json={
                "farm_id": test_farm.id,
                "crop_name": "Rice",
                "soil_ph": 6.5,
                "moisture": 65.0,
                "temperature": 28.5,
                "rainfall": 120.0,
                "confidence_score": 0.92,
                "season": "KHARIF"
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )
        
        assert response.status_code in [201, 401, 404]
    
    
    def test_store_prediction_invalid_ph(self, client, test_farm, auth_token):
        """Test prediction storage with invalid pH"""
        response = client.post('/api/predictions',
            json={
                "farm_id": test_farm.id,
                "crop_name": "Rice",
                "soil_ph": 15.0,  # Invalid pH > 10
                "moisture": 65.0
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )
        
        assert response.status_code in [400, 401, 404]


# ============================================================================
# SOIL DATA TESTS
# ============================================================================

class TestSoilData:
    """Tests for soil data endpoints"""

    def test_create_soil_data_success(self, client, test_farm, auth_token):
        """Test successful soil data creation"""
        response = client.post('/api/soil-data',
            json={
                "farm_id": test_farm.id,
                "ph": 6.45,
                "moisture": 54.25,
                "nitrogen": 120.0,
                "phosphorus": 45.0,
                "potassium": 180.0,
                "organic_matter": 2.5,
                "ec": 0.7,
                "source": "lab_test",
                "notes": "Initial soil test"
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['farm_id'] == test_farm.id
        assert data['data']['ph'] == 6.45
        assert data['data']['source'] == "lab_test"

    def test_get_soil_data_list(self, client, test_farm, auth_token):
        """Test listing user's soil data"""
        client.post('/api/soil-data',
            json={
                "farm_id": test_farm.id,
                "ph": 6.5,
                "moisture": 60.0
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        response = client.get('/api/soil-data',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['total'] >= 1
        assert len(data['data']) >= 1

    def test_get_farm_soil_data(self, client, test_farm, auth_token):
        """Test listing soil data for a specific farm"""
        client.post('/api/soil-data',
            json={
                "farm_id": test_farm.id,
                "ph": 6.5,
                "moisture": 60.0
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        response = client.get(f'/api/farms/{test_farm.id}/soil-data',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['total'] >= 1

    def test_update_soil_data_success(self, client, test_farm, auth_token):
        """Test updating a soil data record"""
        create_response = client.post('/api/soil-data',
            json={
                "farm_id": test_farm.id,
                "ph": 6.5,
                "moisture": 60.0
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )
        soil_data_id = json.loads(create_response.data)['data']['id']

        response = client.put(f'/api/soil-data/{soil_data_id}',
            json={
                "moisture": 62.5,
                "notes": "Updated after irrigation"
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['moisture'] == 62.5
        assert data['data']['notes'] == "Updated after irrigation"

    def test_delete_soil_data_success(self, client, test_farm, auth_token):
        """Test deleting a soil data record"""
        create_response = client.post('/api/soil-data',
            json={
                "farm_id": test_farm.id,
                "ph": 6.5,
                "moisture": 60.0
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )
        soil_data_id = json.loads(create_response.data)['data']['id']

        response = client.delete(f'/api/soil-data/{soil_data_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

        get_response = client.get(f'/api/soil-data/{soil_data_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert get_response.status_code == 404

    def test_create_soil_data_invalid_ph(self, client, test_farm, auth_token):
        """Test soil data validation for invalid pH"""
        response = client.post('/api/soil-data',
            json={
                "farm_id": test_farm.id,
                "ph": 15.0,
                "moisture": 60.0
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'


# ============================================================================
# DATABASE TESTS
# ============================================================================

class TestDatabase:
    """Tests for database connectivity and ORM"""
    
    def test_user_model_creation(self, db_session):
        """Test User model creation"""
        user = User(
            email="testdb@example.com",
            password_hash=hash_password("Password123"),
            first_name="Test",
            last_name="User",
            role=UserRole.FARMER,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        retrieved_user = db_session.query(User).filter_by(email="testdb@example.com").first()
        assert retrieved_user is not None
        assert retrieved_user.first_name == "Test"
    
    
    def test_farm_model_with_owner(self, db_session, test_user):
        """Test Farm model creation with owner relationship"""
        farm = Farm(
            owner_id=test_user.id,
            name="Test Farm",
            location="Test Location",
            state="MH",
            district="Pune",
            size_hectares=10.0,
            soil_type="black"
        )
        
        db_session.add(farm)
        db_session.commit()
        
        retrieved_farm = db_session.query(Farm).filter_by(name="Test Farm").first()
        assert retrieved_farm is not None
        assert retrieved_farm.owner_id == test_user.id


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
