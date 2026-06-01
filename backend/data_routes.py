"""Backward-compatible exports for split data route modules."""

from routes.farm_routes import register_farm_routes
from routes.prediction_routes import register_prediction_routes
from routes.soil_routes import register_soil_data_routes

__all__ = [
    "register_farm_routes",
    "register_prediction_routes",
    "register_soil_data_routes",
]
