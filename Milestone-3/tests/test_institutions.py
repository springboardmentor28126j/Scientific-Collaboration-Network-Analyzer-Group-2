from tests.conftest import extract_token


async def register_institution(client, email="admin@acme-university.edu"):
    files = {"logo": ("logo.png", b"fake-image-bytes", "image/png")}
    data = {
        "name": "Acme University",
        "address": "123 Research Way, Springfield",
        "admin_full_name": "Ada Lovelace",
        "admin_email": email,
        "admin_password": "StrongPass123",
    }
    return await client.post("/api/v1/institutions/register", data=data, files=files)


async def test_register_institution_creates_inactive_admin(client, email_mocks):
    response = await register_institution(client)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Acme University"
    assert body["is_active"] is True  # institution itself defaults active
    assert body["logo_url"] == "https://cdn.example.com/logo.png"

    email_mocks["institution"].assert_awaited_once()

    # Admin can't log in yet — unverified.
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@acme-university.edu", "password": "StrongPass123"},
    )
    assert login.status_code == 403


async def test_duplicate_admin_email_rejected(client, email_mocks):
    first = await register_institution(client)
    assert first.status_code == 201

    second = await register_institution(client)
    assert second.status_code == 409


async def test_verify_email_activates_admin_and_allows_login(client, email_mocks):
    await register_institution(client)

    link = email_mocks["institution"].call_args.args[2]
    token = extract_token(link)

    verify = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verify.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@acme-university.edu", "password": "StrongPass123"},
    )
    assert login.status_code == 200
    body = login.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_verify_email_token_is_single_use(client, email_mocks):
    await register_institution(client)
    link = email_mocks["institution"].call_args.args[2]
    token = extract_token(link)

    first = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert first.status_code == 200

    second = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert second.status_code == 400


async def test_weak_password_rejected_at_registration(client, email_mocks):
    files = {"logo": ("logo.png", b"fake-image-bytes", "image/png")}
    data = {
        "name": "Acme University",
        "address": "123 Research Way",
        "admin_full_name": "Ada Lovelace",
        "admin_email": "admin@weakpass.edu",
        "admin_password": "short",
    }
    response = await client.post("/api/v1/institutions/register", data=data, files=files)
    assert response.status_code == 422
