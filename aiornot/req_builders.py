from typing import Any, Optional, List
from aiornot.settings import BASE_URL

_THREE_MINUTES = 180


def is_live_args(base_url: str, timeout: int = 5) -> dict[str, Any]:
    return {
        "url": f"{base_url}/v1/system/live",
        "timeout": timeout,
    }


def classify_image_blob_args(
    data: bytes,
    api_key: str,
    base_url: str = BASE_URL,
    timeout: int = _THREE_MINUTES,
    external_id: Optional[str] = None,
    only: Optional[List[str]] = None,
    excluding: Optional[List[str]] = None,
) -> dict[str, Any]:
    args = {
        "url": f"{base_url}/v2/image/sync",
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
        "files": {"image": data},
        "timeout": timeout,
    }

    params: dict[str, Any] = {}
    if external_id:
        params["external_id"] = external_id
    if only:
        params["only"] = only
    if excluding:
        params["excluding"] = excluding

    if params:
        args["params"] = params

    return args


def check_token_args(
    api_key: str, base_url: str = BASE_URL, timeout: int = 10
) -> dict[str, Any]:
    return {
        "url": f"{base_url}/v2/billing/balance",
        "timeout": timeout,
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
    }


def text_report_sync_args(
    text: str,
    api_key: str,
    base_url: str = BASE_URL,
    timeout: int = _THREE_MINUTES,
    external_id: Optional[str] = None,
    include_annotations: bool = False,
) -> dict[str, Any]:
    args = {
        "url": f"{base_url}/v2/text/sync",
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
        "files": {"text": (None, text)},
        "timeout": timeout,
    }

    params: dict[str, Any] = {}
    if external_id:
        params["external_id"] = external_id
    if include_annotations:
        params["include_annotations"] = include_annotations

    if params:
        args["params"] = params

    return args


def voice_report_sync_args(
    data: bytes,
    api_key: str,
    base_url: str = BASE_URL,
    timeout: int = _THREE_MINUTES,
) -> dict[str, Any]:
    return {
        "url": f"{base_url}/v1/reports/voice",
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
        "files": {"file": data},
        "timeout": timeout,
    }


def music_report_sync_args(
    data: bytes,
    api_key: str,
    base_url: str = BASE_URL,
    timeout: int = _THREE_MINUTES,
) -> dict[str, Any]:
    return {
        "url": f"{base_url}/v1/reports/music",
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
        "files": {"file": data},
        "timeout": timeout,
    }


def video_report_sync_args(
    data: bytes,
    api_key: str,
    base_url: str = BASE_URL,
    timeout: int = _THREE_MINUTES,
    external_id: Optional[str] = None,
    only: Optional[List[str]] = None,
    excluding: Optional[List[str]] = None,
) -> dict[str, Any]:
    args = {
        "url": f"{base_url}/v2/video/sync",
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
        "files": {"video": data},
        "timeout": timeout,
    }

    params: dict[str, Any] = {}
    if external_id:
        params["external_id"] = external_id
    if only:
        params["only"] = only
    if excluding:
        params["excluding"] = excluding

    if params:
        args["params"] = params

    return args
