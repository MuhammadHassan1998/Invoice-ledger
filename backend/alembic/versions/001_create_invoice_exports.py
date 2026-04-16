"""create invoice_exports table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2024-09-01 10:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "invoice_exports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.String(), nullable=False),
        sa.Column("invoice_number", sa.String(), nullable=False),
        sa.Column("exported_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoice_exports_invoice_id", "invoice_exports", ["invoice_id"])


def downgrade() -> None:
    op.drop_index("ix_invoice_exports_invoice_id", table_name="invoice_exports")
    op.drop_table("invoice_exports")
