"""empty message

Revision ID: 87c7e53631be
Revises: a6214a0487e5
Create Date: 2024-04-10 16:28:59.144589

"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = "87c7e53631be"
down_revision = "a6214a0487e5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Add new columns as nullable first to avoid NOT NULL constraint issues
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(sa.Column("order_time", sa.Time(), nullable=True))
        batch_op.add_column(sa.Column("order_date", sa.Date(), nullable=True))

    # Assuming you want to set a default date/time for existing records
    # You'll need custom logic to convert order_time_pst to date and time
    default_date = datetime(2024, 1, 1).date()
    default_time = datetime.strptime("12:00:00", "%H:%M:%S").time()
    op.execute(
        """
        UPDATE orders
        SET order_date = '{}', order_time = '{}'
        """.format(
            default_date, default_time
        )
    )

    # Now change columns to NOT NULL after they have been populated
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.alter_column("order_time", nullable=False)
        batch_op.alter_column("order_date", nullable=False)

    # Drop the old column if no longer needed
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_column("order_time_pst")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(sa.Column("order_time_pst", sa.DATETIME(), nullable=True))
        batch_op.drop_column("order_date")
        batch_op.drop_column("order_time")

    # ### end Alembic commands ###
