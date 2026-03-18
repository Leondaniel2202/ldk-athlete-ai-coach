"""Shared test fixtures and environment setup."""

import os

# Ensure required settings are present during test collection so that modules
# importing get_settings() at the module level do not fail with a
# ValidationError when the environment is otherwise empty.
# These values are only placeholders; they are never used to make real API
# calls or database connections inside unit tests.
_TEST_ENV_DEFAULTS: dict[str, str] = {
    # Notion integration
    "NOTION_API_KEY": "secret_test_key",
    "NOTION_PHASE_DB_ID": "test-phase-db-id",
    "NOTION_WORKOUT_DB_ID": "test-workout-db-id",
    "NOTION_SESSION_DB_ID": "test-session-db-id",
    "NOTION_FEEDBACK_DB_ID": "test-feedback-db-id",
    # Database (required by db/session.py at import time)
    "POSTGRES_DB": "test_db",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_HOST": "localhost",
}

for _key, _value in _TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)
