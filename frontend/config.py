import os

BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api/v1")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

# Google reCAPTCHA site key -- public, safe to embed in the login page HTML.
# Must match the RECAPTCHA_SITE_KEY the backend verifies against. Defaults
# to Google's published test key so local development works out of the box;
# it always passes verification and must be swapped for a real key (from
# https://www.google.com/recaptcha/admin) before production use.
RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "6LfaSogtAAAAAFVqUtG2GPnC37rZ4E49vD9ArtjP")