import unittest
from unittest.mock import MagicMock, patch

import httpx
import redis

from app.core import recaptcha, redis_client


class LoginFailureCounterTests(unittest.TestCase):
    def test_record_failed_login_increments_and_sets_ttl(self):
        with (
            patch("app.core.redis_client.redis_client.incr", return_value=3) as mock_incr,
            patch("app.core.redis_client.redis_client.expire") as mock_expire,
        ):
            count = redis_client.record_failed_login("USER@Example.com", window_seconds=900)

        self.assertEqual(count, 3)
        mock_incr.assert_called_once_with("login:fail:user@example.com")
        mock_expire.assert_called_once_with("login:fail:user@example.com", 900)

    def test_record_failed_login_fails_open_when_redis_down(self):
        with patch(
            "app.core.redis_client.redis_client.incr",
            side_effect=redis.exceptions.ConnectionError("redis down"),
        ):
            count = redis_client.record_failed_login("user@example.com", window_seconds=900)
        self.assertEqual(count, 0)

    def test_get_failed_login_count_reads_zero_when_missing(self):
        with patch("app.core.redis_client.redis_client.get", return_value=None):
            self.assertEqual(redis_client.get_failed_login_count("user@example.com"), 0)

    def test_get_failed_login_count_fails_open_when_redis_down(self):
        with patch(
            "app.core.redis_client.redis_client.get",
            side_effect=redis.exceptions.ConnectionError("redis down"),
        ):
            self.assertEqual(redis_client.get_failed_login_count("user@example.com"), 0)

    def test_reset_failed_login_deletes_counter(self):
        with patch("app.core.redis_client.redis_client.delete") as mock_delete:
            redis_client.reset_failed_login("USER@Example.com")
        mock_delete.assert_called_once_with("login:fail:user@example.com")


def _fake_response(json_body, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_body
    resp.raise_for_status.side_effect = (
        None if status_code < 400 else httpx.HTTPStatusError("error", request=MagicMock(), response=resp)
    )
    return resp


class RecaptchaTests(unittest.TestCase):
    def test_verify_recaptcha_accepts_successful_token(self):
        with (
            patch("app.core.recaptcha.settings.RECAPTCHA_SECRET_KEY", "test-secret"),
            patch("app.core.recaptcha.httpx.post", return_value=_fake_response({"success": True})) as mock_post,
        ):
            self.assertTrue(recaptcha.verify_recaptcha("good-token", remote_ip="1.2.3.4"))

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["data"]["secret"], "test-secret")
        self.assertEqual(kwargs["data"]["response"], "good-token")
        self.assertEqual(kwargs["data"]["remoteip"], "1.2.3.4")

    def test_verify_recaptcha_rejects_failed_token(self):
        with (
            patch("app.core.recaptcha.settings.RECAPTCHA_SECRET_KEY", "test-secret"),
            patch(
                "app.core.recaptcha.httpx.post",
                return_value=_fake_response({"success": False, "error-codes": ["invalid-input-response"]}),
            ),
        ):
            self.assertFalse(recaptcha.verify_recaptcha("bad-token"))

    def test_verify_recaptcha_rejects_missing_token(self):
        self.assertFalse(recaptcha.verify_recaptcha(None))
        self.assertFalse(recaptcha.verify_recaptcha(""))

    def test_verify_recaptcha_fails_closed_when_secret_key_missing(self):
        with patch("app.core.recaptcha.settings.RECAPTCHA_SECRET_KEY", ""):
            self.assertFalse(recaptcha.verify_recaptcha("some-token"))

    def test_verify_recaptcha_fails_closed_when_google_unreachable(self):
        with (
            patch("app.core.recaptcha.settings.RECAPTCHA_SECRET_KEY", "test-secret"),
            patch("app.core.recaptcha.httpx.post", side_effect=httpx.ConnectError("down")),
        ):
            self.assertFalse(recaptcha.verify_recaptcha("some-token"))


if __name__ == "__main__":
    unittest.main()
