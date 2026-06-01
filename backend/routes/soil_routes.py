"""Soil data routes."""

import logging
import math

from flask import jsonify, request

from database import get_db_context
from models import Farm, SoilData
from routes.auth_routes import token_required
from schemas.soil_schema import SoilDataCreate, SoilDataResponse, SoilDataUpdate

logger = logging.getLogger(__name__)


def register_soil_data_routes(app):
    """Register soil data routes with Flask app."""

    @app.route('/api/soil-data', methods=['GET', 'POST', 'OPTIONS'])
    @token_required
    def soil_data_collection():
        try:
            if request.method == 'GET':
                page = max(request.args.get('page', 1, type=int), 1)
                per_page = min(max(request.args.get('per_page', 10, type=int), 1), 100)
                farm_id = request.args.get('farm_id', type=int)

                with get_db_context() as db:
                    base_query = db.query(SoilData).join(
                        Farm, SoilData.farm_id == Farm.id
                    ).filter(
                        Farm.owner_id == request.user_id
                    )

                    if farm_id is not None:
                        base_query = base_query.filter(SoilData.farm_id == farm_id)

                    total = base_query.count()
                    records = base_query.order_by(
                        SoilData.created_at.desc()
                    ).offset((page - 1) * per_page).limit(per_page).all()

                    return jsonify({
                        "status": "success",
                        "count": len(records),
                        "page": page,
                        "total": total,
                        "pages": math.ceil(total / per_page) if total else 0,
                        "data": [SoilDataResponse.from_soil_data(record).model_dump() for record in records]
                    }), 200

            elif request.method == 'POST':
                try:
                    data = request.get_json()
                    if not data:
                        return jsonify({
                            "status": "error",
                            "message": "Request body is empty"
                        }), 400

                    soil_data = SoilDataCreate(**data)
                except ValueError as e:
                    logger.warning(f"Validation error: {e}")
                    return jsonify({
                        "status": "error",
                        "message": f"Validation failed: {str(e)}"
                    }), 400

                with get_db_context() as db:
                    farm = db.query(Farm).filter_by(
                        id=soil_data.farm_id,
                        owner_id=request.user_id
                    ).first()

                    if not farm:
                        return jsonify({
                            "status": "error",
                            "message": "Farm not found"
                        }), 404

                    new_soil_data = SoilData(
                        farm_id=soil_data.farm_id,
                        ph=soil_data.ph,
                        moisture=soil_data.moisture,
                        nitrogen=soil_data.nitrogen,
                        phosphorus=soil_data.phosphorus,
                        potassium=soil_data.potassium,
                        organic_matter=soil_data.organic_matter,
                        ec=soil_data.ec,
                        measurement_date=soil_data.measurement_date,
                        source=soil_data.source,
                        notes=soil_data.notes
                    )

                    db.add(new_soil_data)
                    db.commit()
                    db.refresh(new_soil_data)

                    return jsonify({
                        "status": "success",
                        "message": "Soil data recorded successfully",
                        "data": SoilDataResponse.from_soil_data(new_soil_data).model_dump()
                    }), 201

        except Exception as e:
            logger.error(f"Error in soil_data_collection endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500

    @app.route('/api/farms/<int:farm_id>/soil-data', methods=['GET', 'OPTIONS'])
    @token_required
    def farm_soil_data(farm_id):
        try:
            page = max(request.args.get('page', 1, type=int), 1)
            per_page = min(max(request.args.get('per_page', 10, type=int), 1), 100)

            with get_db_context() as db:
                farm = db.query(Farm).filter_by(id=farm_id, owner_id=request.user_id).first()
                if not farm:
                    return jsonify({
                        "status": "error",
                        "message": "Farm not found"
                    }), 404

                base_query = db.query(SoilData).filter_by(farm_id=farm_id)
                total = base_query.count()
                records = base_query.order_by(
                    SoilData.created_at.desc()
                ).offset((page - 1) * per_page).limit(per_page).all()

                return jsonify({
                    "status": "success",
                    "count": len(records),
                    "page": page,
                    "total": total,
                    "pages": math.ceil(total / per_page) if total else 0,
                    "data": [SoilDataResponse.from_soil_data(record).model_dump() for record in records]
                }), 200

        except Exception as e:
            logger.error(f"Error in farm_soil_data endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500

    @app.route('/api/soil-data/<int:soil_data_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    @token_required
    def soil_data_detail(soil_data_id):
        try:
            with get_db_context() as db:
                record = db.query(SoilData).join(
                    Farm, SoilData.farm_id == Farm.id
                ).filter(
                    SoilData.id == soil_data_id,
                    Farm.owner_id == request.user_id
                ).first()

                if not record:
                    return jsonify({
                        "status": "error",
                        "message": "Soil data not found"
                    }), 404

                if request.method == 'GET':
                    return jsonify({
                        "status": "success",
                        "data": SoilDataResponse.from_soil_data(record).model_dump()
                    }), 200

                elif request.method == 'PUT':
                    try:
                        data = request.get_json()
                        if not data:
                            return jsonify({
                                "status": "error",
                                "message": "Request body is empty"
                            }), 400

                        update_data = SoilDataUpdate(**data)
                    except ValueError as e:
                        logger.warning(f"Validation error: {e}")
                        return jsonify({
                            "status": "error",
                            "message": f"Validation failed: {str(e)}"
                        }), 400

                    for field, value in update_data.model_dump(exclude_unset=True).items():
                        setattr(record, field, value)

                    db.commit()
                    db.refresh(record)

                    return jsonify({
                        "status": "success",
                        "message": "Soil data updated successfully",
                        "data": SoilDataResponse.from_soil_data(record).model_dump()
                    }), 200

                elif request.method == 'DELETE':
                    db.delete(record)
                    db.commit()

                    return jsonify({
                        "status": "success",
                        "message": "Soil data deleted successfully"
                    }), 200

        except Exception as e:
            logger.error(f"Error in soil_data_detail endpoint: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred"
            }), 500
