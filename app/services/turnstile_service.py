import httpx

from app.core.config import settings
from app.core.exceptions import ForbiddenError


TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


class TurnstileService:
    async def verify(
        self,
        token: str,
    ) -> None:
        payload = {
            "secret": settings.TURNSTILE_SECRET_KEY,
            "response": token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                TURNSTILE_VERIFY_URL,
                json=payload,
                timeout=10.0,
            )

        response.raise_for_status()

        result = response.json()

        if not result.get("success"):
            raise ForbiddenError("Turnstile verification failed.")
