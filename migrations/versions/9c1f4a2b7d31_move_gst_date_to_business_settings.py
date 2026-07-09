"""Move gst_registration_date from financial_years to business_settings

GST registration is a one-time property of the business, not something that
restarts each financial year. Storing it per-year meant every new FY appeared
unregistered, silently disabling Input Tax Credits on that year's expenses.

The existing registration date is carried across: we take the EARLIEST
non-null date recorded on any financial year, which is the date the business
actually registered.

Revision ID: 9c1f4a2b7d31
Revises: bc60923cdefe
Create Date: 2026-07-09

"""
import sqlalchemy as sa
from alembic import op

revision = "9c1f4a2b7d31"
down_revision = "bc60923cdefe"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "business_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("gst_registration_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    bind = op.get_bind()

    # Carry the existing registration across. The earliest non-null date is the
    # real registration date; later years simply repeated it.
    existing = bind.execute(
        sa.text(
            "SELECT MIN(gst_registration_date) FROM financial_years "
            "WHERE gst_registration_date IS NOT NULL"
        )
    ).scalar()

    bind.execute(
        sa.text("INSERT INTO business_settings (id, gst_registration_date) VALUES (1, :d)"),
        {"d": existing},
    )

    # SQLite cannot DROP COLUMN directly; batch mode rebuilds the table for us.
    with op.batch_alter_table("financial_years", schema=None) as batch_op:
        batch_op.drop_column("gst_registration_date")


def downgrade():
    with op.batch_alter_table("financial_years", schema=None) as batch_op:
        batch_op.add_column(sa.Column("gst_registration_date", sa.Date(), nullable=True))

    bind = op.get_bind()

    # Put the date back on whichever financial year contains it, matching the
    # old per-year semantics as closely as possible.
    registration = bind.execute(
        sa.text("SELECT gst_registration_date FROM business_settings ORDER BY id LIMIT 1")
    ).scalar()

    if registration is not None:
        bind.execute(
            sa.text(
                "UPDATE financial_years SET gst_registration_date = :d "
                "WHERE :d BETWEEN start_date AND end_date"
            ),
            {"d": registration},
        )

    op.drop_table("business_settings")
