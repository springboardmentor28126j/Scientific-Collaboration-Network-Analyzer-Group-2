"""reconcile projects/project_members/audit_logs schema drift

This DB was previously migrated by a different, longer chain (almost
certainly the teammate's reference copy in 2807Infosys_Internship.zip --
see the "Import Milestone 3+ features from zip" plan) that got stamped up
through a revision named '0018_auth_audit' which does not exist in this
repo's alembic/versions/. That other chain's design for the same two
tables diverged from what 0015_projects / 0016_audit_log actually created
here:

  - audit_logs.actor_user_id   vs this repo's model column: user_id
  - projects: missing funding_source, budget entirely
  - projects.status native enum labels
        (planned, ongoing, completed, cancelled)
    vs this repo's ProjectStatus enum
        (planning, active, on_hold, completed)
  - project_members.role native enum labels (lead, member)
    vs this repo's ProjectRole enum (lead, co_investigator, member),
    stored in a column named role_in_project

This migration reconciles the *existing* tables/rows to match this
repo's models -- it does not recreate anything, so all existing rows
(5 projects, 5 project_members, 7 audit_logs at the time this was
written) are preserved with their data remapped, not dropped.

project_members.status / invited_by_id / responded_at (an invite/accept
workflow the current app doesn't implement) are deliberately left in
place, untouched. They're unused by the current models/routes, so
their NOT NULL + server_default columns are invisible to the app --
harmless to keep, and available if that workflow gets built out later.

Revision ID: 0017_reconcile_drift
Revises: 0016_audit_log
Create Date: 2026-08-06

"""
from alembic import op
import sqlalchemy as sa

revision = "0017_reconcile_drift"
down_revision = "0016_audit_log"
branch_labels = None
depends_on = None

# Old DB vocabulary -> this repo's ProjectStatus vocabulary.
# 'cancelled' has no direct equivalent in ProjectStatus; 'on_hold' is the
# closest available meaning (a project that isn't actively moving).
PROJECT_STATUS_MAP = {
    "planned": "planning",
    "ongoing": "active",
    "completed": "completed",
    "cancelled": "on_hold",
}


def upgrade() -> None:
    # --- audit_logs: actor_user_id -> user_id ---------------------------
    op.alter_column("audit_logs", "actor_user_id", new_column_name="user_id")

    # --- projects: add the two columns that were missing entirely -------
    op.add_column(
        "projects", sa.Column("funding_source", sa.String(length=255), nullable=True)
    )
    op.add_column("projects", sa.Column("budget", sa.Numeric(14, 2), nullable=True))

    # --- projects.status: old native enum -> plain VARCHAR --------------
    # Drop the old enum-typed default first (its expression is cast to
    # the enum type we're about to abandon), convert the column itself,
    # remap every existing row's value, then set the new default.
    op.execute("ALTER TABLE projects ALTER COLUMN status DROP DEFAULT")
    op.execute(
        "ALTER TABLE projects ALTER COLUMN status TYPE VARCHAR(20) USING status::text"
    )
    conn = op.get_bind()
    for old_value, new_value in PROJECT_STATUS_MAP.items():
        conn.execute(
            sa.text("UPDATE projects SET status = :new WHERE status = :old"),
            {"new": new_value, "old": old_value},
        )
    op.execute("ALTER TABLE projects ALTER COLUMN status SET DEFAULT 'planning'")
    op.execute("DROP TYPE IF EXISTS projectstatus")

    # --- project_members: role -> role_in_project, old native enum ------
    # (lead/member) -> plain VARCHAR carrying this repo's 3-value
    # vocabulary (lead/co_investigator/member). Only 'lead' is present in
    # existing rows, and it's already a valid value in both vocabularies,
    # so no value remapping is needed here -- just rename + retype.
    op.alter_column("project_members", "role", new_column_name="role_in_project")
    op.execute("ALTER TABLE project_members ALTER COLUMN role_in_project DROP DEFAULT")
    op.execute(
        "ALTER TABLE project_members ALTER COLUMN role_in_project "
        "TYPE VARCHAR(20) USING role_in_project::text"
    )
    op.execute(
        "ALTER TABLE project_members ALTER COLUMN role_in_project SET DEFAULT 'member'"
    )
    op.execute("DROP TYPE IF EXISTS projectmemberrole")

    # NOTE: project_members.status still uses the projectmemberstatus
    # enum type -- intentionally left alone, see module docstring.


def downgrade() -> None:
    # This migration reconciles genuine data drift between two divergent
    # schema designs (this repo's vs. the teammate zip's). It is not
    # meaningfully reversible: e.g. a project currently 'on_hold' could
    # have originally been 'cancelled' OR could be a project that was
    # always meant to be 'on_hold' under this repo's own vocabulary --
    # there's no way to tell them apart after the fact. Restore from a
    # backup taken before this migration if you need to revert.
    raise NotImplementedError(
        "0017_reconcile_drift has no safe automatic downgrade -- restore "
        "from a pre-migration backup instead."
    )
