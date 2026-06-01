"""
Crop Zen Database Models
SQLAlchemy ORM models for PostgreSQL
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship, synonym
import enum

Base = declarative_base()


def utc_now():
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(enum.Enum):
    """User role enumeration"""
    FARMER = "farmer"
    ADMIN = "admin"
    RESEARCHER = "researcher"

class Season(enum.Enum):
    """Crop season enumeration"""
    KHARIF = "kharif"      # Monsoon crops (June-October)
    RABI = "rabi"          # Winter crops (October-March)
    SUMMER = "summer"      # Summer crops (March-June)
    YEAR_ROUND = "year_round"

class CropType(enum.Enum):
    """Supported crops"""
    RICE = "Rice"
    WHEAT = "Wheat"
    MAIZE = "Maize"
    SUGARCANE = "Sugarcane"
    BARLEY = "Barley"
    COTTON = "Cotton"

# ============================================================================
# MODELS
# ============================================================================

class User(Base):
    """
    User model for farmer authentication and profile management
    
    Fields:
        id: Primary key
        email: Unique email address (login credential)
        password_hash: Bcrypt hashed password
        first_name: Farmer's first name
        last_name: Farmer's last name
        phone: Contact phone number
        role: User role (farmer, admin, researcher)
        is_active: Account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        
    Relationships:
        farms: One-to-many with Farm model
        predictions: One-to-many with Prediction model
    """
    
    __tablename__ = 'users'
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.FARMER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.first_name} {self.last_name})>"


class Farm(Base):
    """
    Farm model for storing farm details and multiple farms per user
    
    Fields:
        id: Primary key
        user_id: Foreign key to User (owner)
        name: Farm name/identifier
        location: Farm location (village, district, state)
        state: Indian state abbreviation (KA, MH, TN, etc.)
        district: District name
        size_hectares: Farm size in hectares
        soil_type: Primary soil type (red, black, alluvial, etc.)
        latitude: GPS latitude
        longitude: GPS longitude
        is_active: Active farm status
        created_at: Timestamp
        updated_at: Timestamp
        
    Relationships:
        owner: Many-to-one with User
        predictions: One-to-many with Prediction
        soil_data: One-to-many with SoilData
        diseases: One-to-many with DiseaseDetection
    """
    
    __tablename__ = 'farms'
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    owner_id = synonym("user_id")
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    state = Column(String(50), nullable=True)
    district = Column(String(100), nullable=True)
    size_hectares = Column(Float, nullable=True)
    soil_type = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="farms")
    predictions = relationship("Prediction", back_populates="farm", cascade="all, delete-orphan")
    soil_data = relationship("SoilData", back_populates="farm", cascade="all, delete-orphan")
    diseases = relationship("DiseaseDetection", back_populates="farm", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Farm(id={self.id}, name={self.name}, user_id={self.user_id})>"


class SoilData(Base):
    """
    Soil data model for storing soil measurements from sensors/lab tests
    
    Fields:
        id: Primary key
        farm_id: Foreign key to Farm
        ph: Soil pH (3.0-10.0)
        moisture: Soil moisture percentage (0-100%)
        nitrogen: Nitrogen content (mg/kg)
        phosphorus: Phosphorus content (mg/kg)
        potassium: Potassium content (mg/kg)
        organic_matter: Organic matter percentage
        ec: Electrical conductivity (dS/m)
        measurement_date: Date of measurement
        source: Data source (sensor, lab_test, farmer_input)
        notes: Additional notes
        created_at: Timestamp
        
    Relationships:
        farm: Many-to-one with Farm
    """
    
    __tablename__ = 'soil_data'
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False, index=True)
    ph = Column(Float, nullable=True)
    moisture = Column(Float, nullable=True)
    nitrogen = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    organic_matter = Column(Float, nullable=True)
    ec = Column(Float, nullable=True)  # Electrical conductivity
    measurement_date = Column(DateTime, nullable=True)
    source = Column(String(50), default="farmer_input", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    
    # Relationships
    farm = relationship("Farm", back_populates="soil_data")
    
    def __repr__(self):
        return f"<SoilData(id={self.id}, farm_id={self.farm_id}, ph={self.ph}, moisture={self.moisture})>"


class Prediction(Base):
    """
    Prediction model for storing crop recommendation history
    
    Fields:
        id: Primary key
        farm_id: Foreign key to Farm
        input_ph: Input soil pH for prediction
        input_moisture: Input soil moisture for prediction
        recommended_crop: Recommended crop name
        confidence: Model confidence score (0-1)
        rank: Recommendation rank (1st, 2nd, 3rd)
        alternative_crops: JSON string of alternatives
        season: Recommended season
        rainfall_needed: Estimated rainfall (mm)
        fertilizer_recommendation: Fertilizer advice
        irrigation_schedule: Irrigation schedule
        expected_yield: Expected yield (kg/hectare)
        market_price: Current market price (₹/quintal)
        profitability_score: Profitability estimate (0-100)
        created_at: Timestamp
        
    Relationships:
        farm: Many-to-one with Farm
    """
    
    __tablename__ = 'predictions'
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False, index=True)
    input_ph = Column(Float, nullable=False)
    input_moisture = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    recommended_crop = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1 confidence score
    crop_name = synonym("recommended_crop")
    soil_ph = synonym("input_ph")
    moisture = synonym("input_moisture")
    confidence_score = synonym("confidence")
    rank = Column(Integer, default=1, nullable=False)  # 1st, 2nd, 3rd recommendation
    alternative_crops = Column(Text, nullable=True)  # JSON: [{crop, confidence}]
    season = Column(Enum(Season), nullable=True)
    rainfall_needed = Column(Float, nullable=True)
    fertilizer_recommendation = Column(Text, nullable=True)
    irrigation_schedule = Column(Text, nullable=True)
    expected_yield = Column(Float, nullable=True)  # kg/hectare
    market_price = Column(Float, nullable=True)  # ₹ per quintal
    profitability_score = Column(Float, nullable=True)  # 0-100
    model_version = Column(String(50), default="1.0.0", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    
    # Relationships
    farm = relationship("Farm", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, farm_id={self.farm_id}, crop={self.recommended_crop}, confidence={self.confidence})>"


class DiseaseDetection(Base):
    """
    Disease detection model for storing disease detection history
    
    Fields:
        id: Primary key
        farm_id: Foreign key to Farm
        crop: Crop name that was analyzed
        disease_name: Detected disease name
        confidence: Model confidence (0-1)
        severity: Disease severity (mild, moderate, severe)
        affected_area_percent: Percentage of crop affected
        treatment_recommended: Treatment recommendation
        treatment_cost: Estimated treatment cost (₹)
        image_path: Path to uploaded image
        image_url: URL to image (if stored in cloud)
        detected_at: Detection timestamp
        is_confirmed: Whether farmer confirmed diagnosis
        confirmed_by: User ID who confirmed
        notes: Additional notes
        created_at: Timestamp
        
    Relationships:
        farm: Many-to-one with Farm
    """
    
    __tablename__ = 'disease_detections'
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False, index=True)
    crop = Column(String(100), nullable=False)
    disease_name = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1 confidence score
    severity = Column(String(50), nullable=True)  # mild, moderate, severe
    affected_area_percent = Column(Float, nullable=True)  # 0-100
    treatment_recommended = Column(Text, nullable=True)
    treatment_cost = Column(Float, nullable=True)  # ₹
    image_path = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    detected_at = Column(DateTime, default=utc_now, nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    confirmed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    notes = Column(Text, nullable=True)
    model_version = Column(String(50), default="1.0.0", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    
    # Relationships
    farm = relationship("Farm", back_populates="diseases")
    
    def __repr__(self):
        return f"<DiseaseDetection(id={self.id}, farm_id={self.farm_id}, disease={self.disease_name})>"


class Alert(Base):
    """
    Alert model for storing alerts and notifications for farmers
    
    Fields:
        id: Primary key
        farm_id: Foreign key to Farm
        alert_type: Type of alert (disease, weather, pest, market, etc.)
        title: Alert title
        message: Alert message
        severity: Alert severity (info, warning, critical)
        is_read: Whether farmer has read alert
        action_recommended: Recommended action
        created_at: Timestamp
        expires_at: When alert expires
        
    Relationships:
        farm: Many-to-one with Farm
    """
    
    __tablename__ = 'alerts'
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # disease, weather, pest, market
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="info", nullable=False)  # info, warning, critical
    is_read = Column(Boolean, default=False, nullable=False)
    action_recommended = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    farm_id_ref = relationship("Farm")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, farm_id={self.farm_id}, type={self.alert_type})>"


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db(engine):
    """
    Initialize database by creating all tables
    
    Usage:
        from sqlalchemy import create_engine
        from models import init_db
        
        engine = create_engine('postgresql://user:password@localhost/crop_zen')
        init_db(engine)
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def drop_all(engine):
    """
    Drop all tables (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped")
