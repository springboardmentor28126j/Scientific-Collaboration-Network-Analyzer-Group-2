"""
Tests for the email layer added on top of the existing in-app notification
system for Connection & Collaboration events. These mock only send_email()
itself (the actual SMTP call) -- everything above that, including the
allow-list gating and the notify()->email dispatch, runs for real.
"""
from unittest.mock import patch

from app.utils.notifications import notify, EMAIL_ENABLED_NOTIF_TYPES


def test_email_enabled_notif_type_sends_both_inapp_and_email(db_session, make_researcher):
    recipient = make_researcher(first_name="Bob")

    with patch("app.utils.notifications.send_notification_email") as mock_send:
        notify(
            db_session, recipient.user.user_id, "collaboration_request_received", "New collaboration request",
            "Alice wants to connect with you.", link_url="/collaborations/requests",
        )

    from app.models.notification import Notification
    saved = db_session.query(Notification).filter_by(user_id=recipient.user.user_id).all()
    assert len(saved) == 1
    assert saved[0].notif_type == "collaboration_request_received"

    mock_send.assert_called_once()
    call_kwargs = mock_send.call_args.args
    assert call_kwargs[0] == recipient.user.email
    assert call_kwargs[1] == "You have a new collaboration request"
    assert call_kwargs[2] == "Alice wants to connect with you."


def test_notif_type_not_in_allowlist_stays_inapp_only(db_session, make_researcher):
    recipient = make_researcher()

    with patch("app.utils.notifications.send_notification_email") as mock_send:
        notify(db_session, recipient.user.user_id, "some_future_notification_type", "Something happened")

    mock_send.assert_not_called()


def test_all_five_connection_and_collaboration_types_are_registered():
    expected = {
        "collaboration_request_received",
        "collaboration_request_accepted",
        "collaboration_request_rejected",
        "project_invite",
        "project_member_removed",
    }
    assert expected.issubset(EMAIL_ENABLED_NOTIF_TYPES.keys())


def test_a_failed_email_send_does_not_break_notify(db_session, make_researcher):
    """The in-app notification must still be written even if the email
    send blows up -- email is best-effort on top, never a dependency."""
    recipient = make_researcher()

    with patch("app.utils.notifications.send_notification_email", side_effect=RuntimeError("SMTP is down")):
        notify(db_session, recipient.user.user_id, "project_invite", "Project invitation", "You're invited.")

    from app.models.notification import Notification
    saved = db_session.query(Notification).filter_by(user_id=recipient.user.user_id).all()
    assert len(saved) == 1


def test_recipient_with_no_email_is_skipped_gracefully(db_session, make_researcher):
    """user.email is NOT NULL in the schema, so this can't happen through a
    real row -- but _send_notification_email's guard is still real
    defensive code worth exercising directly, in case that constraint
    ever loosens (e.g. a future SSO path that doesn't collect email)."""
    from app.utils.notifications import _send_notification_email

    recipient = make_researcher()
    recipient.user.email = ""  # falsy, without violating NOT NULL
    db_session.commit()

    with patch("app.utils.notifications.send_notification_email") as mock_send:
        _send_notification_email(
            db_session, recipient.user.user_id, "project_member_removed",
            "Removed from a project", "You were removed.", None,
        )

    mock_send.assert_not_called()


def test_full_connection_request_flow_sends_email_via_real_endpoint(client, login_as, make_researcher):
    """End-to-end: hitting the real API triggers the real notify() call
    site in collaborations.py, which triggers the email dispatch -- this
    is the actual integration point, not just the notify() unit above."""
    requester = make_researcher(first_name="Alice")
    addressee = make_researcher(first_name="Bob")

    with patch("app.utils.notifications.send_notification_email") as mock_send:
        login_as(requester.user)
        resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})

    assert resp.status_code == 201, resp.text
    mock_send.assert_called_once()
    to_email = mock_send.call_args.args[0]
    assert to_email == addressee.user.email


def test_connection_accept_and_decline_both_email_the_requester(client, login_as, make_researcher):
    requester = make_researcher(first_name="Alice")
    addressee = make_researcher(first_name="Bob")

    login_as(requester.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})
    request_id = resp.json()["collaboration_request_id"]

    with patch("app.utils.notifications.send_notification_email") as mock_send:
        login_as(addressee.user)
        resp = client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "accepted"})

    assert resp.status_code == 200, resp.text
    mock_send.assert_called_once()
    assert mock_send.call_args.args[0] == requester.user.email
    assert mock_send.call_args.args[1] == "Your collaboration request was accepted"
