# Deploy Crop Zen on Railway as One Web App

Use this if you want backend and frontend on the same public Railway URL.

Railway services:

- `crop-zen-db`: PostgreSQL
- `crop-zen-web`: one Docker service serving both React frontend and Flask API

## 1. Create Project

1. Open Railway.
2. Create a new project.
3. Add a PostgreSQL database.
4. Add a service from GitHub repo `Rushyasree/SmartCrop-FuzzyLogic`.

## 2. Web Service Settings

For the `crop-zen-web` service:

```text
Root Directory: /
Config file path: /railway.json
Dockerfile path: Dockerfile
```

If Railway only asks for the root directory, keep it as the repository root.

## 3. Web Service Variables

Add these variables:

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
FRONTEND_DIST=/app/frontend_dist
```

Because frontend and backend are on the same domain, you do not need a separate `VITE_API_URL`. The React app will call `/api` on the same Railway domain.

## 4. Deploy

1. Deploy the web service.
2. Open service settings.
3. Generate a public Railway domain.
4. Open the generated URL.

The same URL serves:

```text
https://your-app.up.railway.app
https://your-app.up.railway.app/api/health
https://your-app.up.railway.app/api/docs
```

## 5. Test

1. Open the frontend URL.
2. Register a new user.
3. Add a farm.
4. Add soil data.
5. Generate a crop recommendation.
6. Open `/api/docs` to show the API documentation.

## 6. Recommended Railway Plan Note

This app includes TensorFlow and ML model artifacts, so the image is larger than a simple Flask app. If a free/trial deploy fails due to memory or image-size limits, upgrade the Railway project or temporarily disable disease inference for the public demo.
