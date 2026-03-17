"""Shared test fixtures and environment setup."""

import os

# Ensure required Notion settings are present during test collection so that
# modules importing get_settings() at the module level (e.g. test_health.py)
# do not fail with a ValidationError when the environment is otherwise empty.
# These values are only placeholders; they are never used to make real API
# calls inside unit tests.
_NOTION_DEFAULTS: dict[str, str] = {
    "NOTION_API_KEY": "secret_test_key",
    "NOTION_PHASE_DB_ID": "test-phase-db-id",
    "NOTION_WORKOUT_DB_ID": "test-workout-db-id",
    "NOTION_SESSION_DB_ID": "test-session-db-id",
    "NOTION_FEEDBACK_DB_ID": "test-feedback-db-id",
}

for _key, _value in _NOTION_DEFAULTS.items():
    os.environ.setdefault(_key, _value)
