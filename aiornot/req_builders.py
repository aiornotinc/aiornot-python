from typing import Any
from aiornot.settings import BASE_URL

_THREE_MINUTES = 180


def is_live_args(base_url: str, timeout: int = 5) -> dict[str, Any]:
    return {
        "url": f"{base_url}/system/live",
        "timeout": timeout,
    }


def classify_image_url_args(
    url: str, api_key: str, timeout: int = _THREE_MINUTES
) -> dict[str, Any]:
    return {
        "url": f"{BASE_URL}/reports/image",
        "headers": {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        "json": {"object": str(url)},
        "timeout": timeout,
    }


def classify_image_blob_args(
    data: bytes, api_key: str, timeout: int = _THREE_MINUTES
) -> dict[str, Any]:
    return {
        "url": f"{BASE_URL}/reports/image",
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
        "files": {"object": data},
        "timeout": timeout,
    }


def classify_audio_url_args(
    url: str, api_key: str, timeout: int = _THREE_MINUTES
) -> dict[str, Any]:
    return {
        "url": f"{BASE_URL}/reports/audio",
        "headers": {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        "json": {"object": str(url)},
        "timeout": timeout,
    }


def classify_audio_blob_args(
    data: bytes, api_key: str, timeout: int = _THREE_MINUTES
) -> dict[str, Any]:
    return {
        "url": f"{BASE_URL}/reports/audio",
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
        "files": {"object": data},
        "timeout": timeout,
    }
