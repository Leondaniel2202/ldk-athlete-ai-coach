"""Notion sync service.

This module orchestrates the full sync flow for the supported Notion data
sources. It connects the existing client, extractors, and mappers into a single
coordinated service that fetches data from Notion, extracts it into validated
Pydantic models, and hands those extracted batches off to the persistence
boundary.

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

from sqlalchemy.orm import Session

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
from ldk_athlete_ai_coach.db.models.training import TrainingEntityMixin
from ldk_athlete_ai_coach.db.session import SessionLocal

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sync defintion
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SyncDefinition[TSchema: NotionBaseSchema, TEntity: TrainingEntityMixin]:
    """Static wiring needed to sync one Notion-backed entity type."""

    entity_name: str
    data_source_id: str
    extractor: Callable[[dict[str, Any]], TSchema]
    persister: Callable[[NotionPersistenceService, list[TSchema]], list[TEntity]]


# ---------------------------------------------------------------------------
# Sync result
# ---------------------------------------------------------------------------


@dataclass
class SyncResult:
    """Summary of a single entity sync run.

    Attributes:
        entity: Human-readable name of the synced entity (e.g. ``"Phase"``).
        fetched: Total number of raw pages retrieved from Notion.
        success: Number of pages successfully extracted and committed.
        failed: Number of pages that raised an error during extraction or persistence.
        entities: Persisted SQLAlchemy entity instances committed for this sync.
    """

    entity: str
    fetched: int = 0
    success: int = 0
    failed: int = 0
    entities: list[TrainingEntityMixin] = field(default_factory=list)

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

    1. Fetches raw pages from the Notion data source via :class:`NotionClient`.
    2. Extracts each raw page into a validated Pydantic schema using the
        corresponding extractor.
    3. Persists the extracted batch inside a single transaction for that entity.
    4. Returns a :class:`SyncResult` describing the committed outcome.

    Foreign-key resolution and entity mapping are intentionally handled by the
    persistence layer so the sync service stays focused on fetch/extract/commit
    orchestration.

    Args:
        client: Authenticated :class:`NotionClient` instance.
        settings: Application settings providing the Notion data source IDs.
    """

    def __init__(
        self,
        client: NotionClient,
        settings: Settings,
        session_factory: Callable[[], Session] = SessionLocal,
    ) -> None:
        self._client = client
        self._settings = settings
        self._session_factory = session_factory
        self._definitions = self._build_definitions()

    def _build_definitions(self) -> dict[str, SyncDefinition]:
        """Build the sync definitions for all supported entities.

        Returns:
            Dictionary mapping sync keys to their configured definitions.
        """
        return {
            "phase": SyncDefinition(
                entity_name="Phase",
                data_source_id=self._settings.notion_phase_data_source_id,
                extractor=extract_phase,
                persister=lambda persistence, schemas: persistence.persist_phases(schemas),
            ),
            "workout": SyncDefinition(
                entity_name="Workout",
                data_source_id=self._settings.notion_workout_data_source_id,
                extractor=extract_workout,
                persister=lambda persistence, schemas: persistence.persist_workouts(schemas),
            ),
            "session": SyncDefinition(
                entity_name="TrackedSession",
                data_source_id=self._settings.notion_session_data_source_id,
                extractor=extract_session,
                persister=lambda persistence, schemas: persistence.persist_sessions(schemas),
            ),
            "feedback": SyncDefinition(
                entity_name="Feedback",
                data_source_id=self._settings.notion_feedback_data_source_id,
                extractor=extract_weekly_feedback,
                persister=lambda persistence, schemas: persistence.persist_feedback(schemas),
            ),
        }

    def _sync_entity[TSchema: NotionBaseSchema, TEntity: TrainingEntityMixin](
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
        schemas: list[TSchema] = []
        logger.info(
            "Starting sync for entity=%s data_source_id=%s",
            definition.entity_name,
            definition.data_source_id,
        )
        for raw_page in self._client.iter_data_source_entries(definition.data_source_id):
            result.fetched += 1
            try:
                schemas.append(definition.extractor(raw_page))
            except (NotionExtractionError, Exception) as exc:
                result.failed += 1
                logger.error(
                    "Failed to extract %s page notion_id=%s: %s",
                    definition.entity_name,
                    raw_page.get("id", "<unknown>"),
                    exc,
                )

        if not schemas:
            logger.info(
                "Sync completed for entity=%s fetched=%d success=%d failed=%d",
                definition.entity_name,
                result.fetched,
                result.success,
                result.failed,
            )
            return result

        session = self._session_factory()
        try:
            persistence = NotionPersistenceService(session)
            entities = definition.persister(persistence, schemas)
            session.commit()
            result.entities.extend(entities)
            result.success += len(entities)
        except Exception as exc:
            session.rollback()
            result.failed += len(schemas)
            logger.error(
                "Failed to persist %s batch size=%d: %s",
                definition.entity_name,
                len(schemas),
                exc,
            )
        finally:
            session.close()

        logger.info(
            "Sync completed for entity=%s fetched=%d success=%d failed=%d",
            definition.entity_name,
            result.fetched,
            result.success,
            result.failed,
        )
        return result

    def sync_phases(self) -> SyncResult:
        """Fetch, extract, and persist all Phase entries from Notion.

        Returns:
            :class:`SyncResult` for the Phase entity containing all persisted
            :class:`~ldk_athlete_ai_coach.db.models.training.Phase` instances.
        """
        definition = self._definitions["phase"]
        result = self._sync_entity(definition)

        return result

    def sync_workouts(self) -> SyncResult:
        """Fetch, extract, and persist all Workout entries from Notion.

        Returns:
            :class:`SyncResult` for the Workout entity containing all persisted
            :class:`~ldk_athlete_ai_coach.db.models.training.Workout` instances.
        """
        definition = self._definitions["workout"]
        result = self._sync_entity(definition)

        return result

    def sync_sessions(self) -> SyncResult:
        """Fetch, extract, and persist all Tracked Session entries from Notion.

        Returns:
            :class:`SyncResult` for the TrackedSession entity containing all
            persisted :class:`~ldk_athlete_ai_coach.db.models.training.TrackedSession`
            instances.
        """
        definition = self._definitions["session"]
        result = self._sync_entity(definition)

        return result

    def sync_weekly_feedback(self) -> SyncResult:
        """Fetch, extract, and persist all Weekly Feedback entries from Notion.

        Returns:
            :class:`SyncResult` for the Feedback entity containing all persisted
            :class:`~ldk_athlete_ai_coach.db.models.training.Feedback` instances.
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
        1. **Phase** - no upstream Notion dependencies within scope.
        2. **Workout** - depends on Phase.
        3. **TrackedSession** - depends on Workout.
        4. **Feedback** - depends on Phase.

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
