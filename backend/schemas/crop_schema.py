"""Schemas for crop prediction requests."""

from decimal import Decimal, ROUND_HALF_UP

from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


def round_half_up(value, places=2):
    """Round decimal numbers predictably for farmer-entered measurements."""
    quantizer = Decimal("1").scaleb(-places)
    return float(Decimal(str(value)).quantize(quantizer, rounding=ROUND_HALF_UP))


class CropPredictionRequest(BaseModel):
    """Validate crop prediction request data."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "soil_ph": 6.5,
                "moisture": 60.0,
                "nitrogen": 80,
                "phosphorus": 40,
                "potassium": 45,
                "temperature": 28,
                "humidity": 70,
                "rainfall": 120
            }
        }
    )

    soil_ph: float
    moisture: float
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None

    @field_validator('soil_ph')
    @classmethod
    def validate_soil_ph(cls, v):
        if not (3.0 <= v <= 10.0):
            raise ValueError('Soil pH must be between 3.0 and 10.0')
        return round_half_up(v, 2)

    @field_validator('moisture')
    @classmethod
    def validate_moisture(cls, v):
        if not (0 <= v <= 100):
            raise ValueError('Moisture must be between 0 and 100 (%)')
        return round_half_up(v, 2)

    @field_validator('nitrogen', 'phosphorus', 'potassium')
    @classmethod
    def validate_npk(cls, v):
        if v is None:
            return v
        if not (0 <= v <= 300):
            raise ValueError('NPK values must be between 0 and 300')
        return round_half_up(v, 2)

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v is None:
            return v
        if not (-10 <= v <= 60):
            raise ValueError('Temperature must be between -10 and 60 Celsius')
        return round_half_up(v, 2)

    @field_validator('humidity')
    @classmethod
    def validate_humidity(cls, v):
        if v is None:
            return v
        if not (0 <= v <= 100):
            raise ValueError('Humidity must be between 0 and 100 (%)')
        return round_half_up(v, 2)

    @field_validator('rainfall')
    @classmethod
    def validate_rainfall(cls, v):
        if v is None:
            return v
        if not (0 <= v <= 1000):
            raise ValueError('Rainfall must be between 0 and 1000 mm')
        return round_half_up(v, 2)
