from tests.conftest import extract_token
from tests.test_institutions import register_institution


async def _register_and_verify_admin(client, email_mocks, email="admin@acme.edu"):
    await register_institution(client, email=email)
    link = email_mocks["institution"].call_args.args[2]
    token = extract_token(link)
    await client.post("/api/v1/auth/verify-email", json={"token": token})


async def _login(client, email, password):
    response = await client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    return response.json()["access_token"]


async def test_institution_admin_can_create_researcher(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)
    token = await _login(client, "admin@acme.edu", "StrongPass123")

    response = await client.post(
        "/api/v1/institution/users",
        json={
            "email": "researcher@acme.edu",
            "full_name": "Marie Curie",
            "role": "RESEARCHER",
            "description": "Physics dept, radioactivity research",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "RESEARCHER"
    assert body["is_verified"] is False
    assert body["is_active"] is False
    email_mocks["invite"].assert_awaited_once()


async def test_researcher_cannot_log_in_before_invite_verified(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)
    admin_token = await _login(client, "admin@acme.edu", "StrongPass123")

    await client.post(
        "/api/v1/institution/users",
        json={"email": "researcher@acme.edu", "full_name": "Marie Curie", "role": "RESEARCHER"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "researcher@acme.edu", "password": "anything"},
    )
    assert login.status_code == 401  # no password set yet — placeholder hash never matches


async def test_verify_invite_sets_password_and_activates(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)
    admin_token = await _login(client, "admin@acme.edu", "StrongPass123")

    await client.post(
        "/api/v1/institution/users",
        json={"email": "reviewer@acme.edu", "full_name": "Alan Turing", "role": "REVIEWER"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    link = email_mocks["invite"].call_args.args[4]
    token = extract_token(link)

    verify = await client.post(
        "/api/v1/auth/verify-invite", json={"token": token, "password": "ReviewerPass1"}
    )
    assert verify.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "reviewer@acme.edu", "password": "ReviewerPass1"},
    )
    assert login.status_code == 200


async def test_forgot_password_works_for_verified_researcher(client, email_mocks):
    """Confirms researchers/reviewers can use forgot-password once
    verified, same as an institution admin — not gated by role."""
    await _register_and_verify_admin(client, email_mocks)
    admin_token = await _login(client, "admin@acme.edu", "StrongPass123")

    await client.post(
        "/api/v1/institution/users",
        json={"email": "researcher@acme.edu", "full_name": "Marie Curie", "role": "RESEARCHER"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    invite_link = email_mocks["invite"].call_args.args[4]
    invite_token = extract_token(invite_link)
    await client.post(
        "/api/v1/auth/verify-invite",
        json={"token": invite_token, "password": "ResearcherPass1"},
    )

    forgot = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "researcher@acme.edu"}
    )
    assert forgot.status_code == 200
    email_mocks["reset"].assert_awaited_once()

    reset_link = email_mocks["reset"].call_args.args[2]
    reset_token = extract_token(reset_link)
    reset = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "BrandNewPass1"},
    )
    assert reset.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "researcher@acme.edu", "password": "BrandNewPass1"},
    )
    assert login.status_code == 200


async def test_institution_admin_can_deactivate_and_reactivate_researcher(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks)
    admin_token = await _login(client, "admin@acme.edu", "StrongPass123")

    created = await client.post(
        "/api/v1/institution/users",
        json={"email": "researcher@acme.edu", "full_name": "Marie Curie", "role": "RESEARCHER"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    user_id = created.json()["id"]

    invite_link = email_mocks["invite"].call_args.args[4]
    invite_token = extract_token(invite_link)
    await client.post(
        "/api/v1/auth/verify-invite",
        json={"token": invite_token, "password": "ResearcherPass1"},
    )

    deactivate = await client.patch(
        f"/api/v1/institution/users/{user_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False

    login_blocked = await client.post(
        "/api/v1/auth/login",
        data={"username": "researcher@acme.edu", "password": "ResearcherPass1"},
    )
    assert login_blocked.status_code == 403

    reactivate = await client.patch(
        f"/api/v1/institution/users/{user_id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert reactivate.status_code == 200

    login_ok = await client.post(
        "/api/v1/auth/login",
        data={"username": "researcher@acme.edu", "password": "ResearcherPass1"},
    )
    assert login_ok.status_code == 200


async def test_researcher_cannot_create_other_users(client, email_mocks):
    """A researcher (non-admin role) must be forbidden from the
    institution-admin-only user management endpoints."""
    await _register_and_verify_admin(client, email_mocks)
    admin_token = await _login(client, "admin@acme.edu", "StrongPass123")

    await client.post(
        "/api/v1/institution/users",
        json={"email": "researcher@acme.edu", "full_name": "Marie Curie", "role": "RESEARCHER"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    invite_link = email_mocks["invite"].call_args.args[4]
    invite_token = extract_token(invite_link)
    await client.post(
        "/api/v1/auth/verify-invite",
        json={"token": invite_token, "password": "ResearcherPass1"},
    )
    researcher_token = await _login(client, "researcher@acme.edu", "ResearcherPass1")

    response = await client.post(
        "/api/v1/institution/users",
        json={"email": "someone@acme.edu", "full_name": "Nobody", "role": "REVIEWER"},
        headers={"Authorization": f"Bearer {researcher_token}"},
    )
    assert response.status_code == 403


async def test_institution_admin_cannot_be_deactivated_via_institution_user_endpoint(
    client, email_mocks
):
    """Superuser-only authority, per docs/architecture.md §5.7 — an
    institution admin can't be deactivated through the researcher/
    reviewer-facing endpoint, even by themselves."""
    await _register_and_verify_admin(client, email_mocks)
    admin_token = await _login(client, "admin@acme.edu", "StrongPass123")

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    admin_id = me.json()["id"]

    response = await client.patch(
        f"/api/v1/institution/users/{admin_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 403


async def test_institution_admin_only_sees_own_institution_users(client, email_mocks):
    await _register_and_verify_admin(client, email_mocks, email="admin-a@uni-a.edu")
    await _register_and_verify_admin(client, email_mocks, email="admin-b@uni-b.edu")

    token_a = await _login(client, "admin-a@uni-a.edu", "StrongPass123")
    token_b = await _login(client, "admin-b@uni-b.edu", "StrongPass123")

    await client.post(
        "/api/v1/institution/users",
        json={"email": "researcher-a@uni-a.edu", "full_name": "A", "role": "RESEARCHER"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    await client.post(
        "/api/v1/institution/users",
        json={"email": "researcher-b@uni-b.edu", "full_name": "B", "role": "RESEARCHER"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    list_a = await client.get(
        "/api/v1/institution/users", headers={"Authorization": f"Bearer {token_a}"}
    )
    emails_a = {u["email"] for u in list_a.json()}
    assert emails_a == {"researcher-a@uni-a.edu"}
