"""Prediction history routes."""

import logging
import math

from flask import jsonify, request

from database import get_db_context
from models import Farm, Prediction, Season
from routes.auth_routes import token_required
from schemas.prediction_schema import PredictionCreate, PredictionResponse

logger = logging.getLogger(__name__)


def register_prediction_routes(app):
    """Register prediction storage routes with Flask app."""

    @app.route('/api/predictions', methods=['GET', 'POST', 'OPTIONS'])
    @token_required
    def predictions():
        try:
            if request.method == 'GET':
                logger.info(f"Fetching predictions for user: {request.user_id}")

                page = max(request.args.get('page', 1, type=int), 1)
                per_page = min(max(request.args.get('per_page', 10, type=int), 1), 100)

                with get_db_context() as db:
                    base_query = db.query(Prediction).join(
                        Farm, Prediction.farm_id == Farm.id
                    ).filter(
                        Farm.owner_id == request.user_id
                    )
                    total = base_query.count()
                    user_predictions = base_query.order_by(
                        Prediction.created_at.desc()
                    ).offset((page - 1) * per_page).limit(per_page).all()

                    return jsonify({
                        "status": "success",
                        "count": len(user_predictions),
                        "page": page,
                        "total": total,
                        "pages": math.ceil(total / per_page) if total else 0,
                        "data": [PredictionResponse.from_prediction(p).model_dump() for p in user_predictions]
                    }), 200

            elif request.method == 'POST':
                logger.info(f"Storing prediction for user: {request.user_id}")

                try:
                    data = request.get_json()
                    if not data:
                        return jsonify({
                            "status": "error",
                            "message": "Request body is empty"
                        }), 400

                    pred_data = PredictionCreate(**data)
                except ValueError as e:
                    logger.warning(f"Validation error: {e}")
                    return jsonify({
                        "status": "error",
                        "message": f"Validation failed: {str(e)}"
                    }), 400

                with get_db_context() as db:
                    farm = db.query(Farm).filter_by(
                        id=pred_data.farm_id,
                        owner_id=request.user_id
                    ).first()

                    if not farm:
                        logger.warning(f"Farm not found or unauthorized: farm_id={pred_data.farm_id}")
                        return jsonify({
                            "status": "error",
                            "message": "Farm not found"
                        }), 404

                    season_enum = None
                    if pred_data.season:
                        try:
                            season_enum = Season[pred_data.season.upper()]
                        except KeyError:
                            logger.warning(f"Invalid season: {pred_data.season}")

                    new_prediction = Prediction(
                        farm_id=pred_data.farm_id,
                        crop_name=pred_data.crop_name,
                        soil_ph=pred_data.soil_ph,
                        moisture=pred_data.moisture,
                        temperature=pred_data.temperature,
                        rainfall=pred_data.rainfall,
                        confidence_score=pred_data.confidence_score,
                        season=season_enum
                    )

                    db.add(new_prediction)
                    db.commit()
                    db.refresh(new_prediction)

                    logger.info(f"Prediction stored: {new_prediction.id}")

                    return jsonify({
                        "status": "success",
                        "message": "Prediction stored successfully",
                        "data": PredictionResponse.from_prediction(new_prediction).model_dump()
                    }), 201

        except Exception as e:
            logger.error(f"Error in predictions endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500
