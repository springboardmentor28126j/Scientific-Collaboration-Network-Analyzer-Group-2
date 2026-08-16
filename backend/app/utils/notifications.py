from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email_sender import send_notification_email
from app.models.notification import Notification
from app.models.user import User

# notif_type -> the subject line for its email. Only types listed here also
# trigger an email; everything else stays in-app only. Deliberately an
# allow-list (not "email everything") so a brand new in-app notification
# type added somewhere else in the app never silently starts emailing
# people until someone consciously opts that type in here.
#
# Connection & Collaboration (Milestone 3 email rollout, phase 1):
EMAIL_ENABLED_NOTIF_TYPES: dict[str, str] = {
    "collaboration_request_received": "You have a new collaboration request",
    "collaboration_request_accepted": "Your collaboration request was accepted",
    "collaboration_request_rejected": "Your collaboration request was declined",
    "project_invite": "You've been invited to collaborate on a project",
    "project_member_removed": "You've been removed from a project",

    # Phase 2: everything else that was in-app-only, now opted in.
    "account_deactivated": "Your account has been deactivated",
    "affiliation_approved": "Institution affiliation approved",
    "affiliation_pending": "New researcher affiliation request",
    "affiliation_rejected": "Institution affiliation rejected",
    "conference_submission_status_changed": "Conference submission status updated",
    "institution_admin_pending": "New Institution Admin application",
    "password_reset": "Password changed",
    "project_invite_response": "Your project invitation response",
    "publication_status_changed": "Publication status updated",
    "review_accepted": "Review invitation accepted",
    "review_assigned": "New review assignment",
    "review_completed": "Review completed",
    "review_declined": "Review invitation declined",
}


def notify(
    db: Session,
    user_id: int | None,
    notif_type: str,
    title: str,
    message: str | None = None,
    link_url: str | None = None,
) -> None:
    """
    Writes a single in-app notification for user_id. Silently does nothing if
    user_id is None (e.g. an action with no clear single recipient) rather
    than making every call site guard against that itself.

    Deliberately best-effort and separate from the action's own commit: if
    this fails, it must never take down the request that triggered it -- a
    missed notification is much better than a failed publish/assignment/etc.

    In-app is always the primary record. For notif_types listed in
    EMAIL_ENABLED_NOTIF_TYPES, this also sends an email using the exact
    same title/message already written above -- so every call site in the
    app automatically gets email coverage the moment its notif_type is
    added to that registry, with no changes needed at the call site itself.
    """
    if user_id is None:
        return
    try:
        db.add(Notification(user_id=user_id, notif_type=notif_type, title=title, message=message, link_url=link_url))
        db.commit()
    except Exception:
        db.rollback()

    if notif_type in EMAIL_ENABLED_NOTIF_TYPES:
        _send_notification_email(db, user_id, notif_type, title, message, link_url)


def _send_notification_email(
    db: Session, user_id: int, notif_type: str, title: str, message: str | None, link_url: str | None,
) -> None:
    # Just as best-effort as the in-app write above: a failed/misconfigured
    # SMTP send must never surface as a failure of whatever action (accepting
    # a request, sending an invite, removing a member, ...) triggered this.
    try:
        user = db.get(User, user_id)
        if user is None or not user.email:
            return
        subject = EMAIL_ENABLED_NOTIF_TYPES[notif_type]
        full_link = f"{settings.FRONTEND_BASE_URL}{link_url}" if link_url else None
        send_notification_email(user.email, subject, message or title, full_link)
    except Exception:
        pass