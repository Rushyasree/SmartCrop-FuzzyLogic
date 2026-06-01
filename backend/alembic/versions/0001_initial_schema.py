"""Initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-31 10:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    user_role = sa.Enum("FARMER", "ADMIN", "RESEARCHER", name="userrole")
    season = sa.Enum("KHARIF", "RABI", "SUMMER", "YEAR_ROUND", name="season")

    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        user_role.create(bind, checkfirst=True)
        season.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "farms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("size_hectares", sa.Float(), nullable=True),
        sa.Column("soil_type", sa.String(length=50), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farms_id"), "farms", ["id"], unique=False)
    op.create_index(op.f("ix_farms_user_id"), "farms", ["user_id"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("action_recommended", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_farm_id"), "alerts", ["farm_id"], unique=False)
    op.create_index(op.f("ix_alerts_id"), "alerts", ["id"], unique=False)

    op.create_table(
        "disease_detections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("crop", sa.String(length=100), nullable=False),
        sa.Column("disease_name", sa.String(length=255), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=True),
        sa.Column("affected_area_percent", sa.Float(), nullable=True),
        sa.Column("treatment_recommended", sa.Text(), nullable=True),
        sa.Column("treatment_cost", sa.Float(), nullable=True),
        sa.Column("image_path", sa.String(length=500), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False),
        sa.Column("confirmed_by", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["confirmed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_disease_detections_farm_id"), "disease_detections", ["farm_id"], unique=False)
    op.create_index(op.f("ix_disease_detections_id"), "disease_detections", ["id"], unique=False)

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("input_ph", sa.Float(), nullable=False),
        sa.Column("input_moisture", sa.Float(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("rainfall", sa.Float(), nullable=True),
        sa.Column("recommended_crop", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("alternative_crops", sa.Text(), nullable=True),
        sa.Column("season", season, nullable=True),
        sa.Column("rainfall_needed", sa.Float(), nullable=True),
        sa.Column("fertilizer_recommendation", sa.Text(), nullable=True),
        sa.Column("irrigation_schedule", sa.Text(), nullable=True),
        sa.Column("expected_yield", sa.Float(), nullable=True),
        sa.Column("market_price", sa.Float(), nullable=True),
        sa.Column("profitability_score", sa.Float(), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_predictions_farm_id"), "predictions", ["farm_id"], unique=False)
    op.create_index(op.f("ix_predictions_id"), "predictions", ["id"], unique=False)

    op.create_table(
        "soil_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("ph", sa.Float(), nullable=True),
        sa.Column("moisture", sa.Float(), nullable=True),
        sa.Column("nitrogen", sa.Float(), nullable=True),
        sa.Column("phosphorus", sa.Float(), nullable=True),
        sa.Column("potassium", sa.Float(), nullable=True),
        sa.Column("organic_matter", sa.Float(), nullable=True),
        sa.Column("ec", sa.Float(), nullable=True),
        sa.Column("measurement_date", sa.DateTime(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_soil_data_farm_id"), "soil_data", ["farm_id"], unique=False)
    op.create_index(op.f("ix_soil_data_id"), "soil_data", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_soil_data_id"), table_name="soil_data")
    op.drop_index(op.f("ix_soil_data_farm_id"), table_name="soil_data")
    op.drop_table("soil_data")
    op.drop_index(op.f("ix_predictions_id"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_farm_id"), table_name="predictions")
    op.drop_table("predictions")
    op.drop_index(op.f("ix_disease_detections_id"), table_name="disease_detections")
    op.drop_index(op.f("ix_disease_detections_farm_id"), table_name="disease_detections")
    op.drop_table("disease_detections")
    op.drop_index(op.f("ix_alerts_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_farm_id"), table_name="alerts")
    op.drop_table("alerts")
    op.drop_index(op.f("ix_farms_user_id"), table_name="farms")
    op.drop_index(op.f("ix_farms_id"), table_name="farms")
    op.drop_table("farms")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        sa.Enum(name="season").drop(bind, checkfirst=True)
        sa.Enum(name="userrole").drop(bind, checkfirst=True)
