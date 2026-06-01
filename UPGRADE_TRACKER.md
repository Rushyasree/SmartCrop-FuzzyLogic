# Crop Zen Upgrade Tracker

Last updated: 2026-05-31

## Done During Upgrade Work

- Fixed backend model/route mismatches for farm ownership and prediction fields.
- Added temperature/rainfall support to stored predictions.
- Fixed SQLAlchemy pagination.
- Made backend testable with SQLite.
- Created clean `.codex-venv` and restored a passing backend test suite.
- Modernized Pydantic and timestamp warnings in active code paths.
- Hardened image uploads with byte-signature validation and JSON `413` handling.
- Made `/api/predict` support JSON and multipart form-data.
- Added recommendation reasons and model metadata.
- Added crop recommendation service layer.
- Renamed the old simple crop recommender to an explicit legacy pH/moisture fallback and removed the unused scikit-fuzzy dependency.
- Added authenticated soil data APIs.
- Split farm, soil, and prediction routes into `backend/routes/`.
- Moved Pydantic request/response schemas into `backend/schemas/`.
- Added Alembic configuration and an initial schema migration.
- Added OpenAPI JSON and Swagger UI documentation endpoints.
- Built a React dashboard with auth, farms, soil history, recommendations, prediction history, charts, and profile views.
- Trained a Random Forest crop recommendation model from the downloaded crop dataset.
- Saved crop model artifact, labels, feature scaler pipeline, and metrics.
- Added MobileNetV2 disease model training script.
- Added TensorFlow/Keras disease inference loader with treatment hints and beta fallback.
- Trained the disease model for 5 epochs with MobileNetV2 and ImageNet weights.
- Verified disease inference on Apple cedar rust images after fixing duplicate preprocessing.
- Added disease evaluation script with stratified validation metrics and confusion-matrix export.
- Added loose test-image disease validation with known-failure reporting.
- Added disease top-k alternatives and low-confidence warnings.
- Added rate limiting helpers, logout/token revocation, refresh-token rotation, production secret checks, and role helper.
- Added backend/frontend Dockerfiles and `docker-compose.yml` with PostgreSQL.
- Added GitHub Actions CI.
- Updated README, project status, and launch guide.

Current verification:

```text
Backend: 75 passed
Frontend: npm run build passed
Crop model: trained, accuracy 0.9955
Disease model: trained MobileNetV2 artifact, validation accuracy 0.9603
Disease evaluation: stratified accuracy 0.9741, macro F1 0.9738, 14,058 images
Disease demo validation: accuracy 0.9394, 31/33 correct
```

## Still Needed

### Disease Detection

- Validate disease detection against farmer/field-captured images, not only curated and bundled demo images.

### Production Security

- Persist revoked token IDs in Redis/PostgreSQL.
- Add centralized audit logging.
- Add stricter deployment secret management.

### Product Polish

- Add public deployment.
- Add demo screenshots/video.
- Add end-to-end tests for the React dashboard.
