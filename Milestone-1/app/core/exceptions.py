"""
Domain-level exceptions raised by services, translated into proper HTTP
responses by the handlers registered in app/main.py. Keeps services free
of any direct dependency on FastAPI/HTTPException.
"""


class AppError(Exception):
    """Base class for all domain errors."""

    status_code: int = 400

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class InvalidTokenError(AppError):
    status_code = 400
