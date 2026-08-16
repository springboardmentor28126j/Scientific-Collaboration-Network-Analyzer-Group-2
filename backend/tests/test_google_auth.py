import unittest

from fastapi.testclient import TestClient

from app.main import app


class GoogleAuthTests(unittest.TestCase):
    def test_google_auth_invalid_token_returns_client_error(self):
        client = TestClient(app)

        response = client.post(
            "/api/v1/auth/google",
            json={"id_token": "not-a-real-token"},
        )

        self.assertIn(response.status_code, {400, 401})
        self.assertIn("detail", response.json())


if __name__ == "__main__":
    unittest.main()
