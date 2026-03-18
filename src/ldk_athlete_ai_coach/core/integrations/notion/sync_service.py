"""Notion sync service.

This module orchestrates the full sync flow for the supported Notion databases.
It connects the existing client, extractors, and mappers into a single
coordinated service that fetches data from Notion, extracts it into validated
Pydantic models, maps those models to SQLAlchemy entities, and hands the
entities off to the persistence boundary.

Typical usage::

    from ldk_athlete_ai_coach.core.config import get_settings
    from ldk_athlete_ai_coach.core.integrations.notion.client import NotionClient
    from ldk_athlete_ai_coach.core.integrations.notion.sync_service import NotionSyncService

    client = NotionClient(get_settings())
    service = NotionSyncService(client, get_settings())
    results = service.sync_all()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ldk_athlete_ai_coach.core.config import Settings
from ldk_athlete_ai_coach.core.integrations.notion.client import NotionClient
from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors.phase_extractor import extract_phase
from ldk_athlete_ai_coach.core.integrations.notion.extractors.session_extractor import (
    extract_session,
)
from ldk_athlete_ai_coach.core.integrations.notion.extractors.weekly_feedback_extractor import (
    extract_weekly_feedback,
)
from ldk_athlete_ai_coach.core.integrations.notion.extractors.workout_extractor import (
    extract_workout,
)
from ldk_athlete_ai_coach.core.integrations.notion.mappers.feedback import map_feedback
from ldk_athlete_ai_coach.core.integrations.notion.mappers.phase import map_phase
from ldk_athlete_ai_coach.core.integrations.notion.mappers.session import map_session
from ldk_athlete_ai_coach.core.integrations.notion.mappers.workout import map_workout
from ldk_athlete_ai_coach.db.models.sport_manager import Feedback, Phase, TrackedSession, Workout

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sync result
# ---------------------------------------------------------------------------


@dataclass
class SyncResult:
    """Summary of a single entity sync run.

    Attributes:
        entity: Human-readable name of the synced entity (e.g. ``"Phase"``).
        fetched: Total number of raw pages retrieved from Notion.
        success: Number of pages successfully extracted and mapped.
        failed: Number of pages that raised an error during extraction or mapping.
        entities: Mapped SQLAlchemy entity instances ready for persistence.
    """

    entity: str
    fetched: int = 0
    success: int = 0
    failed: int = 0
    entities: list[object] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SyncResult(entity={self.entity!r}, fetched={self.fetched}, "
            f"success={self.success}, failed={self.failed})"
        )


# ---------------------------------------------------------------------------
# Sync service
# ---------------------------------------------------------------------------


class NotionSyncService:
    """Orchestrates the Notion sync flow for all supported entities.

    For each entity the service:

    1. Fetches raw pages from the Notion database via :class:`NotionClient`.
    2. Extracts each raw page into a validated Pydantic schema using the
       corresponding extractor.
    3. Maps the validated schema to a SQLAlchemy entity using the corresponding
       mapper.
    4. Collects the mapped entities into a :class:`SyncResult` for the
       persistence boundary to consume.

    Foreign-key resolution (mapping Notion page IDs to local DB primary keys) is
    intentionally left to the persistence layer; entities are handed off with
    ``*_id`` fields set to ``None`` unless a resolution strategy is wired in
    externally.

    Args:
        client: Authenticated :class:`NotionClient` instance.
        settings: Application settings providing the Notion database IDs.
    """

    def __init__(self, client: NotionClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    # ------------------------------------------------------------------
    # Per-entity sync methods
    # ------------------------------------------------------------------

    def sync_phases(self) -> SyncResult:
        """Fetch, extract, and map all Phase entries from Notion.

        Returns:
            :class:`SyncResult` for the Phase entity containing all mapped
            :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Phase` instances.
        """
        result = SyncResult(entity="Phase")
        db_id = self._settings.notion_phase_db_id
        logger.info("Starting sync for entity=Phase database_id=%s", db_id)

        for raw_page in self._client.iter_database_entries(db_id):
            result.fetched += 1
            try:
                schema = extract_phase(raw_page)
                entity: Phase = map_phase(schema)
                result.entities.append(entity)
                result.success += 1
            except (NotionExtractionError, Exception) as exc:
                result.failed += 1
                logger.error(
                    "Failed to process Phase page notion_id=%s: %s",
                    raw_page.get("id", "<unknown>"),
                    exc,
                )

        logger.info(
            "Sync completed for entity=Phase fetched=%d success=%d failed=%d",
            result.fetched,
            result.success,
            result.failed,
        )
        return result

    def sync_workouts(self) -> SyncResult:
        """Fetch, extract, and map all Workout entries from Notion.

        Returns:
            :class:`SyncResult` for the Workout entity containing all mapped
            :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Workout` instances.
        """
        result = SyncResult(entity="Workout")
        db_id = self._settings.notion_workout_db_id
        logger.info("Starting sync for entity=Workout database_id=%s", db_id)

        for raw_page in self._client.iter_database_entries(db_id):
            result.fetched += 1
            try:
                schema = extract_workout(raw_page)
                entity: Workout = map_workout(schema)
                result.entities.append(entity)
                result.success += 1
            except (NotionExtractionError, Exception) as exc:
                result.failed += 1
                logger.error(
                    "Failed to process Workout page notion_id=%s: %s",
                    raw_page.get("id", "<unknown>"),
                    exc,
                )

        logger.info(
            "Sync completed for entity=Workout fetched=%d success=%d failed=%d",
            result.fetched,
            result.success,
            result.failed,
        )
        return result

    def sync_sessions(self) -> SyncResult:
        """Fetch, extract, and map all Tracked Session entries from Notion.

        Returns:
            :class:`SyncResult` for the TrackedSession entity containing all
            mapped :class:`~ldk_athlete_ai_coach.db.models.sport_manager.TrackedSession`
            instances.
        """
        result = SyncResult(entity="TrackedSession")
        db_id = self._settings.notion_session_db_id
        logger.info("Starting sync for entity=TrackedSession database_id=%s", db_id)

        for raw_page in self._client.iter_database_entries(db_id):
            result.fetched += 1
            try:
                schema = extract_session(raw_page)
                entity: TrackedSession = map_session(schema)
                result.entities.append(entity)
                result.success += 1
            except (NotionExtractionError, Exception) as exc:
                result.failed += 1
                logger.error(
                    "Failed to process TrackedSession page notion_id=%s: %s",
                    raw_page.get("id", "<unknown>"),
                    exc,
                )

        logger.info(
            "Sync completed for entity=TrackedSession fetched=%d success=%d failed=%d",
            result.fetched,
            result.success,
            result.failed,
        )
        return result

    def sync_weekly_feedback(self) -> SyncResult:
        """Fetch, extract, and map all Weekly Feedback entries from Notion.

        Returns:
            :class:`SyncResult` for the Feedback entity containing all mapped
            :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Feedback` instances.
        """
        result = SyncResult(entity="Feedback")
        db_id = self._settings.notion_feedback_db_id
        logger.info("Starting sync for entity=Feedback database_id=%s", db_id)

        for raw_page in self._client.iter_database_entries(db_id):
            result.fetched += 1
            try:
                schema = extract_weekly_feedback(raw_page)
                entity: Feedback = map_feedback(schema)
                result.entities.append(entity)
                result.success += 1
            except (NotionExtractionError, Exception) as exc:
                result.failed += 1
                logger.error(
                    "Failed to process Feedback page notion_id=%s: %s",
                    raw_page.get("id", "<unknown>"),
                    exc,
                )

        logger.info(
            "Sync completed for entity=Feedback fetched=%d success=%d failed=%d",
            result.fetched,
            result.success,
            result.failed,
        )
        return result

    # ------------------------------------------------------------------
    # Aggregate sync
    # ------------------------------------------------------------------

    def sync_all(self) -> list[SyncResult]:
        """Run a full sync across all supported entities in dependency order.

        Sync order:
        1. **Phase** – no upstream Notion dependencies within scope.
        2. **Workout** – depends on Phase.
        3. **TrackedSession** – depends on Workout.
        4. **Feedback** – depends on Phase.

        Returns:
            A list of :class:`SyncResult` instances, one per entity, in sync order.
        """
        logger.info("Starting full Notion sync")
        results = [
            self.sync_phases(),
            self.sync_workouts(),
            self.sync_sessions(),
            self.sync_weekly_feedback(),
        ]
        total_fetched = sum(r.fetched for r in results)
        total_success = sum(r.success for r in results)
        total_failed = sum(r.failed for r in results)
        logger.info(
            "Full Notion sync completed total_fetched=%d total_success=%d total_failed=%d",
            total_fetched,
            total_success,
            total_failed,
        )
        return results
