"""OpenAPI documentation routes for Crop Zen."""

from flask import Response, jsonify


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Crop Zen API",
        "version": "1.0.0",
        "description": (
            "Authenticated agricultural advisory APIs for farms, soil history, "
            "crop recommendations, and prediction history."
        ),
    },
    "servers": [
        {"url": "http://localhost:5000", "description": "Local Flask server"}
    ],
    "tags": [
        {"name": "Health"},
        {"name": "Auth"},
        {"name": "Farms"},
        {"name": "Soil Data"},
        {"name": "Predictions"},
        {"name": "Recommendations"},
        {"name": "Reference"},
    ],
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        },
        "schemas": {
            "ApiError": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "error"},
                    "message": {"type": "string"},
                },
            },
            "AuthTokens": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                    "refresh_token": {"type": "string"},
                    "token_type": {"type": "string", "example": "Bearer"},
                    "user": {"$ref": "#/components/schemas/User"},
                },
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "email": {"type": "string", "format": "email"},
                    "first_name": {"type": "string", "nullable": True},
                    "last_name": {"type": "string", "nullable": True},
                    "phone": {"type": "string", "nullable": True},
                    "role": {"type": "string", "example": "farmer"},
                    "is_active": {"type": "boolean"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
            "RegisterRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string", "minLength": 8},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "phone": {"type": "string"},
                },
            },
            "LoginRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string"},
                },
            },
            "FarmInput": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "example": "North Field"},
                    "location": {"type": "string", "example": "Mandya"},
                    "state": {"type": "string", "example": "Karnataka"},
                    "district": {"type": "string", "example": "Mandya"},
                    "size_hectares": {"type": "number", "example": 2.5},
                    "soil_type": {"type": "string", "example": "alluvial"},
                    "latitude": {"type": "number", "example": 12.5222},
                    "longitude": {"type": "number", "example": 76.8958},
                },
            },
            "Farm": {
                "allOf": [
                    {"$ref": "#/components/schemas/FarmInput"},
                    {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "owner_id": {"type": "integer"},
                            "is_active": {"type": "boolean"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"},
                        },
                    },
                ]
            },
            "SoilDataInput": {
                "type": "object",
                "required": ["farm_id"],
                "properties": {
                    "farm_id": {"type": "integer"},
                    "ph": {"type": "number", "minimum": 3, "maximum": 10},
                    "moisture": {"type": "number", "minimum": 0, "maximum": 100},
                    "nitrogen": {"type": "number"},
                    "phosphorus": {"type": "number"},
                    "potassium": {"type": "number"},
                    "organic_matter": {"type": "number"},
                    "ec": {"type": "number"},
                    "measurement_date": {"type": "string", "format": "date-time"},
                    "source": {"type": "string", "example": "farmer_input"},
                    "notes": {"type": "string"},
                },
            },
            "SoilData": {
                "allOf": [
                    {"$ref": "#/components/schemas/SoilDataInput"},
                    {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "created_at": {"type": "string", "format": "date-time"},
                        },
                    },
                ]
            },
            "CropPredictionRequest": {
                "type": "object",
                "required": ["soil_ph", "moisture"],
                "properties": {
                    "soil_ph": {"type": "number", "minimum": 3, "maximum": 10, "example": 6.5},
                    "soilPH": {"type": "number", "minimum": 3, "maximum": 10, "example": 6.5},
                    "moisture": {"type": "number", "minimum": 0, "maximum": 100, "example": 60},
                },
            },
            "PredictionInput": {
                "type": "object",
                "required": ["farm_id", "crop_name", "soil_ph", "moisture", "confidence_score"],
                "properties": {
                    "farm_id": {"type": "integer"},
                    "crop_name": {"type": "string", "example": "Rice"},
                    "soil_ph": {"type": "number", "example": 6.5},
                    "moisture": {"type": "number", "example": 60},
                    "temperature": {"type": "number", "example": 28},
                    "rainfall": {"type": "number", "example": 140},
                    "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "season": {"type": "string", "example": "kharif"},
                },
            },
            "SuccessEnvelope": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "success"},
                    "message": {"type": "string"},
                    "data": {"type": "object"},
                },
            },
        },
        "responses": {
            "Unauthorized": {
                "description": "Missing, invalid, or expired bearer token",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ApiError"}}},
            },
            "NotFound": {
                "description": "Requested resource was not found or is not owned by the user",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ApiError"}}},
            },
            "ValidationError": {
                "description": "Invalid request data",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ApiError"}}},
            },
        },
    },
    "paths": {
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Check API health",
                "responses": {"200": {"description": "API is healthy"}},
            }
        },
        "/api/auth/register": {
            "post": {
                "tags": ["Auth"],
                "summary": "Register a farmer account",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RegisterRequest"}}},
                },
                "responses": {
                    "201": {"description": "User registered"},
                    "400": {"$ref": "#/components/responses/ValidationError"},
                    "409": {"description": "Email already registered"},
                },
            }
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Auth"],
                "summary": "Log in and receive JWT tokens",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginRequest"}}},
                },
                "responses": {
                    "200": {"description": "Login successful"},
                    "401": {"description": "Invalid credentials"},
                },
            }
        },
        "/api/auth/refresh-token": {
            "post": {
                "tags": ["Auth"],
                "summary": "Refresh an access token",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["refresh_token"],
                                "properties": {"refresh_token": {"type": "string"}},
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Token refreshed"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                },
            }
        },
        "/api/auth/me": {
            "get": {
                "tags": ["Auth"],
                "summary": "Get the current authenticated user",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {"description": "Current user"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                },
            }
        },
        "/api/auth/logout": {
            "post": {
                "tags": ["Auth"],
                "summary": "Logout and revoke the current access token",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {"description": "Logged out"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                },
            }
        },
        "/api/farms": {
            "get": {
                "tags": ["Farms"],
                "summary": "List owned farms",
                "security": [{"bearerAuth": []}],
                "responses": {"200": {"description": "Farm list"}, "401": {"$ref": "#/components/responses/Unauthorized"}},
            },
            "post": {
                "tags": ["Farms"],
                "summary": "Create a farm",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FarmInput"}}},
                },
                "responses": {"201": {"description": "Farm created"}, "400": {"$ref": "#/components/responses/ValidationError"}},
            },
        },
        "/api/farms/{farm_id}": {
            "parameters": [{"name": "farm_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "get": {
                "tags": ["Farms"],
                "summary": "Get a farm",
                "security": [{"bearerAuth": []}],
                "responses": {"200": {"description": "Farm detail"}, "404": {"$ref": "#/components/responses/NotFound"}},
            },
            "put": {
                "tags": ["Farms"],
                "summary": "Update a farm",
                "security": [{"bearerAuth": []}],
                "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/FarmInput"}}}},
                "responses": {"200": {"description": "Farm updated"}, "404": {"$ref": "#/components/responses/NotFound"}},
            },
            "delete": {
                "tags": ["Farms"],
                "summary": "Delete a farm",
                "security": [{"bearerAuth": []}],
                "responses": {"200": {"description": "Farm deleted"}, "404": {"$ref": "#/components/responses/NotFound"}},
            },
        },
        "/api/soil-data": {
            "get": {
                "tags": ["Soil Data"],
                "summary": "List soil measurements",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {"name": "farm_id", "in": "query", "schema": {"type": "integer"}},
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 10}},
                ],
                "responses": {"200": {"description": "Soil data list"}},
            },
            "post": {
                "tags": ["Soil Data"],
                "summary": "Create a soil measurement",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SoilDataInput"}}},
                },
                "responses": {"201": {"description": "Soil data recorded"}, "404": {"$ref": "#/components/responses/NotFound"}},
            },
        },
        "/api/farms/{farm_id}/soil-data": {
            "get": {
                "tags": ["Soil Data"],
                "summary": "List soil measurements for a farm",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {"name": "farm_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 10}},
                ],
                "responses": {"200": {"description": "Farm soil history"}, "404": {"$ref": "#/components/responses/NotFound"}},
            }
        },
        "/api/soil-data/{soil_data_id}": {
            "parameters": [{"name": "soil_data_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "get": {
                "tags": ["Soil Data"],
                "summary": "Get a soil measurement",
                "security": [{"bearerAuth": []}],
                "responses": {"200": {"description": "Soil data detail"}, "404": {"$ref": "#/components/responses/NotFound"}},
            },
            "put": {
                "tags": ["Soil Data"],
                "summary": "Update a soil measurement",
                "security": [{"bearerAuth": []}],
                "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/SoilDataInput"}}}},
                "responses": {"200": {"description": "Soil data updated"}, "404": {"$ref": "#/components/responses/NotFound"}},
            },
            "delete": {
                "tags": ["Soil Data"],
                "summary": "Delete a soil measurement",
                "security": [{"bearerAuth": []}],
                "responses": {"200": {"description": "Soil data deleted"}, "404": {"$ref": "#/components/responses/NotFound"}},
            },
        },
        "/api/predict": {
            "post": {
                "tags": ["Recommendations"],
                "summary": "Generate crop recommendations",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/CropPredictionRequest"}},
                        "multipart/form-data": {
                            "schema": {
                                "allOf": [
                                    {"$ref": "#/components/schemas/CropPredictionRequest"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "image": {"type": "string", "format": "binary"}
                                        },
                                    },
                                ]
                            }
                        },
                    },
                },
                "responses": {
                    "200": {"description": "Recommendations generated"},
                    "400": {"$ref": "#/components/responses/ValidationError"},
                    "413": {"description": "Uploaded image too large"},
                },
            }
        },
        "/api/predictions": {
            "get": {
                "tags": ["Predictions"],
                "summary": "List stored prediction history",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 10}},
                ],
                "responses": {"200": {"description": "Prediction history"}},
            },
            "post": {
                "tags": ["Predictions"],
                "summary": "Store a prediction result",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PredictionInput"}}},
                },
                "responses": {"201": {"description": "Prediction stored"}, "404": {"$ref": "#/components/responses/NotFound"}},
            },
        },
        "/api/crops": {
            "get": {
                "tags": ["Reference"],
                "summary": "List supported crops",
                "responses": {"200": {"description": "Supported crop list"}},
            }
        },
    },
}


SWAGGER_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Crop Zen API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.ui = SwaggerUIBundle({
      url: "/api/openapi.json",
      dom_id: "#swagger-ui",
      deepLinking: true,
      persistAuthorization: true
    });
  </script>
</body>
</html>
"""


def register_api_docs_routes(app):
    """Register API documentation routes."""

    @app.route("/api/openapi.json", methods=["GET"])
    def openapi_json():
        return jsonify(OPENAPI_SPEC), 200

    @app.route("/api/docs", methods=["GET"])
    def swagger_ui():
        return Response(SWAGGER_HTML, mimetype="text/html")
