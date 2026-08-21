"""Shared field-level validators used across multiple Pydantic schemas."""

import re


def validate_password_strength(password: str) -> str:
    """
    Default password policy — reasonable minimum, not overly strict:
    at least 8 characters, at least one letter and one digit.
    Tune this in one place if requirements change.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Za-z]", password):
        raise ValueError("Password must contain at least one letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    return password
