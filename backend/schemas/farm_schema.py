"""Schemas for farm management endpoints."""

from typing import Optional

from pydantic import BaseModel, field_validator

from models import Farm


class FarmCreate(BaseModel):
    """Create farm request schema."""

    name: str
    location: str
    state: str
    district: str
    size_hectares: float
    soil_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v) > 100:
            raise ValueError('Farm name must be 1-100 characters')
        return v

    @field_validator('size_hectares')
    @classmethod
    def validate_size(cls, v):
        if v <= 0 or v > 10000:
            raise ValueError('Farm size must be between 0 and 10000 hectares')
        return v


class FarmUpdate(BaseModel):
    """Update farm request schema."""

    name: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    size_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FarmResponse(BaseModel):
    """Farm response schema."""

    id: int
    name: str
    location: str
    state: str
    district: str
    size_hectares: float
    soil_type: str
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: str

    @classmethod
    def from_farm(cls, farm: Farm):
        return cls(
            id=farm.id,
            name=farm.name,
            location=farm.location,
            state=farm.state,
            district=farm.district,
            size_hectares=farm.size_hectares,
            soil_type=farm.soil_type,
            latitude=farm.latitude,
            longitude=farm.longitude,
            created_at=farm.created_at.isoformat()
        )
