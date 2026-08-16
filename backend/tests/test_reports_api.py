"""
Tests for the new backend /reports API. Focus is on the two things that
matter most here: the aggregation numbers are actually correct (not just
"the endpoint returns 200"), and the permission scoping matches what each
report is supposed to restrict access to.
"""
from app.models.user import UserRole, AffiliationStatus


def test_researcher_report_counts_only_my_own_publications(client, login_as, make_researcher, make_publication):
    me = make_researcher(first_name="Me")
    someone_else = make_researcher(first_name="Someone")
    make_publication(me, title="Mine 1", status="draft")
    make_publication(me, title="Mine 2", status="published")
    make_publication(someone_else, title="Not mine")

    login_as(me.user)
    resp = client.get("/api/v1/reports/researcher")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["publication_count"] == 2
    assert len(body["publications"]) == 2
    statuses = {row["label"]: row["count"] for row in body["publications_by_status"]}
    assert statuses == {"draft": 1, "published": 1}


def test_researcher_report_requires_a_profile(client, login_as, make_user):
    bare_user = make_user(role=UserRole.RESEARCHER)
    login_as(bare_user)
    resp = client.get("/api/v1/reports/researcher")
    assert resp.status_code == 400, resp.text


def test_institution_report_scopes_correctly_to_one_institution(
    client, login_as, make_researcher, make_publication, make_institution, make_user,
):
    inst_a = make_institution(name="A")
    inst_b = make_institution(name="B")
    author_a = make_researcher(institution_id=inst_a.institution_id, affiliation_status=AffiliationStatus.APPROVED)
    make_researcher(institution_id=inst_b.institution_id, affiliation_status=AffiliationStatus.APPROVED)
    make_publication(author_a, institution_id=inst_a.institution_id)

    admin_a = make_user(role=UserRole.INSTITUTION_ADMIN, institution_id=inst_a.institution_id)
    login_as(admin_a)
    resp = client.get(f"/api/v1/reports/institution/{inst_a.institution_id}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_publications"] == 1
    assert body["total_researchers"] == 1


def test_institution_admin_cannot_view_another_institutions_report(client, login_as, make_institution, make_user):
    inst_a = make_institution(name="A")
    inst_b = make_institution(name="B")
    admin_a = make_user(role=UserRole.INSTITUTION_ADMIN, institution_id=inst_a.institution_id)

    login_as(admin_a)
    resp = client.get(f"/api/v1/reports/institution/{inst_b.institution_id}")
    assert resp.status_code == 403, resp.text


def test_system_admin_can_view_any_institutions_report(client, login_as, make_institution, make_user):
    inst = make_institution(name="Any Institution")
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.get(f"/api/v1/reports/institution/{inst.institution_id}")
    assert resp.status_code == 200, resp.text


def test_researcher_cannot_view_institution_report_at_all(client, login_as, make_researcher, make_institution):
    inst = make_institution()
    researcher = make_researcher(institution_id=inst.institution_id)

    login_as(researcher.user)
    resp = client.get(f"/api/v1/reports/institution/{inst.institution_id}")
    assert resp.status_code == 403, resp.text


def test_publications_report_mine_filter_and_year_filter(client, login_as, make_researcher, make_publication):
    from datetime import date
    me = make_researcher()
    other = make_researcher(first_name="Other")
    make_publication(me, title="Mine 2024", publication_date=date(2024, 1, 1))
    make_publication(me, title="Mine 2026", publication_date=date(2026, 1, 1))
    make_publication(other, title="Theirs 2026", publication_date=date(2026, 1, 1))

    login_as(me.user)
    resp = client.get("/api/v1/reports/publications", params={"mine": "true"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 2

    resp = client.get("/api/v1/reports/publications", params={"mine": "true", "year": 2026})
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["title"] == "Mine 2026"

    # No mine filter -- system-wide, sees everyone's.
    resp = client.get("/api/v1/reports/publications", params={"year": 2026})
    assert resp.json()["total"] == 2


def test_projects_report_mine_filter(client, login_as, make_researcher, make_user):
    from app.models.project import Project, ProjectMember, ProjectMemberStatus
    lead = make_researcher(first_name="Lead")
    other_lead = make_researcher(first_name="Other")
    login_as(lead.user)

    resp = client.post("/api/v1/projects", json={"title": "My Project"})
    assert resp.status_code == 201, resp.text

    login_as(other_lead.user)
    resp = client.post("/api/v1/projects", json={"title": "Someone Else's Project"})
    assert resp.status_code == 201, resp.text

    login_as(lead.user)
    resp = client.get("/api/v1/reports/projects", params={"mine": "true"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["title"] == "My Project"


def test_conferences_report_mine_filter(client, login_as, make_researcher, make_user, make_institution):
    inst = make_institution()
    organizer = make_user(role=UserRole.SYSTEM_ADMIN)
    attendee = make_researcher()

    login_as(organizer)
    resp = client.post("/api/v1/conferences", json={
        "name": "Test Conference", "start_date": "2026-09-01", "end_date": "2026-09-03",
    })
    assert resp.status_code == 201, resp.text
    conf_id = resp.json()["conference_id"]

    login_as(attendee.user)
    resp = client.post(f"/api/v1/conferences/{conf_id}/register", json={"role": "attendee"})
    assert resp.status_code == 201, resp.text

    resp = client.get("/api/v1/reports/conferences", params={"mine": "true"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 1

    other_researcher = make_researcher(first_name="NotRegistered")
    login_as(other_researcher.user)
    resp = client.get("/api/v1/reports/conferences", params={"mine": "true"})
    assert resp.json()["total"] == 0


def test_reviews_report_blocks_institution_admin(client, login_as, make_user):
    admin = make_user(role=UserRole.INSTITUTION_ADMIN)
    login_as(admin)
    resp = client.get("/api/v1/reports/reviews")
    assert resp.status_code == 403, resp.text


def test_reviews_report_system_admin_sees_all_reviewers(client, login_as, make_researcher, make_publication, make_user):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    other_reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    client.post("/api/v1/reviews", json={"target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer.user_id})

    resp = client.get("/api/v1/reports/reviews")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["scope"] == "all"
    assert body["total"] == 1
    assert body["items"][0]["reviewer_name"]

    login_as(reviewer)
    resp = client.get("/api/v1/reports/reviews")
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 1
    assert resp.json()["scope"] == "mine"

    login_as(other_reviewer)
    resp = client.get("/api/v1/reports/reviews")
    assert resp.json()["total"] == 0
    assert resp.json()["scope"] == "mine"


def test_collaborations_report_totals_strength_correctly(client, login_as, make_researcher):
    a = make_researcher(first_name="A")
    b = make_researcher(first_name="B")

    login_as(a.user)
    resp = client.post("/api/v1/collaboration-request", json={"addressee_researcher_id": b.researcher_id})
    request_id = resp.json()["collaboration_request_id"]
    login_as(b.user)
    client.patch(f"/api/v1/collaboration-request/{request_id}", json={"status": "accepted"})

    resp = client.get("/api/v1/reports/collaborations")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_collaborators"] == 1
    assert body["total_strength"] == body["items"][0]["strength"]


def test_system_report_requires_system_admin(client, login_as, make_researcher):
    researcher = make_researcher()
    login_as(researcher.user)
    resp = client.get("/api/v1/reports/system")
    assert resp.status_code == 403, resp.text


def test_system_report_counts_across_the_whole_platform(client, login_as, make_researcher, make_publication, make_user):
    a = make_researcher()
    b = make_researcher()
    make_publication(a, status="draft")
    make_publication(b, status="published")
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.get("/api/v1/reports/system")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_publications"] == 2
    assert body["total_users"] >= 3  # a, b, admin
