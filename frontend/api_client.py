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


def register(
    email: str,
    password: str,
    role: str,
    institution_id: int | None = None,
    institution_name: str | None = None,
    website: str | None = None,
    domain: str | None = None,
    address: str | None = None,
    official_email: str | None = None,
) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/auth/register", json={
        "email": email,
        "password": password,
        "role": role,
        "institution_id": institution_id,
        "institution_name": institution_name,
        "website": website,
        "domain": domain,
        "address": address,
        "official_email": official_email,
    })
    return _handle(resp)


def login(email: str, password: str, recaptcha_token: str | None = None) -> dict:
    data = {"username": email, "password": password}
    if recaptcha_token:
        data["recaptcha_token"] = recaptcha_token
    resp = requests.post(f"{BACKEND_API_URL}/auth/login", data=data)
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


def set_my_institution(access_token: str, institution_id: int) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/users/me/institution", json={"institution_id": institution_id},
        headers=_auth_header(access_token),
    )
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


def list_publications(access_token: str, page: int = 1, page_size: int = 10, institution_id: int | None = None,
                       mine: bool = False, author_id: int | None = None, year: int | None = None,
                       q: str | None = None, sort_by: str = "date", sort_dir: str = "desc") -> dict:
    params = {"page": page, "page_size": page_size, "sort_by": sort_by, "sort_dir": sort_dir}
    if institution_id:
        params["institution_id"] = institution_id
    if mine:
        params["mine"] = "true"
    if author_id:
        params["author_id"] = author_id
    if year:
        params["year"] = year
    if q:
        params["q"] = q
    resp = requests.get(
        f"{BACKEND_API_URL}/publications",
        params=params,
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


def list_conferences(access_token: str, page: int = 1, page_size: int = 10, mine: bool = False,
                      institution_id: int | None = None, author_id: int | None = None, year: int | None = None,
                      q: str | None = None, sort_by: str = "date", sort_dir: str = "desc") -> dict:
    params = {"page": page, "page_size": page_size, "sort_by": sort_by, "sort_dir": sort_dir}
    if mine:
        params["mine"] = "true"
    if institution_id:
        params["institution_id"] = institution_id
    if author_id:
        params["author_id"] = author_id
    if year:
        params["year"] = year
    if q:
        params["q"] = q
    resp = requests.get(f"{BACKEND_API_URL}/conferences", params=params, headers=_auth_header(access_token))
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


def delete_conference(access_token: str, conference_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/conferences/{conference_id}", headers=_auth_header(access_token))
    _handle(resp)


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

# --- Add this function to frontend/api_client.py, near update_publication ---

def update_publication_status(access_token: str, publication_id: int, new_status: str) -> dict:
    resp = requests.patch(
        f"{BACKEND_API_URL}/publications/{publication_id}/status",
        json={"status": new_status},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


# --- Admin (System Admin only) ---

def get_dashboard_stats(access_token: str) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/admin/dashboard-stats", headers=_auth_header(access_token))
    return _handle(resp)


def list_audit_logs(access_token: str, page: int = 1, page_size: int = 25, entity_type: str | None = None,
                     action: str | None = None) -> dict:
    params = {"page": page, "page_size": page_size}
    if entity_type:
        params["entity_type"] = entity_type
    if action:
        params["action"] = action
    resp = requests.get(f"{BACKEND_API_URL}/admin/audit-logs", params=params, headers=_auth_header(access_token))
    return _handle(resp)


def list_settings(access_token: str) -> list:
    resp = requests.get(f"{BACKEND_API_URL}/admin/settings", headers=_auth_header(access_token))
    return _handle(resp)


def list_institution_requests(access_token: str) -> list:
    resp = requests.get(f"{BACKEND_API_URL}/institutions/requests", headers=_auth_header(access_token))
    return _handle(resp)


def approve_institution_request(access_token: str, request_id: int) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/institutions/requests/{request_id}/approve",
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def reject_institution_request(access_token: str, request_id: int) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/institutions/requests/{request_id}/reject",
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def update_setting(access_token: str, key: str, value: str, description: str | None = None) -> dict:
    resp = requests.put(
        f"{BACKEND_API_URL}/admin/settings/{key}",
        json={"value": value, "description": description},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def list_all_users(access_token: str, institution_id: int | None = None, role: str | None = None,
                    affiliation_status: str | None = None, page: int = 1, page_size: int = 20) -> list:
    params = {"page": page, "page_size": page_size}
    if institution_id:
        params["institution_id"] = institution_id
    if role:
        params["role"] = role
    if affiliation_status:
        params["affiliation_status"] = affiliation_status
    resp = requests.get(f"{BACKEND_API_URL}/users", params=params, headers=_auth_header(access_token))
    return _handle(resp)


def approve_affiliation(access_token: str, user_id: int) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/users/{user_id}/approve-affiliation", headers=_auth_header(access_token))
    return _handle(resp)


def reject_affiliation(access_token: str, user_id: int) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/users/{user_id}/reject-affiliation", headers=_auth_header(access_token))
    return _handle(resp)


def get_institution_stats(access_token: str, institution_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/institutions/{institution_id}/stats", headers=_auth_header(access_token))
    return _handle(resp)


# --- Reviews ---

def assign_review(access_token: str, target_type: str, target_id: int, reviewer_id: int) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/reviews",
        json={"target_type": target_type, "target_id": target_id, "reviewer_id": reviewer_id},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def list_my_reviews(access_token: str, status: str | None = None, target_type: str | None = None) -> list:
    params = {}
    if status:
        params["status"] = status
    if target_type:
        params["target_type"] = target_type
    resp = requests.get(f"{BACKEND_API_URL}/reviews/mine", params=params, headers=_auth_header(access_token))
    return _handle(resp)


def get_review(access_token: str, review_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/reviews/{review_id}", headers=_auth_header(access_token))
    return _handle(resp)


def list_reviews_for_target(access_token: str, target_type: str, target_id: int) -> list:
    resp = requests.get(
        f"{BACKEND_API_URL}/reviews",
        params={"target_type": target_type, "target_id": target_id},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def accept_review(access_token: str, review_id: int) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/reviews/{review_id}/accept", headers=_auth_header(access_token))
    return _handle(resp)


def decline_review(access_token: str, review_id: int) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/reviews/{review_id}/decline", headers=_auth_header(access_token))
    return _handle(resp)


def submit_review(access_token: str, review_id: int, score: int | None, comments: str | None, recommendation: str) -> dict:
    resp = requests.patch(
        f"{BACKEND_API_URL}/reviews/{review_id}/submit",
        json={"score": score, "comments": comments, "recommendation": recommendation},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


# --- Projects ---

def create_project(access_token: str, data: dict) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/projects", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def list_projects(access_token: str, mine: bool = False, institution_id: int | None = None,
                   status: str | None = None) -> list:
    params = {}
    if mine:
        params["mine"] = "true"
    if institution_id:
        params["institution_id"] = institution_id
    if status:
        params["status"] = status
    resp = requests.get(f"{BACKEND_API_URL}/projects", params=params, headers=_auth_header(access_token))
    return _handle(resp)


def get_project(access_token: str, project_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/projects/{project_id}", headers=_auth_header(access_token))
    return _handle(resp)


def update_project(access_token: str, project_id: int, data: dict) -> dict:
    resp = requests.patch(f"{BACKEND_API_URL}/projects/{project_id}", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def delete_project(access_token: str, project_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/projects/{project_id}", headers=_auth_header(access_token))
    _handle(resp)


def list_project_members(access_token: str, project_id: int) -> list:
    resp = requests.get(f"{BACKEND_API_URL}/projects/{project_id}/members", headers=_auth_header(access_token))
    return _handle(resp)


def add_project_member(access_token: str, project_id: int, researcher_id: int) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/projects/{project_id}/members",
        json={"researcher_id": researcher_id},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def remove_project_member(access_token: str, project_id: int, researcher_id: int) -> None:
    resp = requests.delete(
        f"{BACKEND_API_URL}/projects/{project_id}/members/{researcher_id}", headers=_auth_header(access_token)
    )
    _handle(resp)

def respond_to_project_invitation(access_token: str, project_id: int, project_member_id: int, accept: bool) -> dict:
    resp = requests.patch(
        f"{BACKEND_API_URL}/projects/{project_id}/members/{project_member_id}/respond",
        json={"accept": accept}, headers=_auth_header(access_token),
    )
    return _handle(resp)


def list_pending_project_invitations(access_token: str) -> list:
    resp = requests.get(f"{BACKEND_API_URL}/projects/invitations/pending", headers=_auth_header(access_token))
    return _handle(resp)


def send_project_message(access_token: str, project_id: int, body: str) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/projects/{project_id}/messages", json={"body": body}, headers=_auth_header(access_token)
    )
    return _handle(resp)


def list_project_messages(access_token: str, project_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/projects/{project_id}/messages", headers=_auth_header(access_token))
    return _handle(resp)


# --- Notifications ---

def list_notifications(access_token: str, unread_only: bool = False, page: int = 1, page_size: int = 20) -> dict:
    params = {"page": page, "page_size": page_size}
    if unread_only:
        params["unread_only"] = "true"
    resp = requests.get(f"{BACKEND_API_URL}/notifications", params=params, headers=_auth_header(access_token))
    return _handle(resp)


def get_unread_notification_count(access_token: str) -> int:
    resp = requests.get(f"{BACKEND_API_URL}/notifications/unread-count", headers=_auth_header(access_token))
    return _handle(resp)["unread_count"]


def mark_notification_read(access_token: str, notification_id: int) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/notifications/{notification_id}/read", headers=_auth_header(access_token))
    return _handle(resp)


def mark_all_notifications_read(access_token: str) -> None:
    resp = requests.post(f"{BACKEND_API_URL}/notifications/mark-all-read", headers=_auth_header(access_token))
    _handle(resp)


def delete_notification(access_token: str, notification_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/notifications/{notification_id}", headers=_auth_header(access_token))
    _handle(resp)


def get_user(access_token: str, user_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/users/{user_id}", headers=_auth_header(access_token))
    return _handle(resp)


def admin_update_user(access_token: str, user_id: int, data: dict) -> dict:
    resp = requests.patch(f"{BACKEND_API_URL}/users/{user_id}", json=data, headers=_auth_header(access_token))
    return _handle(resp)


def deactivate_user(access_token: str, user_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/users/{user_id}", headers=_auth_header(access_token))
    _handle(resp)


# --- Collaborations ---

def send_collaboration_request(access_token: str, addressee_researcher_id: int, message: str | None = None) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/collaboration-request",
        json={"addressee_researcher_id": addressee_researcher_id, "message": message},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def list_collaboration_requests(access_token: str, direction: str | None = None, status_filter: str | None = None) -> dict:
    params = {}
    if direction:
        params["direction"] = direction
    if status_filter:
        params["status"] = status_filter
    resp = requests.get(f"{BACKEND_API_URL}/collaboration-requests", params=params, headers=_auth_header(access_token))
    return _handle(resp)


def respond_to_collaboration_request(access_token: str, collaboration_request_id: int, new_status: str) -> dict:
    resp = requests.patch(
        f"{BACKEND_API_URL}/collaboration-request/{collaboration_request_id}",
        json={"status": new_status},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def list_my_collaborations(access_token: str, page: int = 1, page_size: int = 10) -> dict:
    resp = requests.get(
        f"{BACKEND_API_URL}/collaborations/my",
        params={"page": page, "page_size": page_size},
        headers=_auth_header(access_token),
    )
    return _handle(resp)


def get_collaboration(access_token: str, collaboration_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/collaborations/{collaboration_id}", headers=_auth_header(access_token))
    return _handle(resp)


def get_collaboration_network(access_token: str, depth: int = 2) -> dict:
    resp = requests.get(
        f"{BACKEND_API_URL}/collaborations/network", params={"depth": depth}, headers=_auth_header(access_token)
    )
    return _handle(resp)


def list_suggested_collaborators(access_token: str, limit: int = 10) -> list:
    resp = requests.get(
        f"{BACKEND_API_URL}/collaborations/suggested", params={"limit": limit}, headers=_auth_header(access_token)
    )
    return _handle(resp)


# --- Messages ---
def send_message(access_token: str, collaboration_id: int, body: str) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/collaborations/{collaboration_id}/messages",
        json={"body": body}, headers=_auth_header(access_token),
    )
    return _handle(resp)


def list_messages(access_token: str, collaboration_id: int) -> dict:
    resp = requests.get(
        f"{BACKEND_API_URL}/collaborations/{collaboration_id}/messages", headers=_auth_header(access_token)
    )
    return _handle(resp)

def get_unread_message_count(access_token: str) -> int:
    resp = requests.get(f"{BACKEND_API_URL}/messages/unread-count", headers=_auth_header(access_token))
    return _handle(resp)["unread_count"]


# --- Citations ---
def add_citation(access_token: str, publication_id: int, data: dict) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/publications/{publication_id}/citations", json=data, headers=_auth_header(access_token)
    )
    return _handle(resp)


def list_publication_references(access_token: str, publication_id: int) -> dict:
    resp = requests.get(
        f"{BACKEND_API_URL}/publications/{publication_id}/citations", headers=_auth_header(access_token)
    )
    return _handle(resp)


def list_publication_cited_by(access_token: str, publication_id: int) -> dict:
    resp = requests.get(
        f"{BACKEND_API_URL}/publications/{publication_id}/cited-by", headers=_auth_header(access_token)
    )
    return _handle(resp)


def get_citation_text(access_token: str, publication_id: int) -> dict:
    resp = requests.get(
        f"{BACKEND_API_URL}/publications/{publication_id}/citation-text", headers=_auth_header(access_token)
    )
    return _handle(resp)


def delete_citation(access_token: str, citation_id: int) -> None:
    resp = requests.delete(f"{BACKEND_API_URL}/citations/{citation_id}", headers=_auth_header(access_token))
    _handle(resp)

# --- Backend reports API ---

def get_researcher_report(access_token: str) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/reports/researcher", headers=_auth_header(access_token))
    return _handle(resp)


def get_institution_report(access_token: str, institution_id: int) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/reports/institution/{institution_id}", headers=_auth_header(access_token))
    return _handle(resp)


def get_publications_report(access_token: str, mine: bool = False, year: int | None = None) -> dict:
    params = {"mine": mine}
    if year:
        params["year"] = year
    resp = requests.get(f"{BACKEND_API_URL}/reports/publications", params=params, headers=_auth_header(access_token))
    return _handle(resp)


def get_projects_report(access_token: str, mine: bool = False) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/reports/projects", params={"mine": mine}, headers=_auth_header(access_token))
    return _handle(resp)


def get_conferences_report(access_token: str, mine: bool = False) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/reports/conferences", params={"mine": mine}, headers=_auth_header(access_token))
    return _handle(resp)


def get_reviews_report(access_token: str) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/reports/reviews", headers=_auth_header(access_token))
    return _handle(resp)


def get_collaborations_report(access_token: str) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/reports/collaborations", headers=_auth_header(access_token))
    return _handle(resp)


def get_system_report(access_token: str) -> dict:
    resp = requests.get(f"{BACKEND_API_URL}/reports/system", headers=_auth_header(access_token))
    return _handle(resp)


def get_citation_analytics(access_token: str, limit: int = 10) -> dict:
    resp = requests.get(
        f"{BACKEND_API_URL}/analytics", params={"limit": limit}, headers=_auth_header(access_token)
    )
    return _handle(resp)

def forgot_password(email: str) -> dict:
    resp = requests.post(f"{BACKEND_API_URL}/auth/forgot-password", json={"email": email})
    return _handle(resp)


def reset_password(token: str, new_password: str) -> dict:
    resp = requests.post(
        f"{BACKEND_API_URL}/auth/reset-password", json={"token": token, "new_password": new_password}
    )
    return _handle(resp)


def send_chat_message(access_token: str, messages: list) -> dict:
    """messages: [{"role": "user"|"assistant", "content": str}, ...], oldest
    first -- the whole conversation so far. Returns {"reply": str}."""
    resp = requests.post(
        f"{BACKEND_API_URL}/chatbot/message", json={"messages": messages}, headers=_auth_header(access_token)
    )
    return _handle(resp)