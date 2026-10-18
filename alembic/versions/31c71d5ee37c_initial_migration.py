"""Initial migration

Revision ID: 31c71d5ee37c
Revises: 
Create Date: 2026-10-18 18:45:46.700258

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "31c71d5ee37c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bikes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="Available"
        ),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("part_name", sa.String(length=100), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("threshold", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("part_name"),
    )
    op.create_table(
        "work_orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bike_id", sa.Integer(), nullable=False),
        sa.Column("issue_type", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="Open"
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["bike_id"],
            ["bikes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("work_orders")
    op.drop_table("inventory")
    op.drop_table("bikes")
