"""Custom exception hierarchy for AIORNOT API errors."""

from typing import Any


class AIORNotError(Exception):
    """Base exception for all AIORNOT errors."""

    pass


class AIORNotAPIError(AIORNotError):
    """Base for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {super().__str__()}"
        return super().__str__()


class AIORNotValidationError(AIORNotAPIError):
    """422 - Request validation failed (bad input)."""

    pass


class AIORNotAuthenticationError(AIORNotAPIError):
    """401 - Invalid or missing API key."""

    pass


class AIORNotRateLimitError(AIORNotAPIError):
    """429 - Rate limit exceeded."""

    pass


class AIORNotServerError(AIORNotAPIError):
    """5xx - Server-side error."""

    pass


class AIORNotTimeoutError(AIORNotError):
    """Request timed out."""

    pass


class AIORNotFileError(AIORNotError):
    """File-related errors (not found, too large, invalid format)."""

    pass
