import httpx
from pathlib import Path
from typing import Any
from aiornot.req_builders import (
    classify_audio_blob_args,
    classify_audio_url_args,
    classify_image_blob_args,
    classify_image_url_args,
    is_live_args,
)
from aiornot.resp_types import (
    AudioResp,
    CheckTokenResp,
    ImageResp,
    RefreshTokenResp,
    RevokeTokenResp,
)
from aiornot.settings import API_KEY, API_KEY_ERR, BASE_URL


class Client:
    def __init__(
        self,
        api_key: str | None = API_KEY,
        client: httpx.Client | None = None,
        base_url: str = BASE_URL,
    ):
        if api_key is None:
            raise RuntimeError(API_KEY_ERR)
        self._api_key = api_key
        self._client = client or httpx
        self._base_url = base_url

    def _sync_get_json(self, args: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.get(f"{BASE_URL}/system/live", timeout=5)
        resp.raise_for_status()
        return resp.json()

    def is_live(self) -> bool:
        try:
            return self._sync_get_json(is_live_args(self._base_url))["is_live"]
        except httpx.HTTPError:
            return False

    def image_report_by_url(self, url: str) -> ImageResp:
        resp = self._client.post(**classify_image_url_args(url, self._api_key))
        resp.raise_for_status()
        return ImageResp(**resp.json())

    def image_report_by_blob(self, data: bytes) -> ImageResp:
        resp = self._client.post(**classify_image_blob_args(data, self._api_key))
        resp.raise_for_status()
        return ImageResp(**resp.json())

    def image_report_by_file(self, file_path: str | Path) -> ImageResp:
        with open(file_path, "rb") as f:
            return self.image_report_by_blob(f.read())

    def audio_report_by_url(self, url: str) -> AudioResp:
        resp = self._client.post(**classify_audio_url_args(url, self._api_key))
        resp.raise_for_status()
        return AudioResp(**resp.json())

    def audio_report_by_blob(self, data: bytes) -> AudioResp:
        resp = self._client.post(**classify_audio_blob_args(data, self._api_key))
        resp.raise_for_status()
        return AudioResp(**resp.json())

    def audio_report_by_file(self, file_path: str | Path) -> AudioResp:
        with open(file_path, "rb") as f:
            return self.audio_report_by_blob(f.read())

    def check_token(self) -> CheckTokenResp:
        resp = self._client.get(
            f"{BASE_URL}/credentials/tokens",
            timeout=10,
            headers={
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        resp.raise_for_status()
        return CheckTokenResp(**resp.json())

    def refresh_token(self) -> RefreshTokenResp:
        resp = self._client.put(
            f"{BASE_URL}/credentials/tokens",
            timeout=10,
            headers={
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        resp.raise_for_status()
        return RefreshTokenResp(**resp.json())

    def revoke_token(self) -> RevokeTokenResp:
        resp = self._client.delete(
            f"{BASE_URL}/credentials/tokens",
            timeout=10,
            headers={
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        resp.raise_for_status()
        return RevokeTokenResp(**resp.json())
