"""

Revision ID: 2f7c5d8aa1b1
Revises: e5b74b002400
Create Date: 2026-04-11 20:45:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2f7c5d8aa1b1"
down_revision = "e5b74b002400"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("plans", sa.Column("notion_page_content", sa.Text(), nullable=True))
    op.add_column("nutrition_guidelines", sa.Column("notion_page_content", sa.Text(), nullable=True))
    op.add_column("phases", sa.Column("notion_page_content", sa.Text(), nullable=True))
    op.add_column("workouts", sa.Column("notion_page_content", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("notion_page_content", sa.Text(), nullable=True))
    op.add_column("tracked_sessions", sa.Column("notion_page_content", sa.Text(), nullable=True))
    op.add_column("feedback", sa.Column("notion_page_content", sa.Text(), nullable=True))

    op.add_column("workouts", sa.Column("planned_training_load", sa.Float(), nullable=True))
    op.add_column("workouts", sa.Column("actual_duration_min", sa.Float(), nullable=True))
    op.add_column("workouts", sa.Column("actual_distance_km", sa.Float(), nullable=True))
    op.add_column("workouts", sa.Column("actual_training_load", sa.Float(), nullable=True))
    op.add_column("workouts", sa.Column("actual_calories_burned_kcal", sa.Float(), nullable=True))
    op.add_column("workouts", sa.Column("weighted_hrr_intensity_sum", sa.Float(), nullable=True))
    op.add_column("workouts", sa.Column("actual_hrr_intensity", sa.Float(), nullable=True))
    op.add_column("workouts", sa.Column("done_date_start", sa.DateTime(timezone=True), nullable=True))
    op.add_column("workouts", sa.Column("done_date_end", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "workouts",
        sa.Column(
            "done_date_is_datetime",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column("workouts", sa.Column("status", sa.String(length=64), nullable=True))
    op.add_column("workouts", sa.Column("training_load_method", sa.String(length=64), nullable=True))
    op.alter_column("workouts", "done_date_is_datetime", server_default=None)


def downgrade() -> None:
    op.drop_column("workouts", "training_load_method")
    op.drop_column("workouts", "status")
    op.drop_column("workouts", "done_date_is_datetime")
    op.drop_column("workouts", "done_date_end")
    op.drop_column("workouts", "done_date_start")
    op.drop_column("workouts", "actual_hrr_intensity")
    op.drop_column("workouts", "weighted_hrr_intensity_sum")
    op.drop_column("workouts", "actual_calories_burned_kcal")
    op.drop_column("workouts", "actual_training_load")
    op.drop_column("workouts", "actual_distance_km")
    op.drop_column("workouts", "actual_duration_min")
    op.drop_column("workouts", "planned_training_load")

    op.drop_column("feedback", "notion_page_content")
    op.drop_column("tracked_sessions", "notion_page_content")
    op.drop_column("events", "notion_page_content")
    op.drop_column("workouts", "notion_page_content")
    op.drop_column("phases", "notion_page_content")
    op.drop_column("nutrition_guidelines", "notion_page_content")
    op.drop_column("plans", "notion_page_content")
