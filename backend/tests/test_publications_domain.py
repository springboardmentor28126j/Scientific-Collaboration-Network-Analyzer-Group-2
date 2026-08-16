"""
Domain tests for /publications -- the business rules that matter here are
ownership (only the primary author or a system admin may edit/delete),
the affiliation-verification gate on creation, and the separation between
"the author edits their own draft" and "an institution admin changes its
review status" (two different endpoints with different permissions).
"""
from datetime import date

from app.models.user import UserRole, AffiliationStatus


def test_researcher_can_create_a_publication(client, login_as, make_researcher):
    author = make_researcher(first_name="Ada", last_name="Lovelace")
    login_as(author.user)

    resp = client.post("/api/v1/publications", json={
        "title": "Notes on the Analytical Engine",
        "publication_type": "journal_paper",
        "co_author_ids": [],
    })

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["primary_author_id"] == author.researcher_id
    assert body["status"] == "draft"
    assert body["institution_id"] is None


def test_creating_a_publication_requires_a_researcher_profile(client, login_as, make_user):
    # A user with no ResearcherProfile row at all (e.g. mid-registration, or a role that never gets one).
    bare_user = make_user(role=UserRole.RESEARCHER)
    login_as(bare_user)

    resp = client.post("/api/v1/publications", json={
        "title": "Should Not Be Created",
        "publication_type": "journal_paper",
    })

    assert resp.status_code == 400, resp.text


def test_pending_institution_affiliation_blocks_publication_creation(client, login_as, make_researcher, make_institution):
    institution = make_institution()
    author = make_researcher(role=UserRole.RESEARCHER, institution_id=institution.institution_id, affiliation_status=AffiliationStatus.PENDING)
    login_as(author.user)

    resp = client.post("/api/v1/publications", json={
        "title": "Should Be Blocked",
        "publication_type": "journal_paper",
    })

    assert resp.status_code == 403, resp.text
    assert "still pending" in resp.json()["detail"]


def test_approved_institution_affiliation_allows_publication_creation(client, login_as, make_researcher, make_institution):
    institution = make_institution()
    author = make_researcher(role=UserRole.RESEARCHER, institution_id=institution.institution_id, affiliation_status=AffiliationStatus.APPROVED)
    login_as(author.user)

    resp = client.post("/api/v1/publications", json={
        "title": "Should Be Allowed",
        "publication_type": "journal_paper",
    })

    assert resp.status_code == 201, resp.text


def test_independent_researcher_with_no_institution_is_never_blocked(client, login_as, make_researcher):
    # No institution_id at all -- affiliation gating shouldn't apply to independent researchers.
    author = make_researcher(role=UserRole.RESEARCHER, institution_id=None, affiliation_status=AffiliationStatus.NOT_APPLICABLE)
    login_as(author.user)

    resp = client.post("/api/v1/publications", json={
        "title": "Independent Work",
        "publication_type": "journal_paper",
    })

    assert resp.status_code == 201, resp.text


def test_only_primary_author_can_update_their_publication(client, login_as, make_researcher, make_publication):
    author = make_researcher(first_name="Owner", last_name="One")
    other = make_researcher(first_name="Not", last_name="TheOwner")
    pub = make_publication(author, title="Original Title")

    login_as(other.user)
    resp = client.patch(f"/api/v1/publications/{pub.publication_id}", json={"title": "Hijacked Title"})

    assert resp.status_code == 403, resp.text


def test_primary_author_can_update_their_own_publication(client, login_as, make_researcher, make_publication):
    author = make_researcher(first_name="Owner", last_name="One")
    pub = make_publication(author, title="Original Title")

    login_as(author.user)
    resp = client.patch(f"/api/v1/publications/{pub.publication_id}", json={"title": "Updated Title"})

    assert resp.status_code == 200, resp.text
    assert resp.json()["title"] == "Updated Title"


def test_system_admin_can_update_any_publication(client, login_as, make_researcher, make_publication, make_user):
    author = make_researcher(first_name="Owner", last_name="One")
    pub = make_publication(author, title="Original Title")
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.patch(f"/api/v1/publications/{pub.publication_id}", json={"title": "Admin Edited This"})

    assert resp.status_code == 200, resp.text


def test_only_primary_author_or_system_admin_can_delete(client, login_as, make_researcher, make_publication):
    author = make_researcher(first_name="Owner", last_name="One")
    other = make_researcher(first_name="Not", last_name="TheOwner")
    pub = make_publication(author)

    login_as(other.user)
    resp = client.delete(f"/api/v1/publications/{pub.publication_id}")
    assert resp.status_code == 403, resp.text

    login_as(author.user)
    resp = client.delete(f"/api/v1/publications/{pub.publication_id}")
    assert resp.status_code == 204, resp.text


def test_publication_update_cannot_change_status_directly(client, login_as, make_researcher, make_publication):
    """PublicationUpdate deliberately has no `status` field -- a researcher
    editing their own draft can't self-promote it to 'published'. Extra
    fields on a Pydantic model are ignored by default, so this asserts the
    status is untouched rather than expecting a validation error."""
    author = make_researcher()
    pub = make_publication(author, status="draft")

    login_as(author.user)
    resp = client.patch(f"/api/v1/publications/{pub.publication_id}", json={"title": "Still a draft", "status": "published"})

    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "draft"


def test_only_institution_admin_or_system_admin_can_change_status(client, login_as, make_researcher, make_publication):
    author = make_researcher()
    pub = make_publication(author, status="submitted")

    login_as(author.user)  # the author themself, not an admin
    resp = client.patch(f"/api/v1/publications/{pub.publication_id}/status", json={"status": "published"})

    assert resp.status_code == 403, resp.text


def test_institution_admin_can_only_review_their_own_institution_submissions(
    client, login_as, make_researcher, make_publication, make_institution, make_user,
):
    inst_a = make_institution(name="Institution A")
    inst_b = make_institution(name="Institution B")

    author = make_researcher(institution_id=inst_a.institution_id, affiliation_status=AffiliationStatus.APPROVED)
    admin_a = make_user(role=UserRole.INSTITUTION_ADMIN, institution_id=inst_a.institution_id)
    admin_b = make_user(role=UserRole.INSTITUTION_ADMIN, institution_id=inst_b.institution_id)

    pub = make_publication(author, status="submitted", institution_id=inst_a.institution_id)

    login_as(admin_b)
    resp = client.patch(f"/api/v1/publications/{pub.publication_id}/status", json={"status": "published"})
    assert resp.status_code == 403, resp.text

    login_as(admin_a)
    resp = client.patch(f"/api/v1/publications/{pub.publication_id}/status", json={"status": "published"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "published"


def test_editing_a_publication_that_does_not_exist_returns_404(client, login_as, make_researcher):
    author = make_researcher()
    login_as(author.user)
    resp = client.patch("/api/v1/publications/999999", json={"title": "Ghost"})
    assert resp.status_code == 404, resp.text


def test_mine_filter_only_returns_the_current_researchers_own_publications(client, login_as, make_researcher, make_publication):
    me = make_researcher(first_name="Me")
    someone_else = make_researcher(first_name="Someone", last_name="Else")
    make_publication(me, title="My Paper")
    make_publication(someone_else, title="Their Paper")

    login_as(me.user)
    resp = client.get("/api/v1/publications", params={"mine": "true"})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "My Paper"


def test_year_filter_only_matches_publications_in_that_year(client, login_as, make_researcher, make_publication):
    author = make_researcher()
    make_publication(author, title="2024 Paper", publication_date=date(2024, 6, 1))
    make_publication(author, title="2026 Paper", publication_date=date(2026, 1, 15))

    login_as(author.user)
    resp = client.get("/api/v1/publications", params={"year": 2026})

    assert resp.status_code == 200, resp.text
    titles = [p["title"] for p in resp.json()["items"]]
    assert titles == ["2026 Paper"]


def test_page_size_must_be_an_allowed_value(client, login_as, make_researcher):
    author = make_researcher()
    login_as(author.user)
    resp = client.get("/api/v1/publications", params={"page_size": 7})
    assert resp.status_code == 422, resp.text
