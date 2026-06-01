# Crop Zen Backend API Documentation

Version: 1.0.0  
Base URL: `http://localhost:5000`

## Interactive Docs

The backend now exposes live OpenAPI documentation:

- Swagger UI: `GET /api/docs`
- OpenAPI JSON: `GET /api/openapi.json`

Run the Flask server, then open:

```text
http://localhost:5000/api/docs
```

## Authentication

Most farm, soil data, and prediction-history endpoints require a JWT access token:

```text
Authorization: Bearer <access_token>
```

Create tokens with:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh-token`

## Main Endpoints

### Public

- `GET /health`
- `POST /api/predict`
- `GET /api/crops`
- `GET /api/docs`
- `GET /api/openapi.json`

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh-token`
- `GET /api/auth/me`

### Farms

- `GET /api/farms`
- `POST /api/farms`
- `GET /api/farms/<farm_id>`
- `PUT /api/farms/<farm_id>`
- `DELETE /api/farms/<farm_id>`

### Soil Data

- `GET /api/soil-data`
- `POST /api/soil-data`
- `GET /api/farms/<farm_id>/soil-data`
- `GET /api/soil-data/<soil_data_id>`
- `PUT /api/soil-data/<soil_data_id>`
- `DELETE /api/soil-data/<soil_data_id>`

### Prediction History

- `GET /api/predictions`
- `POST /api/predictions`

## Quick Examples

### Register

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"farmer@example.com\",\"password\":\"Password123\",\"first_name\":\"Demo\",\"last_name\":\"Farmer\"}"
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"farmer@example.com\",\"password\":\"Password123\"}"
```

### JSON Crop Recommendation

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d "{\"soil_ph\":6.5,\"moisture\":60}"
```

### Multipart Crop Recommendation With Image

```bash
curl -X POST http://localhost:5000/api/predict \
  -F "soilPH=6.5" \
  -F "moisture=60" \
  -F "image=@leaf.png"
```

### Create Soil Data

```bash
curl -X POST http://localhost:5000/api/soil-data \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d "{\"farm_id\":1,\"ph\":6.5,\"moisture\":60,\"nitrogen\":80,\"phosphorus\":40,\"potassium\":45}"
```

## Status

The OpenAPI schema is maintained in `api_docs.py` and is covered by backend tests.
