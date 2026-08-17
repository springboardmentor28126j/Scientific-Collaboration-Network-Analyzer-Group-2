from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_assistant_chat_endpoint_exists():
    response = client.post(
        "/assistant/chat",
        json={"message": "Where do I add a publication?", "history": []},
    )
    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert "configured" in body
