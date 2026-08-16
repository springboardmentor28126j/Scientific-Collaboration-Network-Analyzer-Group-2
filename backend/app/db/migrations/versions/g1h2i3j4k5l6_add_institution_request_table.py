from alembic import op
import sqlalchemy as sa


revision = 'g1h2i3j4k5l6'
down_revision = 'b8c9d0e1f2a3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'institution_request',
        sa.Column('request_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('institution_name', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('official_email', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('requested_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['requested_by_user_id'], ['user.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('request_id')
    )


def downgrade():
    op.drop_table('institution_request')
