"""Schemas for prediction history endpoints."""

from typing import Optional

from pydantic import BaseModel, field_validator

from models import Prediction


class PredictionCreate(BaseModel):
    """Create prediction request schema."""

    farm_id: int
    crop_name: str
    soil_ph: float
    moisture: float
    temperature: Optional[float] = None
    rainfall: Optional[float] = None
    confidence_score: Optional[float] = None
    season: Optional[str] = None

    @field_validator('soil_ph')
    @classmethod
    def validate_ph(cls, v):
        if not (3.0 <= v <= 10.0):
            raise ValueError('Soil pH must be between 3.0 and 10.0')
        return round(v, 2)

    @field_validator('moisture')
    @classmethod
    def validate_moisture(cls, v):
        if not (0 <= v <= 100):
            raise ValueError('Moisture must be between 0 and 100 (%)')
        return round(v, 2)


class PredictionResponse(BaseModel):
    """Prediction response schema."""

    id: int
    farm_id: int
    crop_name: str
    soil_ph: float
    moisture: float
    temperature: Optional[float]
    rainfall: Optional[float]
    confidence_score: Optional[float]
    season: Optional[str]
    created_at: str

    @classmethod
    def from_prediction(cls, prediction: Prediction):
        return cls(
            id=prediction.id,
            farm_id=prediction.farm_id,
            crop_name=prediction.crop_name,
            soil_ph=prediction.soil_ph,
            moisture=prediction.moisture,
            temperature=prediction.temperature,
            rainfall=prediction.rainfall,
            confidence_score=prediction.confidence_score,
            season=prediction.season.value if prediction.season else None,
            created_at=prediction.created_at.isoformat()
        )
