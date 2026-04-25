"""Regression tests for import-time database configuration behavior."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_SETTINGS_ENV_KEYS = {
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "NOTION_API_KEY",
    "NOTION_PLAN_DATA_SOURCE_ID",
    "NOTION_PHASE_DATA_SOURCE_ID",
    "NOTION_NUTRITION_GUIDELINE_DATA_SOURCE_ID",
    "NOTION_WORKOUT_DATA_SOURCE_ID",
    "NOTION_EVENT_DATA_SOURCE_ID",
    "NOTION_SESSION_DATA_SOURCE_ID",
    "NOTION_FEEDBACK_DATA_SOURCE_ID",
}


def _run_in_clean_process(tmp_path: Path, code: str) -> subprocess.CompletedProcess[str]:
    """Run Python in a clean subprocess without the app settings environment."""
    env = os.environ.copy()
    for key in _SETTINGS_ENV_KEYS:
        env.pop(key, None)

    src_path = Path(__file__).resolve().parents[3] / "src"
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(src_path)
    )

    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_importing_db_base_does_not_require_settings(tmp_path: Path) -> None:
    result = _run_in_clean_process(
        tmp_path,
        "from ldk_athlete_ai_coach.db.base import Base; print(Base.__name__)",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Base"


def test_importing_db_session_module_does_not_initialize_settings(tmp_path: Path) -> None:
    result = _run_in_clean_process(
        tmp_path,
        "from ldk_athlete_ai_coach.db.session import get_db_session; "
        "print(callable(get_db_session))",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "True"
