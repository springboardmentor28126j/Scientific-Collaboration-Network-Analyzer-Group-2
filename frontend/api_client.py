"""
Thin wrapper around the FastAPI backend's REST API.

The Flask app never talks to the database directly -- it is a pure client of
the FastAPI service, matching the architecture's separation between the
Python application layer (FastAPI, JSON API) and the client (Flask, HTML).
"""
import requests

from config import BACKEND_API_URL


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _handle(resp: requests.Response):
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise ApiError(resp.status_code, detail)
    if resp.status_code == 204:
        return None
    return resp.json()


def register(email: str, password: str, role: str, institution_id: int | None = None) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/auth/register", json={
        "email": email, "password": password, "role": role, "institution_id": institution_id,
    })
    return _handle(resp)


def login(email: str, password: str) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/auth/login",
        data={"username": email, "password": password},
    )
    return _handle(resp)


def check_email_deliverability(email: str) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/auth/check-email-deliverability", json={"email": email})
    return _handle(resp)


def verify_email(token: str) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/auth/verify-email", params={"token": token})
    return _handle(resp)


def resend_verification(email: str) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/auth/resend-verification", json={"email": email})
    return _handle(resp)


def get_my_account(access_token: str) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/users/me", headers=_auth_header(access_token))
    return _handle(resp)


def get_my_researcher_profile(access_token: str) -> dict | None:
    resp = requests.get(f"{BACKEND_API_URL}/researchers/me", headers=_auth_header(access_token))
    if resp.status_code == 404:
        return None
    return _handle(resp)


def create_researcher_profile(access_token: str, data: dict) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/researchers", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def update_researcher_profile(access_token: str, data: dict) -> dict:
    resp = requests.patch(f"{BACKEND_API_URL}/researchers/me", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def add_skill(access_token: str, name: str) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/researchers/me/skills", json={"name": name},
                          headers=_auth_header(access_token))
    return _handle(resp)


def remove_skill(access_token: str, skill_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/researchers/me/skills/{skill_id}",
                            headers=_auth_header(access_token))
    return _handle(resp)


def add_interest(access_token: str, name: str) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/researchers/me/interests", json={"name": name},
                          headers=_auth_header(access_token))
    return _handle(resp)


def remove_interest(access_token: str, interest_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/researchers/me/interests/{interest_id}",
                            headers=_auth_header(access_token))
    return _handle(resp)


def search_researchers(access_token: str, skill: str | None = None, interest: str | None = None) -> list[dict]:
    params = {}
    if skill:
        params["skill"] = skill
    if interest:
        params["interest"] = interest
    resp = requests.get(f"{BACKEND_API_URL}/researchers", params=params, headers=_auth_header(access_token))
    return _handle(resp)


def _auth_header(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


def list_publications(access_token: str, page: int = 1, page_size: int = 10) -> dict:
    resp = requests.get(
        f"{BACKEND_API_URL}/publications",
        params={"page": page, "page_size": page_size},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def upload_publication_file(access_token: str, publication_id: int, file_storage) -> dict:
    files = {"file": (file_storage.filename, file_storage.stream, file_storage.mimetype)}
    resp = requests.post(
        f"{BACKEND_API_URL}/publications/{publication_id}/upload",
        files=files,
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def get_publication(access_token: str, publication_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/publications/{publication_id}", headers=_auth_header(access_token))
    return _handle(resp)


def create_publication(access_token: str, data: dict) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/publications", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def update_publication(access_token: str, publication_id: int, data: dict) -> dict:
    resp = requests.patch(f"{BACKEND_API_URL}/publications/{publication_id}", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def delete_publication(access_token: str, publication_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/publications/{publication_id}", headers=_auth_header(access_token))
    _handle(resp)


def list_conferences(access_token: str) -> list:
    resp = requests.get(f"{BACKEND_API_URL}/conferences", headers=_auth_header(access_token))
    return _handle(resp)


def get_conference(access_token: str, conference_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/conferences/{conference_id}", headers=_auth_header(access_token))
    return _handle(resp)


def create_conference(access_token: str, data: dict) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/conferences", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def update_conference(access_token: str, conference_id: int, data: dict) -> dict:
    resp = requests.patch(f"{BACKEND_API_URL}/conferences/{conference_id}", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def list_conference_participants(access_token: str, conference_id: int) -> list:
    resp = requests.get(f"{BACKEND_API_URL}/conferences/{conference_id}/participants", headers=_auth_header(access_token))
    return _handle(resp)


def register_for_conference(access_token: str, conference_id: int, data: dict) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/conferences/{conference_id}/register", json=data, headers=_auth_header(access_token)
    )
    return _handle(resp)


def update_conference_participation(access_token: str, conference_id: int, participation_id: int, data: dict) -> dict:
    resp = requests.patch(
        f"{BACKEND_API_URL}/conferences/{conference_id}/participants/{participation_id}",
        json=data,
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def cancel_conference_participation(access_token: str, conference_id: int, participation_id: int) -> None:
    resp = requests.delete(
        f"{BACKEND_API_URL}/conferences/{conference_id}/participants/{participation_id}",
        headers=_auth_header(access_token),
    )
    _handle(resp)


def list_institutions(access_token: str | None = None) -> list:
    headers = _auth_header(access_token) if access_token else {}
    resp = requests.get(f"{BACKEND_API_URL}/institutions", headers=headers)
    return _handle(resp)


def get_institution(access_token: str, institution_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/institutions/{institution_id}", headers=_auth_header(access_token))
    return _handle(resp)


def create_institution(access_token: str, data: dict) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/institutions", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def update_institution(access_token: str, institution_id: int, data: dict) -> dict:
    resp = requests.patch(f"{BACKEND_API_URL}/institutions/{institution_id}", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def delete_institution(access_token: str, institution_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/institutions/{institution_id}", headers=_auth_header(access_token))
    _handle(resp)


def list_departments(access_token: str, institution_id: int) -> list:
    resp = requests.get(f"{BACKEND_API_URL}/institutions/{institution_id}/departments", headers=_auth_header(access_token))
    return _handle(resp)


def create_department(access_token: str, institution_id: int, data: dict) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/institutions/{institution_id}/departments", json=data, headers=_auth_header(access_token)
    )
    return _handle(resp)


def delete_department(access_token: str, institution_id: int, department_id: int) -> None:
    resp = requests.delete(
        f"{BACKEND_API_URL}/institutions/{institution_id}/departments/{department_id}",
        headers=_auth_header(access_token),
    )
    _handle(resp)
