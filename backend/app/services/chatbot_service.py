"""
AI chatbot for the platform. Two jobs, both handled by one Claude
conversation with tools:

1. FAQ / navigation help -- answered straight from the system prompt below,
   no tool call needed.
2. Live platform data ("what are my publications", "do I have any reviews
   due") -- answered by calling one of the read-only tools in this file,
   which reuse the exact same repository functions the Reports feature is
   built on, so the numbers always match what the person would see on
   their own Reports pages.

Every tool is scoped to the CURRENT user and enforces the same role
boundaries as the rest of the app (see reports.py's ALLOWED_REPORTS, which
this mirrors) -- the model never gets a tool that could read someone else's
personal data, and a researcher's tool set is intentionally smaller than a
system_admin's.
"""
import datetime
import logging

import anthropic
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.institution import Institution
from app.models.researcher import ResearcherProfile
from app.models.user import User, UserRole
from app.repositories import report_repository as repo

logger = logging.getLogger(__name__)

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


class ChatbotUnavailable(Exception):
    """Raised when the chatbot can't be reached right now (no API key
    configured, or the Anthropic API itself failed) -- callers turn this
    into a clean 503 rather than a raw stack trace."""


# --- Site knowledge (FAQ + navigation map) --------------------------------
# Kept as plain text baked into the system prompt rather than a tool, since
# it never changes per-request and doesn't need a round trip to compute.

_SITE_MAP = """
Key pages on this platform (site is the Scientific Collaboration Network
Analyzer, "SCNA"):
- /dashboard -- role-specific home page with recent activity and metrics.
- /profile -- edit your own name, bio, skills, research interests, and
  (for researchers) request/change your institution affiliation.
- /publications -- browse publications; /publications/new to submit one;
  each publication has an edit page, a file upload/download, and (for
  reviewers/admins) a status-setting action.
- /projects -- browse projects; /projects/new to start one; project pages
  let you add/remove members and post project messages.
- /conferences -- browse conferences; /conferences/new to create one;
  register for a conference from its detail page.
- /collaborations -- your collaboration network, connection requests
  (/collaborations/requests), suggested collaborators
  (/collaborations/suggested), and a collaboration timeline.
- /researchers -- directory of researchers on the platform.
- /institutions -- directory of institutions; institution_admin/system_admin
  can create, edit, and manage departments here.
- /notifications -- your notifications; mark one or all as read.
- /reports -- analytics: Researcher, Publications, Projects, Conferences,
  Collaborations, Reviews, Institution, and System reports. Which of these
  a person can see depends on their role (see below) -- system_admin can
  see all of them. Each report has Export to Excel/PDF buttons.
- /reviewer/reviews -- a reviewer's assigned reviews, with accept/decline
  and submit actions.
- /institution-admin/researchers -- institution_admin approves or rejects
  researchers requesting to join their institution.
- /admin -- system_admin only: manage users, approve/reject institution
  creation requests, view audit logs, edit platform settings.

Roles and what they can generally do:
- researcher: manage their own profile/publications/projects, join
  conferences, build their collaboration network, see Researcher/
  Publications/Projects/Conferences/Collaborations reports.
- reviewer: everything a researcher can plus review assignments; sees
  Researcher and Reviews reports (their own review activity).
- institution_admin: manages their institution's researchers/publications/
  projects/conferences; sees the Institution report (their institution
  only) plus Publications/Projects/Conferences reports.
- system_admin: manages all users, institutions, and platform settings;
  can see every report type, including the System report and,
  for the Institution report, can pick *any* institution to inspect
  (they aren't tied to one themselves) and, for Reviews, sees a
  system-wide view across every reviewer instead of a personal one.

Common how-tos:
- "How do I submit a publication?" -> Go to /publications/new, fill in the
  details, and optionally upload the file afterward from the publication's
  detail page.
- "How do I join an institution?" -> On /profile, use the institution
  section to request affiliation; an institution_admin (or system_admin)
  approves it.
- "How do I export a report?" -> Open the report from /reports, then use
  the Export Excel / Export PDF buttons at the top of the page.
- "How do I connect with another researcher?" -> Visit their profile from
  /researchers and send a connection request, or check
  /collaborations/suggested for recommended matches.
- "Where do I see my review assignments?" -> /reviewer/reviews (reviewer
  role only).
"""

_SYSTEM_PROMPT_TEMPLATE = """You are the in-app assistant for SCNA (Scientific Collaboration Network \
Analyzer). You help the current logged-in user in two ways: answering \
questions about how to use the site (FAQ/navigation), and answering \
questions about their own live data on the platform (their publications, \
projects, reviews, collaborations, and -- for admins -- institution/system \
data) by calling the tools available to you.

The person you're talking to: {name}, role: {role}{institution_clause}.

{site_map}

Rules:
- For "how do I / where is / what is" questions about the site, answer \
directly from the site knowledge above -- don't call a tool.
- For anything about the person's own data (counts, lists, statuses of \
their publications/projects/reviews/collaborations, or institution/system \
stats if they're an admin), call the relevant tool rather than guessing.
- Only call a tool when it's actually needed to answer the question -- \
don't call tools speculatively.
- You cannot see or affect any other specific user's private data beyond \
what your tools return; if asked about someone else's personal records, \
say that's not something you have access to, and suggest where they could \
look instead (e.g. /researchers directory for public profile info, or the \
institution/system reports which aggregate without exposing everything).
- Keep answers short and concrete. Prefer a few sentences or a short list \
over a long essay. When it helps, point to the relevant page (e.g. \
"you can see this in full on /reports/publications").
- You cannot perform actions (submitting, editing, deleting, approving) \
yourself -- only read data and point the person to the right page to do it.
- If a tool call fails or returns no data, say so plainly rather than \
inventing numbers.
"""


def _institution_clause(current_user: User, db: Session) -> str:
    if current_user.institution_id is None:
        return ""
    institution = db.get(Institution, current_user.institution_id)
    return f", institution: {institution.name}" if institution else ""


def _json_safe(value):
    """Recursively converts date/datetime values (as returned by the report
    repository) into ISO strings so the payload can go straight into a
    tool_result content block."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


def _my_profile(db: Session, current_user: User) -> ResearcherProfile | None:
    return db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))


# --- Tools -----------------------------------------------------------------
# Each entry: JSON schema (Anthropic tool format) + the handler that
# executes it. Handlers take (db, current_user) and return a JSON-safe dict.

def _tool_my_profile_and_activity(db: Session, current_user: User) -> dict:
    profile = _my_profile(db, current_user)
    if profile is None:
        return {"has_profile": False, "message": "This account has no researcher profile."}
    data = repo.researcher_report(db, profile, is_reviewer=current_user.role == UserRole.REVIEWER)
    return _json_safe({"has_profile": True, **data})


def _tool_my_publications(db: Session, current_user: User) -> dict:
    profile = _my_profile(db, current_user)
    if profile is None:
        return {"has_profile": False, "message": "This account has no researcher profile, so no publications."}
    return _json_safe(repo.publications_report(db, researcher_id=profile.researcher_id))


def _tool_my_projects(db: Session, current_user: User) -> dict:
    profile = _my_profile(db, current_user)
    if profile is None:
        return {"has_profile": False, "message": "This account has no researcher profile, so no projects."}
    return _json_safe(repo.projects_report(db, researcher_id=profile.researcher_id))


def _tool_my_reviews(db: Session, current_user: User) -> dict:
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return _json_safe(repo.all_reviews_report(db))
    if current_user.role != UserRole.REVIEWER:
        return {"message": "This account is not a Reviewer, so it has no review assignments."}
    return _json_safe(repo.reviews_report(db, current_user.user_id))


def _tool_my_collaborations(db: Session, current_user: User) -> dict:
    profile = _my_profile(db, current_user)
    if profile is None:
        return {"has_profile": False, "message": "This account has no researcher profile, so no collaborations."}
    return _json_safe(repo.collaborations_report(db, profile.researcher_id))


def _tool_institution_overview(db: Session, current_user: User) -> dict:
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return {"message": "Provide an institution_name to look up, or use the System report for a platform-wide view."}
    if current_user.institution_id is None:
        return {"message": "This account is not linked to an institution."}
    institution = db.get(Institution, current_user.institution_id)
    if institution is None:
        return {"message": "Institution not found."}
    return _json_safe(repo.institution_report(db, institution))


def _tool_lookup_institution(db: Session, current_user: User, institution_name: str) -> dict:
    if current_user.role != UserRole.SYSTEM_ADMIN:
        return {"message": "Only a system_admin can look up an arbitrary institution by name."}
    institution = db.scalar(select(Institution).where(Institution.name.ilike(f"%{institution_name}%")))
    if institution is None:
        return {"message": f"No institution found matching '{institution_name}'."}
    return _json_safe(repo.institution_report(db, institution))


def _tool_system_overview(db: Session, current_user: User) -> dict:
    if current_user.role != UserRole.SYSTEM_ADMIN:
        return {"message": "Only a system_admin can see the system-wide report."}
    return _json_safe(repo.system_report(db))


_TOOL_SPECS = {
    "get_my_profile_and_activity": {
        "roles": {UserRole.RESEARCHER, UserRole.REVIEWER},
        "schema": {
            "name": "get_my_profile_and_activity",
            "description": (
                "Get the current user's own researcher profile and an activity summary: "
                "publication counts by status/type, project counts, collaboration count, "
                "and (for reviewers) review counts."
            ),
            "input_schema": {"type": "object", "properties": {}},
        },
        "handler": lambda db, u, **_: _tool_my_profile_and_activity(db, u),
    },
    "get_my_publications": {
        "roles": {UserRole.RESEARCHER, UserRole.REVIEWER},
        "schema": {
            "name": "get_my_publications",
            "description": "List the current user's own publications with status, type, year, and venue.",
            "input_schema": {"type": "object", "properties": {}},
        },
        "handler": lambda db, u, **_: _tool_my_publications(db, u),
    },
    "get_my_projects": {
        "roles": {UserRole.RESEARCHER, UserRole.REVIEWER},
        "schema": {
            "name": "get_my_projects",
            "description": "List the current user's own projects with status and dates.",
            "input_schema": {"type": "object", "properties": {}},
        },
        "handler": lambda db, u, **_: _tool_my_projects(db, u),
    },
    "get_my_reviews": {
        "roles": {UserRole.REVIEWER, UserRole.SYSTEM_ADMIN},
        "schema": {
            "name": "get_my_reviews",
            "description": (
                "Get review data. For a Reviewer, their own assigned reviews (status, "
                "recommendation, target). For a system_admin, a system-wide view across "
                "every reviewer, since admins have no personal reviews of their own."
            ),
            "input_schema": {"type": "object", "properties": {}},
        },
        "handler": lambda db, u, **_: _tool_my_reviews(db, u),
    },
    "get_my_collaborations": {
        "roles": {UserRole.RESEARCHER, UserRole.REVIEWER},
        "schema": {
            "name": "get_my_collaborations",
            "description": "Get the current user's collaboration network: collaborators, strength, and date range.",
            "input_schema": {"type": "object", "properties": {}},
        },
        "handler": lambda db, u, **_: _tool_my_collaborations(db, u),
    },
    "get_institution_overview": {
        "roles": {UserRole.INSTITUTION_ADMIN},
        "schema": {
            "name": "get_institution_overview",
            "description": "Get stats for the current user's own institution: researcher, publication, project, and conference counts.",
            "input_schema": {"type": "object", "properties": {}},
        },
        "handler": lambda db, u, **_: _tool_institution_overview(db, u),
    },
    "lookup_institution": {
        "roles": {UserRole.SYSTEM_ADMIN},
        "schema": {
            "name": "lookup_institution",
            "description": "Look up any institution by (partial) name and get its stats. system_admin only.",
            "input_schema": {
                "type": "object",
                "properties": {"institution_name": {"type": "string", "description": "Full or partial institution name"}},
                "required": ["institution_name"],
            },
        },
        "handler": lambda db, u, institution_name="": _tool_lookup_institution(db, u, institution_name),
    },
    "get_system_overview": {
        "roles": {UserRole.SYSTEM_ADMIN},
        "schema": {
            "name": "get_system_overview",
            "description": "Get platform-wide stats: total users by role, institutions, publications, projects, conferences. system_admin only.",
            "input_schema": {"type": "object", "properties": {}},
        },
        "handler": lambda db, u, **_: _tool_system_overview(db, u),
    },
}


def _tools_for_role(role: UserRole) -> list[dict]:
    return [spec["schema"] for spec in _TOOL_SPECS.values() if role in spec["roles"]]


def _execute_tool(db: Session, current_user: User, name: str, tool_input: dict) -> dict:
    spec = _TOOL_SPECS.get(name)
    if spec is None:
        return {"error": f"Unknown tool: {name}"}
    if current_user.role not in spec["roles"]:
        return {"error": "This account's role doesn't have access to that data."}
    try:
        return spec["handler"](db, current_user, **tool_input)
    except TypeError as e:
        return {"error": f"Invalid arguments for {name}: {e}"}
    except Exception:
        logger.exception("Chatbot tool %s failed", name)
        return {"error": "Something went wrong fetching that data."}


def _display_name(current_user: User, db: Session) -> str:
    profile = _my_profile(db, current_user)
    if profile:
        return f"{profile.first_name} {profile.last_name}"
    return current_user.email


def run_chat(db: Session, current_user: User, messages: list[dict]) -> str:
    """
    messages: [{"role": "user"|"assistant", "content": str}, ...] -- the
    client's full conversation so far, oldest first. Returns the assistant's
    reply text.
    """
    if not settings.ANTHROPIC_API_KEY:
        raise ChatbotUnavailable("Chatbot is not configured on this server.")

    trimmed = messages[-settings.CHATBOT_MAX_HISTORY_MESSAGES:]
    working_messages = [{"role": m["role"], "content": m["content"]} for m in trimmed]

    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
        name=_display_name(current_user, db),
        role=current_user.role.value,
        institution_clause=_institution_clause(current_user, db),
        site_map=_SITE_MAP,
    )
    tools = _tools_for_role(current_user.role)
    client = _get_client()

    for _ in range(settings.CHATBOT_MAX_TOOL_ITERATIONS):
        try:
            response = client.messages.create(
                model=settings.CHATBOT_MODEL,
                max_tokens=1024,
                system=system_prompt,
                tools=tools,
                messages=working_messages,
            )
        except anthropic.APIError as e:
            logger.error("Anthropic API error in chatbot: %s", e)
            raise ChatbotUnavailable("The chatbot is temporarily unavailable. Please try again shortly.") from e

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text").strip() or \
                "I don't have a specific answer for that -- could you rephrase?"

        working_messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result = _execute_tool(db, current_user, block.name, block.input or {})
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result),
            })
        working_messages.append({"role": "user", "content": tool_results})

    return "I looked into that but couldn't pull together a complete answer -- please try asking in a different way, or check the relevant Reports page directly."
