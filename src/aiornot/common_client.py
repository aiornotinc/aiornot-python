"""Common response parsing functions for AIORNOT API."""

import httpx

from aiornot.exceptions import (
    AIORNotAPIError,
    AIORNotAuthenticationError,
    AIORNotRateLimitError,
    AIORNotServerError,
    AIORNotValidationError,
)
from aiornot.types import (
    MusicReportResponse,
    TextReportResponse,
    V2ImageReportResponse,
    VideoReportResponse,
    VoiceReportResponse,
)


def _handle_error_response(resp: httpx.Response) -> None:
    """Raise appropriate exception for error responses."""
    status = resp.status_code

    try:
        response_data = resp.json()
    except Exception:
        response_data = {"detail": resp.text}

    message = response_data.get("detail", str(response_data))
    if isinstance(message, list):
        # Handle validation error format
        message = "; ".join(
            f"{err.get('loc', [])}: {err.get('msg', '')}" for err in message
        )

    if status == 401:
        raise AIORNotAuthenticationError(
            message or "Invalid or missing API key",
            status_code=status,
            response=response_data,
        )
    elif status == 422:
        raise AIORNotValidationError(
            message or "Request validation failed",
            status_code=status,
            response=response_data,
        )
    elif status == 429:
        raise AIORNotRateLimitError(
            message or "Rate limit exceeded",
            status_code=status,
            response=response_data,
        )
    elif status >= 500:
        raise AIORNotServerError(
            message or "Server error",
            status_code=status,
            response=response_data,
        )
    else:
        raise AIORNotAPIError(
            message or f"API error: {status}",
            status_code=status,
            response=response_data,
        )


def _check_response(resp: httpx.Response) -> None:
    """Check response status and raise exception if error."""
    if not resp.is_success:
        _handle_error_response(resp)


def is_live(resp: httpx.Response) -> bool:
    """Parse health check response."""
    resp.raise_for_status()
    return resp.json().get("is_live", False)


def image_report(resp: httpx.Response) -> V2ImageReportResponse:
    """Parse v2 image report response."""
    _check_response(resp)
    return V2ImageReportResponse(**resp.json())


def video_report(resp: httpx.Response) -> VideoReportResponse:
    """Parse v2 video report response."""
    _check_response(resp)
    return VideoReportResponse(**resp.json())


def voice_report(resp: httpx.Response) -> VoiceReportResponse:
    """Parse v1 voice report response."""
    _check_response(resp)
    return VoiceReportResponse(**resp.json())


def music_report(resp: httpx.Response) -> MusicReportResponse:
    """Parse v1 music report response."""
    _check_response(resp)
    return MusicReportResponse(**resp.json())


def text_report(resp: httpx.Response) -> TextReportResponse:
    """Parse v2 text report response."""
    _check_response(resp)
    return TextReportResponse(**resp.json())
