from app.core.security import (
    hash_password,
    verify_password,
)

password = "Password@123"

hashed = hash_password(password)

print(hashed)

print(
    verify_password(
        password,
        hashed,
    )
)
