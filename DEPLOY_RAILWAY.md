# Deploy Crop Zen on Railway

This project is a monorepo. Deploy it on Railway as three services:

- `crop-zen-db`: PostgreSQL database
- `crop-zen-backend`: Flask API from `/backend`
- `crop-zen-frontend`: React/Vite frontend from `/frontend`

## 1. Push This Repository

Make sure the latest code is pushed to GitHub before creating Railway services.

## 2. Create Railway Project

1. Open Railway and create a new project.
2. Add a PostgreSQL database service.
3. Add a backend service from the GitHub repository.
4. Add a frontend service from the same GitHub repository.

## 3. Backend Service Settings

Set the backend service root directory:

```text
/backend
```

If Railway asks for a config file path, use:

```text
/backend/railway.json
```

Set these backend variables:

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<generate-a-long-random-secret>
FLASK_ENV=production
FLASK_DEBUG=false
LOG_FOLDER=logs
UPLOAD_FOLDER=uploads
MAX_UPLOAD_SIZE=5242880
CROP_MODEL_PATH=ml_models/crop_recommendation_model.joblib
DISEASE_MODEL_PATH=ml_models/disease_detection_model.keras
DISEASE_LABELS_PATH=ml_models/disease_labels.json
FRONTEND_URL=https://your-frontend-domain.up.railway.app
FRONTEND_URLS=https://your-frontend-domain.up.railway.app
```

After the frontend URL is known, update `FRONTEND_URL` and `FRONTEND_URLS`.

The backend healthcheck is:

```text
/api/health
```

The API docs will be available at:

```text
https://your-backend-domain.up.railway.app/api/docs
```

## 4. Frontend Service Settings

Set the frontend service root directory:

```text
/frontend
```

If Railway asks for a config file path, use:

```text
/frontend/railway.json
```

Set this frontend variable before deploying:

```text
VITE_API_URL=https://your-backend-domain.up.railway.app/api
```

The frontend healthcheck is:

```text
/index.html
```

## 5. Deployment Order

1. Deploy PostgreSQL first.
2. Deploy backend.
3. Generate/open the backend public domain.
4. Set `VITE_API_URL` on the frontend service.
5. Deploy frontend.
6. Generate/open the frontend public domain.
7. Set backend `FRONTEND_URL` and `FRONTEND_URLS` to the frontend public domain.
8. Redeploy backend.

## 6. Quick Smoke Test

Open:

```text
https://your-backend-domain.up.railway.app/api/health
https://your-backend-domain.up.railway.app/api/docs
https://your-frontend-domain.up.railway.app
```

Then register a new user in the frontend and create a farm. If registration works, the frontend, backend, JWT auth, CORS, and PostgreSQL connection are all working together.

## 7. Resume Bullet

After deploying, you can write:

```text
Deployed a full-stack AI agriculture advisory platform on Railway with Flask, React, PostgreSQL, JWT auth, Docker, OpenAPI docs, trained crop recommendation, and disease-image inference.
```
