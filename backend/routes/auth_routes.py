"""Authentication route exports.

The implementation currently lives in the legacy root-level auth_routes module.
This module provides the new routes package import path while preserving
backward compatibility.
"""

from auth_routes import register_user_routes, token_required

__all__ = ["register_user_routes", "token_required"]
