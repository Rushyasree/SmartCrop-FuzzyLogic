"""Farm management routes."""

import logging

from flask import jsonify, request

from database import get_db_context
from models import Farm
from routes.auth_routes import token_required
from schemas.farm_schema import FarmCreate, FarmResponse, FarmUpdate

logger = logging.getLogger(__name__)


def register_farm_routes(app):
    """Register farm management routes with Flask app."""

    @app.route('/api/farms', methods=['GET', 'POST', 'OPTIONS'])
    @token_required
    def farms():
        try:
            if request.method == 'GET':
                logger.info(f"Fetching farms for user: {request.user_id}")

                with get_db_context() as db:
                    user_farms = db.query(Farm).filter_by(owner_id=request.user_id).all()

                    return jsonify({
                        "status": "success",
                        "count": len(user_farms),
                        "data": [FarmResponse.from_farm(farm).model_dump() for farm in user_farms]
                    }), 200

            elif request.method == 'POST':
                logger.info(f"Creating new farm for user: {request.user_id}")

                try:
                    data = request.get_json()
                    if not data:
                        return jsonify({
                            "status": "error",
                            "message": "Request body is empty"
                        }), 400

                    farm_data = FarmCreate(**data)
                except ValueError as e:
                    logger.warning(f"Validation error: {e}")
                    return jsonify({
                        "status": "error",
                        "message": f"Validation failed: {str(e)}"
                    }), 400

                with get_db_context() as db:
                    new_farm = Farm(
                        owner_id=request.user_id,
                        name=farm_data.name,
                        location=farm_data.location,
                        state=farm_data.state,
                        district=farm_data.district,
                        size_hectares=farm_data.size_hectares,
                        soil_type=farm_data.soil_type,
                        latitude=farm_data.latitude,
                        longitude=farm_data.longitude
                    )

                    db.add(new_farm)
                    db.commit()
                    db.refresh(new_farm)

                    logger.info(f"Farm created successfully: {new_farm.id}")

                    return jsonify({
                        "status": "success",
                        "message": "Farm created successfully",
                        "data": FarmResponse.from_farm(new_farm).model_dump()
                    }), 201

        except Exception as e:
            logger.error(f"Error in farms endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500

    @app.route('/api/farms/<int:farm_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    @token_required
    def farm_detail(farm_id):
        try:
            with get_db_context() as db:
                farm = db.query(Farm).filter_by(id=farm_id, owner_id=request.user_id).first()

                if not farm:
                    logger.warning(f"Farm not found or user unauthorized: farm_id={farm_id}, user_id={request.user_id}")
                    return jsonify({
                        "status": "error",
                        "message": "Farm not found"
                    }), 404

                if request.method == 'GET':
                    logger.info(f"Fetching farm: {farm_id}")
                    return jsonify({
                        "status": "success",
                        "data": FarmResponse.from_farm(farm).model_dump()
                    }), 200

                elif request.method == 'PUT':
                    logger.info(f"Updating farm: {farm_id}")

                    try:
                        data = request.get_json()
                        if not data:
                            return jsonify({
                                "status": "error",
                                "message": "Request body is empty"
                            }), 400

                        update_data = FarmUpdate(**data)

                        for field, value in update_data.model_dump(exclude_unset=True).items():
                            if value is not None:
                                setattr(farm, field, value)

                        db.commit()
                        db.refresh(farm)

                        logger.info(f"Farm updated: {farm_id}")

                        return jsonify({
                            "status": "success",
                            "message": "Farm updated successfully",
                            "data": FarmResponse.from_farm(farm).model_dump()
                        }), 200

                    except ValueError as e:
                        logger.warning(f"Validation error: {e}")
                        return jsonify({
                            "status": "error",
                            "message": f"Validation failed: {str(e)}"
                        }), 400

                elif request.method == 'DELETE':
                    logger.info(f"Deleting farm: {farm_id}")

                    db.delete(farm)
                    db.commit()

                    logger.info(f"Farm deleted: {farm_id}")

                    return jsonify({
                        "status": "success",
                        "message": "Farm deleted successfully"
                    }), 200

        except Exception as e:
            logger.error(f"Error in farm_detail endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500
