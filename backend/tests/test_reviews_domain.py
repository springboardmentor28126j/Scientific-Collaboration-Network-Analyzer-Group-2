"""
Domain tests for /reviews. The rules that matter here are the most
business-logic-dense in the app: only the right institution admin (or a
system admin) can assign a reviewer, the reviewer's identity is masked
from anyone who shouldn't see it (blind review), a review must be
accepted before it can be submitted, and assigning the first reviewer
automatically moves the target out of the submitted queue.
"""
from app.models.user import UserRole


def test_researcher_cannot_assign_a_review(client, login_as, make_researcher, make_publication, make_user):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)

    login_as(author.user)
    resp = client.post("/api/v1/reviews", json={
        "target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer.user_id,
    })
    assert resp.status_code == 403, resp.text


def test_reviewer_id_must_belong_to_an_actual_reviewer_account(client, login_as, make_researcher, make_publication, make_user):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    not_a_reviewer = make_user(role=UserRole.RESEARCHER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.post("/api/v1/reviews", json={
        "target_type": "publication", "target_id": pub.publication_id, "reviewer_id": not_a_reviewer.user_id,
    })
    assert resp.status_code == 400, resp.text


def test_system_admin_can_assign_a_reviewer_and_it_moves_status_to_under_review(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.post("/api/v1/reviews", json={
        "target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer.user_id,
    })
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "assigned"

    login_as(author.user)
    pub_resp = client.get(f"/api/v1/publications/{pub.publication_id}")
    assert pub_resp.json()["status"] == "under_review"


def test_institution_admin_can_only_assign_within_their_own_institution(
    client, login_as, make_researcher, make_publication, make_institution, make_user,
):
    inst_a = make_institution(name="Institution A")
    inst_b = make_institution(name="Institution B")

    author = make_researcher(institution_id=inst_a.institution_id)
    pub = make_publication(author, status="submitted", institution_id=inst_a.institution_id)
    reviewer_a = make_user(role=UserRole.REVIEWER, institution_id=inst_a.institution_id)
    admin_b = make_user(role=UserRole.INSTITUTION_ADMIN, institution_id=inst_b.institution_id)

    login_as(admin_b)
    resp = client.post("/api/v1/reviews", json={
        "target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer_a.user_id,
    })
    assert resp.status_code == 403, resp.text  # wrong institution's admin, can't touch this publication at all


def test_institution_admin_cannot_assign_a_reviewer_from_a_different_institution(
    client, login_as, make_researcher, make_publication, make_institution, make_user,
):
    inst_a = make_institution(name="Institution A")
    inst_b = make_institution(name="Institution B")

    author = make_researcher(institution_id=inst_a.institution_id)
    pub = make_publication(author, status="submitted", institution_id=inst_a.institution_id)
    reviewer_from_b = make_user(role=UserRole.REVIEWER, institution_id=inst_b.institution_id)
    admin_a = make_user(role=UserRole.INSTITUTION_ADMIN, institution_id=inst_a.institution_id)

    login_as(admin_a)
    resp = client.post("/api/v1/reviews", json={
        "target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer_from_b.user_id,
    })
    assert resp.status_code == 403, resp.text  # right publication, wrong reviewer's institution


def test_cannot_assign_the_same_reviewer_twice_to_the_same_target(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    client.post("/api/v1/reviews", json={"target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer.user_id})
    resp = client.post("/api/v1/reviews", json={"target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer.user_id})
    assert resp.status_code == 409, resp.text


def _assign(client, login_as, admin, pub, reviewer):
    login_as(admin)
    resp = client.post("/api/v1/reviews", json={
        "target_type": "publication", "target_id": pub.publication_id, "reviewer_id": reviewer.user_id,
    })
    return resp.json()["review_id"]


def test_reviewer_identity_is_hidden_from_the_publications_own_author(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(author.user)
    resp = client.get(f"/api/v1/reviews/{review_id}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["reviewer_id"] is None  # masked -- the author can see a review exists, not who's doing it


def test_reviewer_identity_is_visible_to_the_reviewer_the_assigner_and_admins(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(reviewer)
    resp = client.get(f"/api/v1/reviews/{review_id}")
    assert resp.json()["reviewer_id"] == reviewer.user_id

    login_as(admin)
    resp = client.get(f"/api/v1/reviews/{review_id}")
    assert resp.json()["reviewer_id"] == reviewer.user_id


def test_unrelated_researcher_cannot_view_a_review_at_all(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    stranger = make_researcher(first_name="Stranger")
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(stranger.user)
    resp = client.get(f"/api/v1/reviews/{review_id}")
    assert resp.status_code == 403, resp.text


def test_only_the_assigned_reviewer_can_accept_or_decline(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    someone_else = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(someone_else)
    resp = client.post(f"/api/v1/reviews/{review_id}/accept")
    assert resp.status_code == 403, resp.text

    login_as(reviewer)
    resp = client.post(f"/api/v1/reviews/{review_id}/accept")
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "accepted"


def test_cannot_respond_to_the_same_review_invitation_twice(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(reviewer)
    resp = client.post(f"/api/v1/reviews/{review_id}/accept")
    assert resp.status_code == 200

    resp = client.post(f"/api/v1/reviews/{review_id}/decline")
    assert resp.status_code == 400, resp.text


def test_declining_a_review_leaves_it_declined(client, login_as, make_researcher, make_publication, make_user):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(reviewer)
    resp = client.post(f"/api/v1/reviews/{review_id}/decline")
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "declined"


def test_cannot_submit_a_review_before_accepting_it(client, login_as, make_researcher, make_publication, make_user):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(reviewer)
    resp = client.patch(f"/api/v1/reviews/{review_id}/submit", json={"recommendation": "accept", "score": 8})
    assert resp.status_code == 400, resp.text


def test_submitting_a_review_requires_accept_first_then_completes_it(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(reviewer)
    client.post(f"/api/v1/reviews/{review_id}/accept")
    resp = client.patch(f"/api/v1/reviews/{review_id}/submit", json={
        "recommendation": "minor_revision", "score": 7, "comments": "Solid work, needs a stronger related-work section.",
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "completed"
    assert body["recommendation"] == "minor_revision"
    assert body["score"] == 7


def test_score_must_be_within_the_one_to_ten_range(client, login_as, make_researcher, make_publication, make_user):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    review_id = _assign(client, login_as, admin, pub, reviewer)

    login_as(reviewer)
    client.post(f"/api/v1/reviews/{review_id}/accept")
    resp = client.patch(f"/api/v1/reviews/{review_id}/submit", json={"recommendation": "accept", "score": 11})
    assert resp.status_code == 422, resp.text


def test_publication_owner_can_see_the_review_roster_for_their_own_paper(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    _assign(client, login_as, admin, pub, reviewer)

    login_as(author.user)
    resp = client.get("/api/v1/reviews", params={"target_type": "publication", "target_id": pub.publication_id})
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) == 1
    assert resp.json()[0]["reviewer_id"] is None  # still masked, even for the owner viewing their own roster


def test_unrelated_researcher_cannot_see_the_review_roster(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    stranger = make_researcher(first_name="Stranger")
    pub = make_publication(author, status="submitted")
    reviewer = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    _assign(client, login_as, admin, pub, reviewer)

    login_as(stranger.user)
    resp = client.get("/api/v1/reviews", params={"target_type": "publication", "target_id": pub.publication_id})
    assert resp.status_code == 403, resp.text


def test_list_my_reviews_only_returns_the_current_reviewers_own_assignments(
    client, login_as, make_researcher, make_publication, make_user,
):
    author = make_researcher()
    pub_a = make_publication(author, title="Paper A", status="submitted")
    pub_b = make_publication(author, title="Paper B", status="submitted")
    reviewer_1 = make_user(role=UserRole.REVIEWER)
    reviewer_2 = make_user(role=UserRole.REVIEWER)
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    _assign(client, login_as, admin, pub_a, reviewer_1)
    _assign(client, login_as, admin, pub_b, reviewer_2)

    login_as(reviewer_1)
    resp = client.get("/api/v1/reviews/mine")
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) == 1
    assert resp.json()[0]["target_id"] == pub_a.publication_id


def test_assigning_a_review_for_a_nonexistent_publication_returns_404(client, login_as, make_user):
    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    reviewer = make_user(role=UserRole.REVIEWER)

    login_as(admin)
    resp = client.post("/api/v1/reviews", json={"target_type": "publication", "target_id": 999999, "reviewer_id": reviewer.user_id})
    assert resp.status_code == 404, resp.text
