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
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

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
from ldk_athlete_ai_coach.core.integrations.notion.persistence_service import (
    NotionPersistenceService,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_base import NotionBaseSchema
from ldk_athlete_ai_coach.db.models.sport_manager import NotionSyncMixin
from ldk_athlete_ai_coach.db.session import get_db_session

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sync defintion
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SyncDefinition[TSchema: NotionBaseSchema, TEntity: NotionSyncMixin]:
    """Static wiring needed to sync one Notion-backed entity type."""

    entity_name: str
    database_id: str
    extractor: Callable[[dict[str, Any]], TSchema]
    persister: Callable[[TSchema], TEntity]


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
    entities: list[NotionSyncMixin] = field(default_factory=list)

    @property
    def entity_name(self) -> str:
        """Backward-compatible alias for the synced entity name."""
        return self.entity

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
        self._session = next(get_db_session())
        self._persistence = NotionPersistenceService(self._session)
        self._definitions = self._build_definitions()

    def _build_definitions(self) -> dict[str, SyncDefinition]:
        """Build the sync definitions for all supported entities.

        Returns:
            Dictionary mapping sync keys to their configured definitions.
        """
        return {
            "phase": SyncDefinition(
                entity_name="Phase",
                database_id=self._settings.notion_phase_db_id,
                extractor=extract_phase,
                persister=lambda schema: self._persistence.persist_phases([schema])[0],
            ),
            "workout": SyncDefinition(
                entity_name="Workout",
                database_id=self._settings.notion_workout_db_id,
                extractor=extract_workout,
                persister=lambda schema: self._persistence.persist_workouts([schema])[0],
            ),
            "session": SyncDefinition(
                entity_name="TrackedSession",
                database_id=self._settings.notion_session_db_id,
                extractor=extract_session,
                persister=lambda schema: self._persistence.persist_sessions([schema])[0],
            ),
            "feedback": SyncDefinition(
                entity_name="Feedback",
                database_id=self._settings.notion_feedback_db_id,
                extractor=extract_weekly_feedback,
                persister=lambda schema: self._persistence.persist_feedback([schema])[0],
            ),
        }

    def _sync_entity[TSchema: NotionBaseSchema, TEntity: NotionSyncMixin](
        self,
        definition: SyncDefinition[TSchema, TEntity],
    ) -> SyncResult:
        """Private helper method to sync a single entity.

        Args:
            definition: The sync definition for the entity.

        Returns:
            The result of the sync operation.
        """
        result = SyncResult(entity=definition.entity_name)
        logger.info(
            "Starting sync for entity=%s database_id=%s",
            definition.entity_name,
            definition.database_id,
        )
        for raw_page in self._client.iter_database_entries(definition.database_id):
            result.fetched += 1
            try:
                schema = definition.extractor(raw_page)
                entity = definition.persister(schema)
                result.entities.append(entity)
                result.success += 1
            except (NotionExtractionError, Exception) as exc:
                result.failed += 1
                logger.error(
                    "Failed to process %s page notion_id=%s: %s",
                    definition.entity_name,
                    raw_page.get("id", "<unknown>"),
                    exc,
                )

        logger.info(
            "Sync completed for entity=%s fetched=%d success=%d failed=%d",
            definition.entity_name,
            result.fetched,
            result.success,
            result.failed,
        )
        return result

    def sync_phases(self) -> SyncResult:
        """Fetch, extract, and map all Phase entries from Notion.

        Returns:
            :class:`SyncResult` for the Phase entity containing all mapped
            :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Phase` instances.
        """
        definition = self._definitions["phase"]
        result = self._sync_entity(definition)

        return result

    def sync_workouts(self) -> SyncResult:
        """Fetch, extract, and map all Workout entries from Notion.

        Returns:
            :class:`SyncResult` for the Workout entity containing all mapped
            :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Workout` instances.
        """
        definition = self._definitions["workout"]
        result = self._sync_entity(definition)

        return result

    def sync_sessions(self) -> SyncResult:
        """Fetch, extract, and map all Tracked Session entries from Notion.

        Returns:
            :class:`SyncResult` for the TrackedSession entity containing all
            mapped :class:`~ldk_athlete_ai_coach.db.models.sport_manager.TrackedSession`
            instances.
        """
        definition = self._definitions["session"]
        result = self._sync_entity(definition)

        return result

    def sync_weekly_feedback(self) -> SyncResult:
        """Fetch, extract, and map all Weekly Feedback entries from Notion.

        Returns:
            :class:`SyncResult` for the Feedback entity containing all mapped
            :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Feedback` instances.
        """
        definition = self._definitions["feedback"]
        result = self._sync_entity(definition)

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
