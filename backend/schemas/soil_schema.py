"""Schemas for soil data endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from models import SoilData


class SoilDataCreate(BaseModel):
    """Create soil data request schema."""

    farm_id: int
    ph: Optional[float] = None
    moisture: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    organic_matter: Optional[float] = None
    ec: Optional[float] = None
    measurement_date: Optional[datetime] = None
    source: str = "farmer_input"
    notes: Optional[str] = None

    @field_validator('ph')
    @classmethod
    def validate_ph(cls, v):
        if v is not None and not (3.0 <= v <= 10.0):
            raise ValueError('Soil pH must be between 3.0 and 10.0')
        return round(v, 2) if v is not None else v

    @field_validator('moisture')
    @classmethod
    def validate_moisture(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError('Moisture must be between 0 and 100 (%)')
        return round(v, 2) if v is not None else v

    @field_validator('nitrogen', 'phosphorus', 'potassium', 'organic_matter', 'ec')
    @classmethod
    def validate_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Soil nutrient and chemistry values cannot be negative')
        return v

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        if not v or len(v) > 50:
            raise ValueError('Source must be 1-50 characters')
        return v


class SoilDataUpdate(BaseModel):
    """Update soil data request schema."""

    ph: Optional[float] = None
    moisture: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    organic_matter: Optional[float] = None
    ec: Optional[float] = None
    measurement_date: Optional[datetime] = None
    source: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('ph')
    @classmethod
    def validate_ph(cls, v):
        if v is not None and not (3.0 <= v <= 10.0):
            raise ValueError('Soil pH must be between 3.0 and 10.0')
        return round(v, 2) if v is not None else v

    @field_validator('moisture')
    @classmethod
    def validate_moisture(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError('Moisture must be between 0 and 100 (%)')
        return round(v, 2) if v is not None else v

    @field_validator('nitrogen', 'phosphorus', 'potassium', 'organic_matter', 'ec')
    @classmethod
    def validate_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Soil nutrient and chemistry values cannot be negative')
        return v

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        if v is not None and (not v or len(v) > 50):
            raise ValueError('Source must be 1-50 characters')
        return v


class SoilDataResponse(BaseModel):
    """Soil data response schema."""

    id: int
    farm_id: int
    ph: Optional[float]
    moisture: Optional[float]
    nitrogen: Optional[float]
    phosphorus: Optional[float]
    potassium: Optional[float]
    organic_matter: Optional[float]
    ec: Optional[float]
    measurement_date: Optional[str]
    source: str
    notes: Optional[str]
    created_at: str

    @classmethod
    def from_soil_data(cls, soil_data: SoilData):
        return cls(
            id=soil_data.id,
            farm_id=soil_data.farm_id,
            ph=soil_data.ph,
            moisture=soil_data.moisture,
            nitrogen=soil_data.nitrogen,
            phosphorus=soil_data.phosphorus,
            potassium=soil_data.potassium,
            organic_matter=soil_data.organic_matter,
            ec=soil_data.ec,
            measurement_date=soil_data.measurement_date.isoformat() if soil_data.measurement_date else None,
            source=soil_data.source,
            notes=soil_data.notes,
            created_at=soil_data.created_at.isoformat()
        )
