"""backfill existing project_members to accepted

Revision ID: 0021_project_member_backfill
Revises: 0020_auth_tokens
Create Date: 2026-08-13

Data-only migration -- no ALTER TABLE. The project_members.status /
invited_by_id / responded_at columns already physically exist in this
shared DB (confirmed via diagnostic before this feature was built, same
story as auth_tokens). Every row inserted by this project's code up to
this point was inserted without ever setting status, so it silently took
on the column's DB default of 'pending' -- including every existing
project lead. Left as-is, the new invite/accept gate being added in this
same feature would make every existing project (including ones people
are actively using) vanish from their own project list until they
"accept" a membership they were never actually invited to.

Per explicit user approval, backfill every existing pending row (lead
and regular member alike) to accepted, with responded_at set to their
original joined_at. Only rows already sitting at the DB default are
touched -- a genuine pending invite created after this feature ships
(via the new /projects/{id}/members endpoint) will never match, since by
then the app itself is setting status explicitly.
"""
from alembic import op

revision = "0021_project_member_backfill"
down_revision = "0020_auth_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE project_members
        SET status = 'accepted', responded_at = joined_at
        WHERE status = 'pending'
        """
    )


def downgrade() -> None:
    # Not reversible in a meaningful way -- we can't distinguish which
    # rows were backfilled here from ones that were already genuinely
    # accepted before this migration ran. No-op.
    pass
