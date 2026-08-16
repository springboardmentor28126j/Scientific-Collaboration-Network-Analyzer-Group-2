import unittest
from types import SimpleNamespace
from unittest.mock import patch

import redis

from app.models.user import UserRole
from app.services import user_service


class RedisFallbackTests(unittest.TestCase):
    def test_issue_tokens_does_not_raise_when_redis_is_unavailable(self):
        user = SimpleNamespace(user_id=42, role=UserRole.SYSTEM_ADMIN)

        with (
            patch("app.services.user_service.create_access_token", return_value=SimpleNamespace(jti="access-jti", ttl_seconds=60, token="access-token")),
            patch("app.services.user_service.create_refresh_token", return_value=SimpleNamespace(jti="refresh-jti", ttl_seconds=120, token="refresh-token")),
            patch("app.core.redis_client.redis_client.setex", side_effect=redis.exceptions.ConnectionError("redis down")),
        ):
            access_token, refresh_token = user_service.issue_tokens(user)

        self.assertEqual(access_token, "access-token")
        self.assertEqual(refresh_token, "refresh-token")


if __name__ == "__main__":
    unittest.main()
