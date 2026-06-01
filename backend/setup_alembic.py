"""
Alembic migration helper for Crop Zen.

This script checks that the configured database is reachable and applies all
checked-in migrations. It does not generate migrations automatically; create new
revisions intentionally after model changes.
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))


def run_command(args):
    """Run an Alembic command from the backend directory."""
    executable = Path(sys.executable).with_name("alembic.exe")
    command = [str(executable) if executable.exists() else "alembic", "-c", "alembic.ini", *args]
    return subprocess.run(
        command,
        cwd=str(backend_path),
        capture_output=True,
        text=True,
        check=False,
    )


def test_database_connection():
    """Test database connection before running migrations."""
    from database import test_connection

    print("Testing database connection...")
    if test_connection():
        return True

    print("Database connection failed. Check DATABASE_URL and database availability.")
    return False


def show_current_revision():
    """Print the current migration revision."""
    result = run_command(["current"])
    if result.returncode != 0:
        print(result.stderr)
        return False

    print(result.stdout.strip() or "No migration revision applied yet.")
    return True


def run_migrations():
    """Apply all pending migrations."""
    print("Running migrations...")
    result = run_command(["upgrade", "head"])
    if result.returncode != 0:
        print(result.stderr)
        return False

    print(result.stdout.strip() or "Migrations applied.")
    return True


def main():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/crop_zen")

    print("=" * 70)
    print("CROP ZEN - DATABASE MIGRATIONS")
    print("=" * 70)
    print(f"Database: {'...@' + database_url.split('@')[-1] if '@' in database_url else database_url}")

    if not test_database_connection():
        return False

    show_current_revision()
    if not run_migrations():
        return False

    print("Database migrations complete.")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
