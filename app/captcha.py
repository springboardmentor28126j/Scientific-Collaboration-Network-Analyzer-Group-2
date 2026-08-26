"""Short-lived, server-validated CAPTCHA challenges for sign-in.

This deliberately has no external dependency.  In a multi-server production
deployment the store should be moved to Redis; for the single application
container used by this project an in-memory store is reliable and simple.
"""
from datetime import datetime, timedelta, timezone
import secrets
import threading

_challenges: dict[str, dict] = {}
_lock = threading.Lock()
_TTL = timedelta(minutes=5)


def create_challenge() -> dict:
    left, right = secrets.randbelow(9) + 1, secrets.randbelow(9) + 1
    token = secrets.token_urlsafe(24)
    with _lock:
        _cleanup()
        _challenges[token] = {
            "answer": str(left + right),
            "expires_at": datetime.now(timezone.utc) + _TTL,
            "attempts": 0,
        }
    return {"captcha_token": token, "question": f"What is {left} + {right}?", "expires_in_seconds": int(_TTL.total_seconds())}


def verify_challenge(token: str | None, answer: str | None) -> bool:
    if not token or not answer:
        return False
    with _lock:
        _cleanup()
        challenge = _challenges.get(token)
        if not challenge:
            return False
        challenge["attempts"] += 1
        correct = secrets.compare_digest(challenge["answer"], str(answer).strip())
        if correct or challenge["attempts"] >= 3:
            _challenges.pop(token, None)
        return correct


def _cleanup() -> None:
    now = datetime.now(timezone.utc)
    for token in [key for key, item in _challenges.items() if item["expires_at"] <= now]:
        _challenges.pop(token, None)
