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
from typing import cast, Optional, Union
import aiofiles
import httpx
from pathlib import Path
import aiornot.common_client as cc


_SHARED_CLIENT = httpx.AsyncClient()


class AsyncClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self._api_key = cast(str, api_key or API_KEY)
        if not self._api_key:
            raise RuntimeError(API_KEY_ERR)
        self._base_url = base_url or BASE_URL
        self._client = client or _SHARED_CLIENT

    async def is_live(self) -> bool:
        return cc.is_live(await self._client.get(**is_live_args(self._base_url)))

    async def image_report_by_url(self, url: str) -> ImageResp:
        return cc.image_report(
            await self._client.post(**classify_image_url_args(url, self._api_key))
        )

    async def image_report_by_blob(self, data: bytes) -> ImageResp:
        return cc.image_report(
            await self._client.post(**classify_image_blob_args(data, self._api_key))
        )

    async def image_report_by_file(self, file_path: Union[str, Path]) -> ImageResp:
        async with aiofiles.open(file_path, "rb") as f:
            return await self.image_report_by_blob(await f.read())

    async def audio_report_by_url(self, url: str) -> AudioResp:
        return cc.audio_report(
            await self._client.post(**classify_audio_url_args(url, self._api_key))
        )

    async def audio_report_by_blob(self, data: bytes) -> AudioResp:
        return cc.audio_report(
            await self._client.post(**classify_audio_blob_args(data, self._api_key))
        )

    async def audio_report_by_file(self, file_path: Union[str, Path]) -> AudioResp:
        async with aiofiles.open(file_path, "rb") as f:
            return await self.audio_report_by_blob(await f.read())

    async def check_token(self) -> CheckTokenResp:
        return cc.check_token(
            await self._client.get(
                f"{BASE_URL}/credentials/tokens",
                timeout=10,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                },
            )
        )

    async def refresh_token(self) -> RefreshTokenResp:
        return cc.refresh_token(
            await self._client.put(
                f"{BASE_URL}/credentials/tokens",
                timeout=10,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                },
            )
        )

    async def revoke_token(self) -> RevokeTokenResp:
        return cc.revoke_token(
            await self._client.delete(
                f"{BASE_URL}/credentials/tokens",
                timeout=10,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                },
            )
        )
