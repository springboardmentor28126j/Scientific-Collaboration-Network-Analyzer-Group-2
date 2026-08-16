import unittest

from fastapi.testclient import TestClient

from app.main import app


class InstitutionRequestRegistrationTests(unittest.TestCase):
    def test_institution_admin_registration_without_institution_creates_request(self):
        client = TestClient(app)

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new-institution-admin@example.com",
                "password": "Password123!",
                "role": "institution_admin",
                "institution_id": None,
                "institution_name": "Example University",
                "website": "https://example.edu",
                "domain": "example.edu",
                "address": "123 Example Street",
                "official_email": "admin@example.edu",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(body["affiliation_status"], "pending")
        # Institution Admin applications can't log in until a System Admin
        # approves them, even when a brand-new institution is being requested.
        self.assertFalse(body["is_active"])

    def test_system_admin_role_is_rejected_on_registration(self):
        client = TestClient(app)

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "wannabe-admin@example.com",
                "password": "Password123!",
                "role": "system_admin",
            },
        )

        # System Admin accounts may only be created by inserting directly
        # into PostgreSQL -- there is no self-service registration path.
        self.assertEqual(response.status_code, 400, response.text)

    def test_independent_reviewer_registration_succeeds_without_institution(self):
        client = TestClient(app)

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "independent-reviewer@example.com",
                "password": "Password123!",
                "role": "reviewer",
                "institution_id": None,
            },
        )

        # Reviewers, like researchers, must be allowed to register without
        # picking an institution at all (an "Independent Reviewer").
        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertIsNone(body["institution_id"])
        self.assertEqual(body["affiliation_status"], "not_applicable")

    def test_institutional_reviewer_with_personal_email_is_rejected(self):
        client = TestClient(app)

        # Pick up whatever institution exists with a configured email domain
        # (seeded/previously-created data) and try to register a reviewer
        # against it using an obviously-personal email address.
        institutions = client.get("/api/v1/institutions").json()
        domain_institution = next((i for i in institutions if i.get("email_domain")), None)
        if domain_institution is None:
            self.skipTest("No institution with a configured email_domain is available to test against")

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "someone@gmail.com",
                "password": "Password123!",
                "role": "reviewer",
                "institution_id": domain_institution["institution_id"],
            },
        )

        # BR: institutional researcher/reviewer accounts are only accepted
        # with the institution's official email -- a personal email must be
        # rejected outright, not silently queued as pending.
        self.assertEqual(response.status_code, 400, response.text)


if __name__ == "__main__":
    unittest.main()
