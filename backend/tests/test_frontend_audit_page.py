import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "frontend_app",
    Path(__file__).resolve().parents[2] / "frontend" / "app.py",
)
frontend_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frontend_app)

app = frontend_app.app


def test_audit_page_renders_for_system_admin(monkeypatch):
    class FakeResponse:
        def __init__(self, payload=None, status_code=200):
            self._payload = payload or {}
            self.status_code = status_code
            self.content = b""
            self.headers = {}

        def json(self):
            return self._payload

    def fake_get(url, *args, **kwargs):
        if url.endswith("/researchers/me"):
            return FakeResponse({
                "id": 1,
                "user": {"id": 1, "email": "admin@example.com", "role": "system_admin"},
            })
        if url.endswith("/audit-logs"):
            return FakeResponse({
                "items": [{
                    "id": 7,
                    "actor_user_id": 1,
                    "actor_email": "admin@example.com",
                    "action": "user_login",
                    "entity_type": "user",
                    "entity_id": 1,
                    "details": "login succeeded",
                    "created_at": "2026-08-17T09:00:00",
                }],
                "total": 1,
                "page": 1,
                "page_size": 25,
            })
        if url.endswith("/audit-logs/actions"):
            return FakeResponse(["user_login"])
        if url.endswith("/notifications/unread-count"):
            return FakeResponse({"unread_count": 0})
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(frontend_app.requests, "get", fake_get)

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["token"] = "abc"
            sess["email"] = "admin@example.com"

        response = client.get("/audit")

        assert response.status_code == 200
        assert b"Audit Logs" in response.data
        assert b"user_login" in response.data
