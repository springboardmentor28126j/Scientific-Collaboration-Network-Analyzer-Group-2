"""
Domain tests for collaboration requests/connections/messaging. The rules
that matter here: you can't request yourself, duplicate/redundant requests
are blocked, only the addressee can accept/reject (only the requester can
cancel), accepting creates a durable Collaboration, and private messaging
is gated to an established Collaboration -- there is no way to message
someone you're not connected with.
"""
from app.models.user import UserRole


def test_cannot_send_a_collaboration_request_to_yourself(client, login_as, make_researcher):
    me = make_researcher()
    login_as(me.user)

    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": me.researcher_id})
    assert resp.status_code == 400, resp.text


def test_send_and_accept_a_collaboration_request_creates_a_connection(client, login_as, make_researcher):
    requester = make_researcher(first_name="Alice")
    addressee = make_researcher(first_name="Bob")

    login_as(requester.user)
    resp = client.post("/api/v1/collaboration-request", json={
        "addressee_researcher_id": addressee.researcher_id, "message": "Let's work together",
    })
    assert resp.status_code == 201, resp.text
    request_id = resp.json()["collaboration_request_id"]
    assert resp.json()["status"] == "pending"

    # Only the addressee can accept -- the requester trying to "accept their own" request should fail.
    login_as(requester.user)
    resp = client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "accepted"})
    assert resp.status_code == 403, resp.text

    login_as(addressee.user)
    resp = client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "accepted"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "accepted"

    # A real Collaboration should now exist and be visible to both sides.
    resp = client.get("/api/v1/collaborations/my")
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 1

    login_as(requester.user)
    resp = client.get("/api/v1/collaborations/my")
    assert resp.json()["total"] == 1


def test_only_requester_can_cancel_a_pending_request(client, login_as, make_researcher):
    requester = make_researcher(first_name="Alice")
    addressee = make_researcher(first_name="Bob")

    login_as(requester.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})
    request_id = resp.json()["collaboration_request_id"]

    login_as(addressee.user)  # addressee trying to cancel -- should fail, only requester can cancel
    resp = client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "cancelled"})
    assert resp.status_code == 403, resp.text

    login_as(requester.user)
    resp = client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "cancelled"})
    assert resp.status_code == 200, resp.text


def test_a_second_request_between_the_same_pending_pair_is_rejected(client, login_as, make_researcher):
    requester = make_researcher(first_name="Alice")
    addressee = make_researcher(first_name="Bob")

    login_as(requester.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})
    assert resp.status_code == 201

    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})
    assert resp.status_code == 409, resp.text


def test_cannot_request_someone_you_are_already_connected_with(client, login_as, make_researcher):
    requester = make_researcher(first_name="Alice")
    addressee = make_researcher(first_name="Bob")

    login_as(requester.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})
    request_id = resp.json()["collaboration_request_id"]

    login_as(addressee.user)
    client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "accepted"})

    login_as(requester.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})
    assert resp.status_code == 409, resp.text


def test_responding_twice_to_the_same_request_is_rejected(client, login_as, make_researcher):
    requester = make_researcher(first_name="Alice")
    addressee = make_researcher(first_name="Bob")

    login_as(requester.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})
    request_id = resp.json()["collaboration_request_id"]

    login_as(addressee.user)
    resp = client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "accepted"})
    assert resp.status_code == 200

    resp = client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "rejected"})
    assert resp.status_code == 400, resp.text


def _connect(client, login_as, requester, addressee):
    """Test helper: send + accept a request, returns the resulting collaboration_id."""
    login_as(requester.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": addressee.researcher_id})
    request_id = resp.json()["collaboration_request_id"]
    login_as(addressee.user)
    client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "accepted"})
    resp = client.get("/api/v1/collaborations/my")
    return resp.json()["items"][0]["collaboration_id"]


def test_only_connected_participants_can_message_each_other(client, login_as, make_researcher):
    a = make_researcher(first_name="Alice")
    b = make_researcher(first_name="Bob")
    stranger = make_researcher(first_name="Carol")

    collaboration_id = _connect(client, login_as, a, b)

    login_as(stranger.user)
    resp = client.post(f"/api/v1/collaborations/{collaboration_id}/messages", json={"body": "Hi, let me in?"})
    assert resp.status_code == 403, resp.text

    login_as(a.user)
    resp = client.post(f"/api/v1/collaborations/{collaboration_id}/messages", json={"body": "Hey Bob!"})
    assert resp.status_code == 201, resp.text

    login_as(b.user)
    resp = client.get(f"/api/v1/collaborations/{collaboration_id}/messages")
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["body"] == "Hey Bob!"


def test_messaging_someone_you_are_not_connected_with_is_impossible(client, login_as, make_researcher):
    """There's no collaboration_id to even post to without an established
    connection first -- this asserts posting to a nonexistent/foreign
    collaboration_id (e.g. one guessed or belonging to two other people)
    is rejected, not silently allowed."""
    a = make_researcher(first_name="Alice")
    b = make_researcher(first_name="Bob")
    outsider = make_researcher(first_name="Eve")

    collaboration_id = _connect(client, login_as, a, b)

    login_as(outsider.user)
    resp = client.post(f"/api/v1/collaborations/{collaboration_id}/messages", json={"body": "Let me in"})
    assert resp.status_code == 403, resp.text

    resp = client.post("/api/v1/collaborations/999999/messages", json={"body": "Ghost thread"})
    assert resp.status_code == 404, resp.text


def test_empty_message_body_is_rejected(client, login_as, make_researcher):
    a = make_researcher(first_name="Alice")
    b = make_researcher(first_name="Bob")
    collaboration_id = _connect(client, login_as, a, b)

    login_as(a.user)
    resp = client.post(f"/api/v1/collaborations/{collaboration_id}/messages", json={"body": "   "})
    assert resp.status_code == 422, resp.text


def test_system_admin_can_view_any_collaboration_but_not_message_in_it(client, login_as, make_researcher, make_user):
    a = make_researcher(first_name="Alice")
    b = make_researcher(first_name="Bob")
    collaboration_id = _connect(client, login_as, a, b)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.get(f"/api/v1/collaborations/{collaboration_id}")
    assert resp.status_code == 200, resp.text

    # Viewing is admin-permitted; messaging is participant-only. A system
    # admin typically has no ResearcherProfile at all, so this correctly
    # 400s ("you need a profile") rather than 403 -- there's no researcher
    # identity for them to send a message *as* in the first place.
    resp = client.post(f"/api/v1/collaborations/{collaboration_id}/messages", json={"body": "I'm watching"})
    assert resp.status_code == 400, resp.text
