"""Security helpers for production-facing Flask routes."""

import os
import time
from collections import defaultdict, deque
from functools import wraps

from flask import current_app, jsonify, request


UNSAFE_SECRET_KEYS = {
    "",
    "your-secret-key-change-in-production",
    "your-super-secret-key-change-in-production",
    "test-secret-key-for-local-tests",
}

REVOKED_TOKENS = set()
RATE_LIMIT_BUCKETS = defaultdict(deque)


def validate_production_secret():
    """Fail fast when production uses a known placeholder secret."""
    env_name = os.getenv("FLASK_ENV", "development").lower()
    if env_name not in {"production", "prod"}:
        return

    secret_key = os.getenv("SECRET_KEY", "")
    if secret_key in UNSAFE_SECRET_KEYS or len(secret_key) < 32:
        raise RuntimeError(
            "Production SECRET_KEY must be unique, random, and at least 32 characters."
        )


def revoke_token_id(token_id):
    """Mark a token id as revoked for this process."""
    if token_id:
        REVOKED_TOKENS.add(token_id)


def is_token_revoked(token_id):
    """Return whether a token id has been revoked."""
    return bool(token_id and token_id in REVOKED_TOKENS)


def _client_key():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.remote_addr
    return f"{ip or 'unknown'}:{request.endpoint or request.path}"


def rate_limit(max_requests=60, window_seconds=60):
    """Simple in-process sliding-window rate limiter."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.method == "OPTIONS" or current_app.config.get("TESTING"):
                return fn(*args, **kwargs)

            now = time.time()
            bucket = RATE_LIMIT_BUCKETS[_client_key()]

            while bucket and now - bucket[0] > window_seconds:
                bucket.popleft()

            if len(bucket) >= max_requests:
                return jsonify({
                    "status": "error",
                    "message": "Too many requests. Please try again shortly."
                }), 429

            bucket.append(now)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def role_required(*allowed_roles):
    """Require an authenticated user role for future admin/researcher routes."""
    normalized_roles = {role.lower() for role in allowed_roles}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(request, "user", None)
            role = getattr(getattr(user, "role", None), "value", None)
            if not user or role not in normalized_roles:
                return jsonify({
                    "status": "error",
                    "message": "You do not have permission to perform this action."
                }), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator
