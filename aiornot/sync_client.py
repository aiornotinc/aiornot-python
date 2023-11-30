import httpx
from pathlib import Path
from typing import Optional, Union, cast
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
import aiornot.common_client as cc
from aiornot.settings import API_KEY_ERR, BASE_URL, API_KEY


class Client:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        client: Optional[httpx.Client] = None,
    ):
        self._api_key = cast(str, api_key or API_KEY)
        if not self._api_key:
            raise RuntimeError(API_KEY_ERR)

        self._api_key = api_key or API_KEY
        self._client = client or httpx
        self._base_url = base_url or BASE_URL

    def is_live(self) -> bool:
        return cc.is_live(self._client.get(**is_live_args(self._base_url)))

    def image_report_by_url(self, url: str) -> ImageResp:
        return cc.image_report(
            self._client.post(**classify_image_url_args(url, self._api_key))
        )

    def image_report_by_blob(self, data: bytes) -> ImageResp:
        return cc.image_report(
            self._client.post(**classify_image_blob_args(data, self._api_key))
        )

    def image_report_by_file(self, file_path: Union[str, Path]) -> ImageResp:
        with open(file_path, "rb") as f:
            return self.image_report_by_blob(f.read())

    def audio_report_by_url(self, url: str) -> AudioResp:
        return cc.audio_report(
            self._client.post(**classify_audio_url_args(url, self._api_key))
        )

    def audio_report_by_blob(self, data: bytes) -> AudioResp:
        return cc.audio_report(
            self._client.post(**classify_audio_blob_args(data, self._api_key))
        )

    def audio_report_by_file(self, file_path: Union[str, Path]) -> AudioResp:
        with open(file_path, "rb") as f:
            return self.audio_report_by_blob(f.read())

    def check_token(self) -> CheckTokenResp:
        return cc.check_token(
            self._client.get(
                f"{BASE_URL}/credentials/tokens",
                timeout=10,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                },
            )
        )

    def refresh_token(self) -> RefreshTokenResp:
        return cc.refresh_token(
            self._client.put(
                f"{BASE_URL}/credentials/tokens",
                timeout=10,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                },
            )
        )

    def revoke_token(self) -> RevokeTokenResp:
        return cc.revoke_token(
            self._client.delete(
                f"{BASE_URL}/credentials/tokens",
                timeout=10,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                },
            )
        )
