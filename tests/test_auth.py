from tests.conftest import extract_token
from tests.test_institutions import register_institution


async def _register_and_verify_admin(client, email_mocks, email="admin@acme.edu"):
    await register_institution(client, email=email)
    link = email_mocks["institution"].call_args.args[2]
    token = extract_token(link)
    await client.post("/api/v1/auth/verify-email", json={"token": token})


async def test_login_with_wrong_password_returns_401(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)

    response = await client.post(
        "/api/v1/auth/login", data={"username": "admin@acme.edu", "password": "WrongPass1"}
    )
    assert response.status_code == 401


async def test_refresh_token_issues_new_access_token(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)

    login = await client.post(
        "/api/v1/auth/login", data={"username": "admin@acme.edu", "password": "StrongPass123"}
    )
    refresh_token = login.json()["refresh_token"]

    refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    assert "access_token" in refreshed.json()


async def test_me_endpoint_requires_bearer_token(client, email_mocks):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_endpoint_returns_current_user(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)
    login = await client.post(
        "/api/v1/auth/login", data={"username": "admin@acme.edu", "password": "StrongPass123"}
    )
    access_token = login.json()["access_token"]

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "admin@acme.edu"
    assert me.json()["role"] == "INSTITUTION_ADMIN"


async def test_forgot_password_always_returns_generic_message(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)

    known = await client.post("/api/v1/auth/forgot-password", json={"email": "admin@acme.edu"})
    unknown = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "nobody@nowhere.com"}
    )

    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json()["detail"] == unknown.json()["detail"]
    email_mocks["reset"].assert_awaited_once()  # only for the real account


async def test_reset_password_with_valid_token_allows_new_login(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)
    await client.post("/api/v1/auth/forgot-password", json={"email": "admin@acme.edu"})

    link = email_mocks["reset"].call_args.args[2]
    token = extract_token(link)

    reset = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "NewStrongPass1"}
    )
    assert reset.status_code == 200

    old_login = await client.post(
        "/api/v1/auth/login", data={"username": "admin@acme.edu", "password": "StrongPass123"}
    )
    assert old_login.status_code == 401

    new_login = await client.post(
        "/api/v1/auth/login", data={"username": "admin@acme.edu", "password": "NewStrongPass1"}
    )
    assert new_login.status_code == 200


async def test_reset_password_token_is_single_use(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)
    await client.post("/api/v1/auth/forgot-password", json={"email": "admin@acme.edu"})
    link = email_mocks["reset"].call_args.args[2]
    token = extract_token(link)

    first = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "NewStrongPass1"}
    )
    assert first.status_code == 200

    second = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "AnotherPass2"}
    )
    assert second.status_code == 400
