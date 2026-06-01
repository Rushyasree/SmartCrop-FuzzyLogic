# Crop Zen

Crop Zen is a full-stack agricultural advisory platform for managing farms, recording soil data, and generating crop recommendations from soil and weather conditions. The backend uses Flask, SQLAlchemy, Alembic, JWT authentication, OpenAPI docs, and a trained crop recommendation model. The frontend includes a working React dashboard.

## Current Working Features

- React dashboard with login/register, overview metrics, farms, soil history, recommendations, prediction history, profile, charts, and responsive layouts.
- User registration, login, JWT access/refresh tokens, refresh-token rotation, logout/token revocation, and protected routes.
- Farm CRUD APIs.
- Soil data CRUD/list APIs with farm ownership checks.
- Prediction history APIs.
- Crop recommendation API supporting JSON and multipart form-data.
- Trained Random Forest crop recommendation model using nitrogen, phosphorus, potassium, temperature, humidity, pH, and rainfall.
- Saved crop model artifact and metrics in `backend/ml_models/`.
- Legacy pH/moisture fallback for older/simple requests when full trained-model features are missing.
- Disease-image inference path with a trained MobileNetV2 `.keras` artifact, label metadata, top-3 alternatives, and low-confidence warnings.
- Image upload validation using file extensions and image byte signatures.
- Rate limiting helpers, production secret checks, and role-permission helper.
- SQLite-compatible test mode and PostgreSQL-ready database config.
- Alembic migration environment with an initial schema migration.
- Split route modules and extracted Pydantic schemas.
- Swagger UI and OpenAPI JSON documentation endpoints.
- Dockerfiles, `docker-compose.yml` with PostgreSQL, and GitHub Actions CI.
- Backend test suite passing: `75 passed`.

## Important Limitations

- Crop model quality depends on the downloaded Kaggle-style dataset; current local test accuracy is `0.9955`.
- Disease detection is trained on the local PlantVillage-style dataset; validate it further on real field images before using it for agricultural decisions.
- Token revocation is in-process; production should persist revoked/rotated token IDs in Redis or the database.

## Backend Quick Start

```bash
cd backend
..\.codex-venv\Scripts\python.exe -m pytest test_app.py test_phase2.py -q -p no:cacheprovider
```

Use PostgreSQL for normal development, or SQLite for lightweight tests:

```bash
set DATABASE_URL=sqlite:///crop_zen_test.db
set SECRET_KEY=test-secret-key-for-local-tests
set LOG_FOLDER=logs
set UPLOAD_FOLDER=uploads
pytest test_app.py test_phase2.py -q
```

Run migrations before starting against a real database:

```bash
alembic -c alembic.ini upgrade head
```

## ML Training

Train the crop recommendation model:

```bash
cd backend
python scripts/train_crop_model.py
```

Current trained crop artifact:

- `backend/ml_models/crop_recommendation_model.joblib`
- `backend/ml_models/crop_recommendation_metrics.json`
- Accuracy: `0.9955`
- Classes: `22`

Train the disease model from the downloaded image dataset:

```bash
cd backend
python scripts/train_disease_model.py --epochs 5
```

For a quick local smoke artifact:

```bash
python scripts/train_disease_model.py --epochs 1 --batch-size 16 --image-size 128 --max-images-per-class 10 --no-imagenet-weights
```

The current trained disease artifact is:

- `backend/ml_models/disease_detection_model.keras`
- `backend/ml_models/disease_labels.json`
- Classes: `38`
- Model: MobileNetV2 with ImageNet weights
- Epochs: `5`
- Final training accuracy: `0.9558`
- Final validation accuracy: `0.9603`
- Stratified evaluation accuracy: `0.9741` across `14,058` validation-split images
- Evaluation artifacts: `backend/ml_models/disease_evaluation.json` and `backend/ml_models/disease_confusion_matrix.csv`
- Loose test-image validation: `0.9394` accuracy on `33` labeled demo images
- Field/demo validation artifacts: `backend/ml_models/disease_field_validation.json` and `backend/ml_models/disease_field_validation.csv`
- Disease API responses include `top_predictions`, `confidence_threshold`, and `is_low_confidence`.
- Verified inference: Apple cedar rust test image predicted as `Apple - Cedar apple rust` with confidence above `0.9999`

Generate disease per-class metrics and a confusion matrix:

```bash
cd backend
python scripts/evaluate_disease_model.py --batch-size 32
```

Validate loose demo/test images and capture known failures:

```bash
cd backend
python scripts/validate_disease_test_images.py
```

## Frontend Quick Start

```bash
cd frontend
npm install
npm run dev
```

Production build:

```bash
npm run build
```

## Docker

```bash
set SECRET_KEY=replace-with-a-secure-random-value
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`
- Swagger UI: `http://localhost:5000/api/docs`

## Railway Deployment

Railway deployment files are included for a public full-stack demo with PostgreSQL:

- `backend/railway.json`
- `frontend/railway.json`
- `DEPLOY_RAILWAY.md`

Deploy the repository as three Railway services: PostgreSQL, backend from `/backend`, and frontend from `/frontend`. Set the frontend `VITE_API_URL` to the backend public URL plus `/api`, then set backend `FRONTEND_URL`/`FRONTEND_URLS` to the frontend public URL.

## Main API Areas

- `GET /api/health`
- `GET /api/docs`
- `GET /api/openapi.json`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh-token`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET/POST /api/farms`
- `GET/PUT/DELETE /api/farms/<farm_id>`
- `GET/POST /api/soil-data`
- `GET /api/farms/<farm_id>/soil-data`
- `GET/PUT/DELETE /api/soil-data/<soil_data_id>`
- `POST /api/predict`
- `GET/POST /api/predictions`

## Recommended Next Upgrades

1. Persist refresh-token rotation and revoked tokens in Redis/PostgreSQL.
2. Add centralized API error helpers and audit logging.
3. Expand disease validation with real farmer/field images beyond the bundled demo images.
4. Deploy a public demo with screenshots and a short walkthrough video.
