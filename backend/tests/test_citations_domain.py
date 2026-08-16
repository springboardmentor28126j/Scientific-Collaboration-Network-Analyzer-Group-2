"""
Domain tests for /publications/{id}/citations. The rules that matter:
exactly one of cited_publication_id / external_title must be given, a
publication can't cite itself, the same internal citation can't be added
twice, only the citing publication's primary author (or system admin) can
add/remove citations, and the APA/MLA/BibTeX generator produces something
usable from a publication's own metadata.
"""
from app.models.user import UserRole


def test_must_provide_either_internal_or_external_target(client, login_as, make_researcher, make_publication):
    author = make_researcher()
    citing = make_publication(author, title="Citing Paper")
    login_as(author.user)

    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={})
    assert resp.status_code == 422, resp.text


def test_cannot_provide_both_internal_and_external_target(client, login_as, make_researcher, make_publication):
    author = make_researcher()
    citing = make_publication(author, title="Citing Paper")
    cited = make_publication(author, title="Cited Paper")
    login_as(author.user)

    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={
        "cited_publication_id": cited.publication_id, "external_title": "Also this one",
    })
    assert resp.status_code == 422, resp.text


def test_publication_cannot_cite_itself(client, login_as, make_researcher, make_publication):
    author = make_researcher()
    pub = make_publication(author, title="Self Referential Paper")
    login_as(author.user)

    resp = client.post(f"/api/v1/publications/{pub.publication_id}/citations", json={
        "cited_publication_id": pub.publication_id,
    })
    assert resp.status_code == 400, resp.text


def test_add_internal_citation_and_see_it_in_references_and_cited_by(client, login_as, make_researcher, make_publication):
    author = make_researcher()
    citing = make_publication(author, title="The New Paper")
    cited = make_publication(author, title="The Foundational Paper")
    login_as(author.user)

    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={
        "cited_publication_id": cited.publication_id, "context": "Builds on their baseline model",
    })
    assert resp.status_code == 201, resp.text
    assert resp.json()["is_internal"] is True
    assert resp.json()["display_title"] == "The Foundational Paper"

    resp = client.get(f"/api/v1/publications/{citing.publication_id}/citations")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    resp = client.get(f"/api/v1/publications/{cited.publication_id}/cited-by")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["citing_publication_title"] == "The New Paper"


def test_add_external_citation(client, login_as, make_researcher, make_publication):
    author = make_researcher()
    citing = make_publication(author, title="Citing Paper")
    login_as(author.user)

    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={
        "external_title": "A Classic 1995 Paper", "external_authors": "Smith J, Doe A", "external_year": 1995,
    })
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["is_internal"] is False
    assert body["display_title"] == "A Classic 1995 Paper"
    assert body["cited_publication_id"] is None


def test_duplicate_internal_citation_is_rejected(client, login_as, make_researcher, make_publication):
    author = make_researcher()
    citing = make_publication(author, title="Citing Paper")
    cited = make_publication(author, title="Cited Paper")
    login_as(author.user)

    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={"cited_publication_id": cited.publication_id})
    assert resp.status_code == 201

    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={"cited_publication_id": cited.publication_id})
    assert resp.status_code == 409, resp.text


def test_two_different_external_citations_from_the_same_paper_are_both_allowed(client, login_as, make_researcher, make_publication):
    """The uniqueness constraint only applies to internal citations --
    external ones have no target publication_id to collide on."""
    author = make_researcher()
    citing = make_publication(author, title="Citing Paper")
    login_as(author.user)

    resp1 = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={"external_title": "Reference One"})
    resp2 = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={"external_title": "Reference Two"})
    assert resp1.status_code == 201
    assert resp2.status_code == 201


def test_only_primary_author_can_add_a_citation(client, login_as, make_researcher, make_publication):
    author = make_researcher(first_name="Owner")
    other = make_researcher(first_name="Not", last_name="TheOwner")
    citing = make_publication(author, title="Citing Paper")

    login_as(other.user)
    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={"external_title": "Sneaky Reference"})
    assert resp.status_code == 403, resp.text


def test_system_admin_without_a_profile_cannot_add_a_citation(client, login_as, make_researcher, make_publication, make_user):
    """Different from most admin-bypass cases in this app: added_by_id is
    real provenance (who's vouching for this reference), not just an audit
    stamp, and it's a NOT NULL FK -- there's no researcher identity to
    attribute the write to without a profile, so this is a deliberate,
    permanent 400, not a permission gap to fix."""
    author = make_researcher(first_name="Owner")
    citing = make_publication(author, title="Citing Paper")
    admin = make_user(role=UserRole.SYSTEM_ADMIN)

    login_as(admin)
    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={"external_title": "Admin-added Reference"})
    assert resp.status_code == 400, resp.text


def test_system_admin_can_delete_any_citation_even_without_a_profile(client, login_as, make_researcher, make_publication, make_user):
    """Unlike add, delete needs no attribution -- this one IS a full bypass."""
    author = make_researcher(first_name="Owner")
    citing = make_publication(author, title="Citing Paper")

    login_as(author.user)
    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={"external_title": "A Reference"})
    citation_id = resp.json()["citation_id"]

    admin = make_user(role=UserRole.SYSTEM_ADMIN)
    login_as(admin)
    resp = client.delete(f"/api/v1/citations/{citation_id}")
    assert resp.status_code == 204, resp.text


def test_only_the_citation_adder_or_citing_author_can_delete_it(client, login_as, make_researcher, make_publication):
    author = make_researcher(first_name="Owner")
    other = make_researcher(first_name="Not", last_name="TheOwner")
    citing = make_publication(author, title="Citing Paper")

    login_as(author.user)
    resp = client.post(f"/api/v1/publications/{citing.publication_id}/citations", json={"external_title": "A Reference"})
    citation_id = resp.json()["citation_id"]

    login_as(other.user)
    resp = client.delete(f"/api/v1/citations/{citation_id}")
    assert resp.status_code == 403, resp.text

    login_as(author.user)
    resp = client.delete(f"/api/v1/citations/{citation_id}")
    assert resp.status_code == 204, resp.text


def test_citation_text_generates_all_three_formats(client, login_as, make_researcher, make_publication):
    from datetime import date
    author = make_researcher(first_name="Ada", last_name="Lovelace")
    pub = make_publication(
        author, title="Notes on the Analytical Engine", venue_name="Scientific Memoirs",
        publication_date=date(1843, 1, 1), doi="10.1234/example",
    )
    login_as(author.user)

    resp = client.get(f"/api/v1/publications/{pub.publication_id}/citation-text")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    for style in ("apa", "mla", "bibtex"):
        assert style in body
        assert "Notes on the Analytical Engine" in body[style]
        assert "Lovelace" in body[style]
    assert "1843" in body["apa"]
    assert body["bibtex"].startswith("@")


def test_citations_are_scoped_to_the_correct_publication(client, login_as, make_researcher, make_publication):
    """A publication's reference list should never include another
    publication's citations, even if they share the same author."""
    author = make_researcher()
    paper_a = make_publication(author, title="Paper A")
    paper_b = make_publication(author, title="Paper B")
    other_target = make_publication(author, title="Some Target Paper")
    login_as(author.user)

    client.post(f"/api/v1/publications/{paper_a.publication_id}/citations", json={"cited_publication_id": other_target.publication_id})

    resp = client.get(f"/api/v1/publications/{paper_b.publication_id}/citations")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
