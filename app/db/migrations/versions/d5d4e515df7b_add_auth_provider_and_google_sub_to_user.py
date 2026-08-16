"""add auth_provider and google_sub to user

Revision ID: d5d4e515df7b
Revises: a09b62865a06
Create Date: 2026-07-12 18:44:30.258965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd5d4e515df7b'
down_revision: Union[str, None] = 'a09b62865a06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- institution.email_domain ---
    op.add_column('institution', sa.Column('email_domain', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_institution_email_domain'), 'institution', ['email_domain'], unique=True)

    # --- user.auth_provider (create Postgres ENUM type first, then the column) ---
    auth_provider_enum = postgresql.ENUM('LOCAL', 'GOOGLE', name='authprovider')
    auth_provider_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'user',
        sa.Column('auth_provider', auth_provider_enum, nullable=False, server_default='LOCAL'),
    )

    # --- user.google_sub ---
    op.add_column('user', sa.Column('google_sub', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_user_google_sub'), 'user', ['google_sub'], unique=True)

    # --- user.is_email_verified (new column, needed for mandatory verification feature) ---
    op.add_column(
        'user',
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'),
    )

    # --- user.password_hash: allow NULL for Google-only accounts ---
    op.alter_column('user', 'password_hash', existing_type=sa.String(length=255), nullable=True)


def downgrade() -> None:
    op.alter_column('user', 'password_hash', existing_type=sa.String(length=255), nullable=False)
    op.drop_column('user', 'is_email_verified')
    op.drop_index(op.f('ix_user_google_sub'), table_name='user')
    op.drop_column('user', 'google_sub')
    op.drop_column('user', 'auth_provider')

    auth_provider_enum = postgresql.ENUM('LOCAL', 'GOOGLE', name='authprovider')
    auth_provider_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index(op.f('ix_institution_email_domain'), table_name='institution')
    op.drop_column('institution', 'email_domain')