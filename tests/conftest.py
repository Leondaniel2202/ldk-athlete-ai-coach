"""Shared test fixtures and environment setup."""

from __future__ import annotations

import os
import shutil
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest

# Ensure required settings are present during test collection so that modules
# importing get_settings() at the module level do not fail with a
# ValidationError when the environment is otherwise empty.
# These values are only placeholders; they are never used to make real API
# calls or database connections inside unit tests.
_TEST_ENV_DEFAULTS: dict[str, str] = {
    # Notion integration
    "NOTION_API_KEY": "secret_test_key",
    "NOTION_PLAN_DATA_SOURCE_ID": "test-plan-data-source-id",
    "NOTION_PHASE_DATA_SOURCE_ID": "test-phase-data-source-id",
    "NOTION_WORKOUT_DATA_SOURCE_ID": "test-workout-data-source-id",
    "NOTION_SESSION_DATA_SOURCE_ID": "test-session-data-source-id",
    "NOTION_FEEDBACK_DATA_SOURCE_ID": "test-feedback-data-source-id",
    # Database (required by db/session.py at import time)
    "POSTGRES_DB": "test_db",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_HOST": "localhost",
}

for _key, _value in _TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)


_TEST_TMP_ROOT = Path(__file__).resolve().parent.parent / "test_tmp"


@pytest.fixture()
def tmp_path() -> Generator[Path, None, None]:
    """Provide a workspace-local temporary directory.

    Pytest's built-in tmp_path fixture resolves through the system temp area,
    which is not writable in this sandbox. These tests only need an isolated
    writable directory, so a repo-local substitute is sufficient.
    """
    _TEST_TMP_ROOT.mkdir(exist_ok=True)
    path = _TEST_TMP_ROOT / f"tmp-{uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
