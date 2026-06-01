# Crop Zen Launch Guide

Last updated: 2026-05-30

## Current Status

```text
Overall: about 65 percent complete for a portfolio-grade project
Backend: strong prototype, authenticated APIs, soil data APIs, 73 passing tests
Frontend: static pages plus Vite/React setup; real React dashboard pending
ML: rule-based crop recommendation only; real ML baseline pending
Disease detection: placeholder only
DevOps: Docker, CI/CD, deployment guide pending
```

## What Works Now

### Backend

- User registration/login with JWT.
- Token refresh and current-user endpoint.
- Protected farm CRUD APIs.
- Protected soil data CRUD/list APIs.
- Prediction history APIs.
- `/api/predict` supports:
  - JSON input
  - multipart form-data input
  - optional image upload
  - recommendation explanations
  - model metadata
- Upload safety:
  - extension checks
  - image byte-signature checks
  - JSON `413` for oversized uploads
- SQLite-compatible automated tests.

Current backend test result:

```text
73 passed
```

### Frontend

- Static HTML/CSS/JS pages exist.
- Static prediction UI can display recommendation reasons.
- Vite/React config exists and production build was fixed.
- Full React dashboard is still not implemented.

## What Is Not Production-Ready Yet

- Real crop ML model.
- Real disease detection model.
- Alembic migration files for the latest model changes.
- React dashboard.
- OpenAPI/Swagger/Postman docs.
- Docker and cloud deployment setup.
- Rate limiting, logout/token revocation, production secret checks, and role-based permissions.

## Recommended Next Build Paths

### Option A: Backend Architecture Polish

Best if you want cleaner code before adding more features.

1. Move schemas into `backend/schemas/`.
2. Move more business logic into `backend/services/`.
3. Generate Alembic migrations.
4. Add OpenAPI docs.

### Option B: React Dashboard

Best if you want the project to look impressive in demos.

Build these pages first:

1. Login/register.
2. Dashboard overview.
3. Farm management.
4. Soil data history.
5. Crop recommendation form.
6. Prediction history.

### Option C: ML Baseline

Best if you want the project to be more AI-focused.

1. Add a crop dataset with N, P, K, temperature, humidity, pH, and rainfall.
2. Train RandomForest or XGBoost baseline.
3. Save model with `joblib`.
4. Add model inference service.
5. Compare rule-based vs ML output.

### Option D: Deployment

Best after backend and frontend are stable.

1. Add backend Dockerfile.
2. Add frontend Dockerfile.
3. Add `docker-compose.yml` with PostgreSQL.
4. Add GitHub Actions.
5. Deploy backend and frontend.

## Backend Test Command

```powershell
cd E:\Documents\Crop_Zen\backend
$env:DATABASE_URL='sqlite:///C:/Users/trush/OneDrive/Documents/New project/crop_zen_test.db'
$env:SECRET_KEY='test-secret-key-for-local-tests'
$env:LOG_FOLDER='C:/Users/trush/OneDrive/Documents/New project/crop_zen_logs'
$env:UPLOAD_FOLDER='C:/Users/trush/OneDrive/Documents/New project/crop_zen_uploads'
$env:PYTHONDONTWRITEBYTECODE='1'
E:\Documents\Crop_Zen\.codex-venv\Scripts\python.exe -m pytest test_app.py test_phase2.py -q -p no:cacheprovider
```

## Frontend Commands

```bash
cd frontend
npm install
npm run dev
npm run build
```

## Recommended Immediate Next Step

Move schemas out of `app.py`, `auth_routes.py`, and `data_routes.py` into a `backend/schemas/` package. This will make the backend easier to maintain before adding more APIs or a real ML pipeline.
