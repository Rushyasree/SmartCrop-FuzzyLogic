# Crop Zen Project Status

Last updated: 2026-05-31

## Summary

Crop Zen is now a portfolio-ready full-stack agricultural advisory prototype. It has a tested Flask backend, authenticated farm and soil APIs, OpenAPI docs, Alembic migrations, Docker/CI scaffolding, a React dashboard, security hardening, a trained dataset-backed crop recommendation model, and trained MobileNetV2 disease-image inference.

Overall current status: about 90 percent complete for a portfolio-grade project.

## Completed

### Backend API

- Health endpoint.
- Auth routes:
  - Register
  - Login
  - Refresh token with rotation
  - Logout/token revocation
  - Current user
- Farm routes:
  - Create/list farms
  - Get/update/delete owned farm
- Soil data routes:
  - Create/list soil measurements
  - Filter soil data by farm
  - Get/update/delete individual soil data records
  - Farm ownership enforcement
- Prediction history routes:
  - Store predictions
  - Paginated prediction listing
- Recommendation endpoint:
  - JSON input
  - Multipart form-data image upload
  - Legacy pH/moisture fallback for older/simple requests
  - Trained crop model for NPK/weather inputs
- API documentation:
  - Swagger UI at `/api/docs`
  - OpenAPI JSON at `/api/openapi.json`

### Backend Quality

- SQLAlchemy models for users, farms, soil data, predictions, disease detections, and alerts.
- SQLite-compatible tests and PostgreSQL-ready runtime configuration.
- Pydantic schemas extracted into `backend/schemas/`.
- Farm, soil, and prediction APIs split into `backend/routes/`.
- Alembic migration environment with initial schema migration.
- Upload hardening with byte-signature validation and JSON `413` handling.
- Rate limiting helper for auth and prediction routes.
- Production `SECRET_KEY` validation.
- Role-permission helper for future admin/researcher endpoints.
- Backend tests passing:

```text
75 passed
```

### Frontend

- Working React dashboard under `frontend/src/`.
- Login/register panel connected to backend auth.
- Dashboard overview cards.
- Farm management UI.
- Soil history UI with NPK chart.
- Crop recommendation form using pH, moisture, NPK, temperature, humidity, and rainfall.
- Recommendation explanation panel.
- Prediction history page.
- Profile page.
- Responsive layout and accessible focus states.
- Vite production build passing.

### DevOps

- Backend Dockerfile.
- Frontend Dockerfile with Nginx static serving.
- `docker-compose.yml` with PostgreSQL, backend, and frontend services.
- GitHub Actions CI for backend tests and frontend build.
- Lean `requirements-ci.txt` for CI speed.

## Partially Complete

### Machine Learning

- Implemented: trained Random Forest crop recommender.
- Dataset: `backend/data/crop_recommendation.csv/Crop_recommendation.csv`.
- Artifact: `backend/ml_models/crop_recommendation_model.joblib`.
- Metrics: `backend/ml_models/crop_recommendation_metrics.json`.
- Accuracy: `0.9955`.
- Features:
  - Nitrogen
  - Phosphorus
  - Potassium
  - Temperature
  - Humidity
  - pH
  - Rainfall
- Fallback: deterministic NPK/weather baseline if the artifact is missing.
- Final fallback: legacy pH/moisture recommender for simple requests.

### Disease Detection

- Implemented: TensorFlow/Keras inference loader, label decoding, confidence score, top-3 alternatives, low-confidence warnings, treatment hints, and beta fallback.
- Training script: `backend/scripts/train_disease_model.py`.
- Dataset: `backend/data/plant_disease/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)`.
- Trained artifact: `backend/ml_models/disease_detection_model.keras`.
- Labels/metrics created: `backend/ml_models/disease_labels.json`.
- Artifact details: MobileNetV2, ImageNet weights, 38 classes, 5 epochs, image size 224.
- Final training accuracy: `0.9558`.
- Final validation accuracy: `0.9603`.
- Evaluation script: `backend/scripts/evaluate_disease_model.py`.
- Evaluation artifacts:
  - `backend/ml_models/disease_evaluation.json`
  - `backend/ml_models/disease_confusion_matrix.csv`
- Stratified evaluation accuracy: `0.9741` across `14,058` validation-split images.
- Macro F1 score: `0.9738`.
- Loose test-image validation script: `backend/scripts/validate_disease_test_images.py`.
- Loose test-image validation artifacts:
  - `backend/ml_models/disease_field_validation.json`
  - `backend/ml_models/disease_field_validation.csv`
- Loose test-image validation accuracy: `0.9394` across `33` labeled demo images.
- Known demo-image failures:
  - `AppleScab3.JPG` predicted as `Squash___Powdery_mildew` with low-confidence warning.
  - `TomatoEarlyBlight3.JPG` predicted as `Tomato___Target_Spot` with low-confidence warning.
- Disease API responses now expose `top_predictions`, `confidence_threshold`, and `is_low_confidence` so the UI can avoid presenting uncertain predictions as final diagnoses.
- Verified inference after removing duplicate preprocessing: Apple cedar rust test images classify as `Apple - Cedar apple rust` with confidence above `0.9999`.
- Still needed: validate against farmer/field-captured images before positioning this as production-grade plant pathology.

### Security

- Implemented: rate limiting helper, token revocation/logout, refresh rotation, production secret checks, role helper.
- Still needed for production: persistent token denylist in Redis/PostgreSQL and centralized audit logging.

## Current Test Command

```powershell
$env:DATABASE_URL='sqlite:///C:/Users/trush/OneDrive/Documents/New project/crop_zen_test.db'
$env:SECRET_KEY='test-secret-key-for-local-tests'
$env:LOG_FOLDER='C:/Users/trush/OneDrive/Documents/New project/crop_zen_logs'
$env:UPLOAD_FOLDER='C:/Users/trush/OneDrive/Documents/New project/crop_zen_uploads'
$env:PYTHONDONTWRITEBYTECODE='1'
E:\Documents\Crop_Zen\.codex-venv\Scripts\python.exe -m pytest test_app.py test_phase2.py -q -p no:cacheprovider
```

## Current Build Command

```powershell
cd E:\Documents\Crop_Zen\frontend
npm run build
```

## Current Crop Training Command

```powershell
cd E:\Documents\Crop_Zen\backend
E:\Documents\Crop_Zen\.codex-venv\Scripts\python.exe scripts\train_crop_model.py
```

## Current Disease Training Command

```powershell
cd E:\Documents\Crop_Zen\backend
E:\Documents\Crop_Zen\.codex-venv\Scripts\python.exe scripts\train_disease_model.py --epochs 5 --batch-size 32 --image-size 224
```

## Current Disease Evaluation Command

```powershell
cd E:\Documents\Crop_Zen\backend
E:\Documents\Crop_Zen\.codex-venv\Scripts\python.exe scripts\evaluate_disease_model.py --batch-size 32
```

## Current Disease Demo Validation Command

```powershell
cd E:\Documents\Crop_Zen\backend
E:\Documents\Crop_Zen\.codex-venv\Scripts\python.exe -B scripts\validate_disease_test_images.py
```

Quick smoke artifact command:

```powershell
cd E:\Documents\Crop_Zen\backend
E:\Documents\Crop_Zen\.codex-venv\Scripts\python.exe scripts\train_disease_model.py --epochs 1 --batch-size 16 --image-size 128 --max-images-per-class 10 --no-imagenet-weights
```

## Current Migration Command

```powershell
$env:DATABASE_URL='postgresql://postgres:password@localhost:5432/crop_zen'
E:\Documents\Crop_Zen\.codex-venv\Scripts\alembic.exe -c E:\Documents\Crop_Zen\backend\alembic.ini upgrade head
```

## Recommended Priority Order

1. Persist refresh-token rotation/revocation in Redis/PostgreSQL.
2. Add public deployment.
3. Collect farmer/field-captured disease images and compare them against the current demo-image results.
4. Add demo screenshots/video for resume and placement use.
