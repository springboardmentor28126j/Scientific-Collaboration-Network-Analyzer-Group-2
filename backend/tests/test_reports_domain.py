"""
Tests for /reports/*. These check the actual aggregation math (counts,
group-bys, filters) against known input data, plus the permission rules
that differ report-to-report (institution scoping, reviewer-only, etc.).
"""
from datetime import date

from app.models.user import UserRole, AffiliationStatus


def test_researcher_report_counts_and_breakdowns(client, login_as, make_researcher, make_publication):
    me = make_researcher(first_name="Ada")
    make_publication(me, title="Paper A", status="published", publication_type="journal_paper")
    make_publication(me, title="Paper B", status="draft", publication_type="journal_paper")
    make_publication(me, title="Paper C", status="published", publication_type="conference_paper")

    login_as(me.user)
    resp = client.get("/api/v1/reports/researcher")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["publication_count"] == 3
    assert {d["label"]: d["count"] for d in body["publications_by_status"]} == {"published": 2, "draft": 1}
    assert {d["label"]: d["count"] for d in body["publications_by_type"]} == {"journal_paper": 2, "conference_paper": 1}


def test_researcher_report_review_count_is_zero_for_non_reviewers(client, login_as, make_researcher):
    me = make_researcher()
    login_as(me.user)
    resp = client.get("/api/v1/reports/researcher")
    assert resp.status_code == 200
    assert resp.json()["review_count"] == 0
    assert resp.json()["reviews"] == []


def test_researcher_report_requires_a_profile(client, login_as, make_user):
    bare_user = make_user(role=UserRole.RESEARCHER)
    login_as(bare_user)
    resp = client.get("/api/v1/reports/researcher")
    assert resp.status_code == 400, resp.text


def test_institution_report_counts(client, login_as, make_researcher, make_institution, make_publication, make_user):
    inst = make_institution(name="Test University")
    r1 = make_researcher(institution_id=inst.institution_id, affiliation_status=AffiliationStatus.APPROVED)
    r2 = make_researcher(institution_id=inst.institution_id, affiliation_status=AffiliationStatus.PENDING)
    make_publication(r1, institution_id=inst.institution_id)
    admin = make_user(role=UserRole.INSTITUTION_ADMIN, institution_id=inst.institution_id)

    login_as(admin)
    resp = client.get(f"/api/v1/reports/institution/{inst.institution_id}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_researchers"] == 2
    assert body["approved_researchers"] == 1
    assert body["pending_researchers"] == 1
    assert body["total_publications"] == 1
    assert len(body["researchers"]) == 2


def test_institution_admin_cannot_view_another_institutions_report(client, login_as, make_institution, make_user):
    inst_a = make_institution(name="A")
    inst_b = make_institution(name="B")
    admin_b = make_user(role=UserRole.INSTITUTION_ADMIN, institution_id=inst_b.institution_id)

    login_as(admin_b)
    resp = client.get(f"/api/v1/reports/institution/{inst_a.institution_id}")
    assert resp.status_code == 403, resp.text


def test_system_admin_can_view_any_institutions_report(client, login_as, make_institution, make_user):
    inst = make_institution()
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.get(f"/api/v1/reports/institution/{inst.institution_id}")
    assert resp.status_code == 200, resp.text


def test_researcher_cannot_view_institution_report_at_all(client, login_as, make_researcher, make_institution):
    inst = make_institution()
    r = make_researcher(institution_id=inst.institution_id)
    login_as(r.user)
    resp = client.get(f"/api/v1/reports/institution/{inst.institution_id}")
    assert resp.status_code == 403, resp.text


def test_publications_report_mine_filter(client, login_as, make_researcher, make_publication):
    me = make_researcher(first_name="Me")
    other = make_researcher(first_name="Other")
    make_publication(me, title="Mine")
    make_publication(other, title="Theirs")

    login_as(me.user)
    resp = client.get("/api/v1/reports/publications", params={"mine": "true"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Mine"


def test_publications_report_year_filter(client, login_as, make_researcher, make_publication):
    me = make_researcher()
    make_publication(me, title="2024", publication_date=date(2024, 5, 1))
    make_publication(me, title="2026", publication_date=date(2026, 1, 1))

    login_as(me.user)
    resp = client.get("/api/v1/reports/publications", params={"year": 2026})
    assert resp.status_code == 200
    titles = [p["title"] for p in resp.json()["items"]]
    assert titles == ["2026"]


def test_publications_report_without_mine_returns_everyone(client, login_as, make_researcher, make_publication):
    me = make_researcher(first_name="Me")
    other = make_researcher(first_name="Other")
    make_publication(me)
    make_publication(other)

    login_as(me.user)
    resp = client.get("/api/v1/reports/publications")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_projects_report_mine_includes_pending_invitations(client, login_as, make_researcher):
    """Matches list_projects()'s existing mine= semantics exactly --
    lead OR member, member rows included even while still pending."""
    lead = make_researcher(first_name="Lead")
    invitee = make_researcher(first_name="Invitee")

    login_as(lead.user)
    resp = client.post("/api/v1/projects", json={"title": "Shared Project"})
    project_id = resp.json()["project_id"]

    # Connect them first (invite requires an existing connection), then invite.
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": invitee.researcher_id})
    req_id = resp.json()["collaboration_request_id"]
    login_as(invitee.user)
    client.patch(f"/api/v1/collaboration-request/{req_id}", json={"status": "accepted"})

    login_as(lead.user)
    client.post(f"/api/v1/projects/{project_id}/members", json={"researcher_id": invitee.researcher_id})

    login_as(invitee.user)
    resp = client.get("/api/v1/reports/projects", params={"mine": "true"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 1  # still pending, but shows up as "mine"


def test_reviews_report_requires_actual_reviewer_role(client, login_as, make_user):
    admin = make_user(role=UserRole.INSTITUTION_ADMIN)
    login_as(admin)
    resp = client.get("/api/v1/reports/reviews")
    assert resp.status_code == 403, resp.text  # this is the fix -- institution_admin used to hit this and fail


def test_reviews_report_shows_only_my_assignments(client, login_as, make_researcher, make_publication, make_user):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    client.post("/api/v1/reviews", json={"target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer.user_id})

    login_as(reviewer)
    resp = client.get("/api/v1/reports/reviews")
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 1


def test_collaborations_report_totals(client, login_as, make_researcher):
    a = make_researcher(first_name="Alice")
    b = make_researcher(first_name="Bob")

    login_as(a.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": b.researcher_id})
    req_id = resp.json()["collaboration_request_id"]
    login_as(b.user)
    client.patch(f"/api/v1/collaboration-request/{req_id}", json={"status": "accepted"})

    login_as(a.user)
    resp = client.get("/api/v1/reports/collaborations")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_collaborators"] == 1
    assert body["items"][0]["name"] == "Bob Researcher"


def test_system_report_requires_system_admin(client, login_as, make_researcher):
    r = make_researcher()
    login_as(r.user)
    resp = client.get("/api/v1/reports/system")
    assert resp.status_code == 403, resp.text


def test_system_report_totals(client, login_as, make_researcher, make_publication, make_user):
    make_researcher()
    make_researcher()
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.get("/api/v1/reports/system")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_users"] >= 3  # 2 researchers + this admin
    roles = {d["label"]: d["count"] for d in body["users_by_role"]}
    assert roles.get("researcher", 0) == 2
    assert roles.get("system_admin", 0) == 1
