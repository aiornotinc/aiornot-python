"""Request builder functions for AIORNOT API endpoints."""

from typing import Any, Sequence

from aiornot.types.enums import ImageAnalysisType, VideoAnalysisType

_DEFAULT_TIMEOUT = 180  # 3 minutes


def is_live_args(base_url: str, timeout: int = 5) -> dict[str, Any]:
    """Build args for health check endpoint."""
    return {
        "url": f"{base_url}/v1/system/live",
        "timeout": timeout,
    }


def _build_query_params(
    only: Sequence[str] | None = None,
    excluding: Sequence[str] | None = None,
    external_id: str | None = None,
    include_annotations: bool | None = None,
) -> dict[str, Any]:
    """Build query parameters for API requests."""
    params: dict[str, Any] = {}
    if only:
        params["only"] = list(only)
    if excluding:
        params["excluding"] = list(excluding)
    if external_id:
        params["external_id"] = external_id
    if include_annotations is not None:
        params["include_annotations"] = include_annotations
    return params


def image_report_args(
    data: bytes,
    api_key: str,
    base_url: str,
    only: Sequence[ImageAnalysisType] | None = None,
    excluding: Sequence[ImageAnalysisType] | None = None,
    external_id: str | None = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Build args for v2 image analysis endpoint."""
    params = _build_query_params(
        only=[t.value for t in only] if only else None,
        excluding=[t.value for t in excluding] if excluding else None,
        external_id=external_id,
    )
    return {
        "url": f"{base_url}/v2/image/sync",
        "headers": {"Authorization": f"Bearer {api_key}"},
        "files": {"image": data},
        "params": params if params else None,
        "timeout": timeout,
    }


def video_report_args(
    data: bytes,
    api_key: str,
    base_url: str,
    only: Sequence[VideoAnalysisType] | None = None,
    excluding: Sequence[VideoAnalysisType] | None = None,
    external_id: str | None = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Build args for v2 video analysis endpoint."""
    params = _build_query_params(
        only=[t.value for t in only] if only else None,
        excluding=[t.value for t in excluding] if excluding else None,
        external_id=external_id,
    )
    return {
        "url": f"{base_url}/v2/video/sync",
        "headers": {"Authorization": f"Bearer {api_key}"},
        "files": {"video": data},
        "params": params if params else None,
        "timeout": timeout,
    }


def voice_report_args(
    data: bytes,
    api_key: str,
    base_url: str,
    timeout: int = _DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Build args for v1 voice analysis endpoint."""
    return {
        "url": f"{base_url}/v1/reports/voice",
        "headers": {"Authorization": f"Bearer {api_key}"},
        "files": {"file": data},
        "timeout": timeout,
    }


def music_report_args(
    data: bytes,
    api_key: str,
    base_url: str,
    timeout: int = _DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Build args for v1 music analysis endpoint."""
    return {
        "url": f"{base_url}/v1/reports/music",
        "headers": {"Authorization": f"Bearer {api_key}"},
        "files": {"file": data},
        "timeout": timeout,
    }


def text_report_args(
    text: str,
    api_key: str,
    base_url: str,
    include_annotations: bool = False,
    external_id: str | None = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Build args for v2 text analysis endpoint."""
    params = _build_query_params(
        include_annotations=include_annotations,
        external_id=external_id,
    )
    return {
        "url": f"{base_url}/v2/text/sync",
        "headers": {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        "data": {"text": text},
        "params": params if params else None,
        "timeout": timeout,
    }
