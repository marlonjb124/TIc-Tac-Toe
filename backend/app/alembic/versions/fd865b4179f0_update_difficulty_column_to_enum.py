"""update_difficulty_column_to_enum

Revision ID: fd865b4179f0
Revises: ba52a6fe9545
Create Date: 2025-11-09 16:08:58.870754

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "fd865b4179f0"
down_revision = "ba52a6fe9545"
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Update any NULL or invalid values to 'MEDIUM'
    op.execute(
        """
        UPDATE game
        SET difficulty = 'MEDIUM'
        WHERE difficulty NOT IN ('EASY', 'MEDIUM', 'HARD')
        OR difficulty IS NULL
        """
    )

    # Step 2: Modify column to ENUM type with MariaDB syntax
    op.execute(
        """
        ALTER TABLE game
        MODIFY COLUMN difficulty ENUM('EASY', 'MEDIUM', 'HARD')
        NOT NULL DEFAULT 'MEDIUM'
        """
    )


def downgrade():
    # Revert ENUM back to VARCHAR
    op.execute(
        """
        ALTER TABLE game
        MODIFY COLUMN difficulty VARCHAR(50) DEFAULT 'MEDIUM'
        """
    )
