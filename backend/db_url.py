import os


def resolve_database_url(default: str | None = None) -> str:
    """Resolve the database URL from common Railway/PostgreSQL env vars."""
    for name in ("DATABASE_URL", "POSTGRES_URL", "POSTGRES_DATABASE_URL", "RAILWAY_DATABASE_URL"):
        value = os.getenv(name)
        if value:
            return value.replace("postgres://", "postgresql://", 1)

    if os.getenv("FLASK_ENV") == "production":
        raise RuntimeError(
            "Missing DATABASE_URL. In Railway, add a PostgreSQL service and set "
            "DATABASE_URL=${{Postgres.DATABASE_URL}} on the web service."
        )

    return default or "postgresql://postgres:password@localhost:5432/crop_zen"
