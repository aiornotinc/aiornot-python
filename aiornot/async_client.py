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
from typing import cast
import aiofiles
import httpx


from pathlib import Path


class AsyncClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self._api_key = cast(str, api_key or API_KEY)
        if not self._api_key:
            raise ValueError(API_KEY_ERR)
        self._base_url = base_url or BASE_URL
        self._client = client or httpx.AsyncClient()

    async def is_live(self) -> bool:
        resp = await self._client.get(**is_live_args(self._base_url))
        resp.raise_for_status()
        return resp.json()["is_live"]

    async def image_report_by_url(self, url: str) -> ImageResp:
        resp = await self._client.post(**classify_image_url_args(url, self._api_key))
        resp.raise_for_status()
        return ImageResp(**resp.json())

    async def image_report_by_blob(self, data: bytes) -> ImageResp:
        resp = await self._client.post(**classify_image_blob_args(data, self._api_key))
        resp.raise_for_status()
        return ImageResp(**resp.json())

    async def image_report_by_file(self, file_path: str | Path) -> ImageResp:
        async with aiofiles.open(file_path, "rb") as f:
            return await self.image_report_by_blob(await f.read())

    async def audio_report_by_url(self, url: str) -> AudioResp:
        resp = await self._client.post(**classify_audio_url_args(url, self._api_key))
        resp.raise_for_status()
        return AudioResp(**resp.json())

    async def audio_report_by_blob(self, data: bytes) -> AudioResp:
        resp = await self._client.post(**classify_audio_blob_args(data, self._api_key))
        resp.raise_for_status()
        return AudioResp(**resp.json())

    async def audio_report_by_file(self, file_path: str | Path) -> AudioResp:
        async with aiofiles.open(file_path, "rb") as f:
            return await self.audio_report_by_blob(await f.read())

    async def check_token(self) -> CheckTokenResp:
        resp = await self._client.get(
            f"{BASE_URL}/credentials/tokens",
            timeout=10,
            headers={
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        resp.raise_for_status()
        return CheckTokenResp(**resp.json())

    async def refresh_token(self) -> RefreshTokenResp:
        resp = await self._client.put(
            f"{BASE_URL}/credentials/tokens",
            timeout=10,
            headers={
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        resp.raise_for_status()
        return RefreshTokenResp(**resp.json())

    async def revoke_token(self) -> RevokeTokenResp:
        resp = await self._client.delete(
            f"{BASE_URL}/credentials/tokens",
            timeout=10,
            headers={
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        resp.raise_for_status()
        return RevokeTokenResp(**resp.json())
