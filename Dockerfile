FROM node:20-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FRONTEND_DIST=/app/frontend_dist

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend-build /frontend/dist ./frontend_dist

EXPOSE 5000

CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && gunicorn -w ${WEB_CONCURRENCY:-2} -b 0.0.0.0:${PORT:-5000} app:app"]
