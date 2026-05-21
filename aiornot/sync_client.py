import httpx
import time
from pathlib import Path
from typing import Any, List, Optional, Set, Union
from aiornot.req_builders import (
    classify_image_blob_args,
    is_live_args,
    check_token_args,
    music_report_sync_args,
    text_report_sync_args,
    video_report_sync_args,
    voice_report_sync_args,
)
from aiornot.resp_types import (
    ImageResp,
    CheckTokenResp,
    MusicResp,
    TextResp,
    VideoResp,
    VoiceResp,
)
import aiornot.common_client as cc
from aiornot.base_client import BaseClient


class Client(BaseClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        client: Optional[httpx.Client] = None,
        max_retries: int = 3,
        retry_backoff: float = 0.25,
        retry_status_codes: Optional[Set[int]] = None,
    ):
        super().__init__(
            api_key, base_url, max_retries, retry_backoff, retry_status_codes
        )
        self._client = client or httpx

    def is_live(self) -> bool:
        return cc.is_live(self._request("get", **is_live_args(self._base_url)))

    def image_report_by_blob_sync(
        self,
        data: bytes,
        external_id: Optional[str] = None,
        only: Optional[List[str]] = None,
        excluding: Optional[List[str]] = None,
    ) -> ImageResp:
        return cc.image_report(
            self._request(
                "post",
                **classify_image_blob_args(
                    data,
                    self._api_key,
                    base_url=self._base_url,
                    external_id=external_id,
                    only=only,
                    excluding=excluding,
                ),
            )
        )

    def image_report_by_file_sync(
        self,
        file_path: Union[str, Path],
        external_id: Optional[str] = None,
        only: Optional[List[str]] = None,
        excluding: Optional[List[str]] = None,
    ) -> ImageResp:
        with open(file_path, "rb") as f:
            return self.image_report_by_blob_sync(
                f.read(), external_id=external_id, only=only, excluding=excluding
            )

    def check_token(self) -> CheckTokenResp:
        return cc.check_token(
            self._request("get", **check_token_args(self._api_key, self._base_url))
        )

    def text_report_sync(
        self,
        text: str,
        external_id: Optional[str] = None,
        include_annotations: bool = False,
    ) -> TextResp:
        return cc.text_report(
            self._request(
                "post",
                **text_report_sync_args(
                    text,
                    self._api_key,
                    base_url=self._base_url,
                    external_id=external_id,
                    include_annotations=include_annotations,
                ),
            )
        )

    def voice_report_by_blob_sync(self, data: bytes) -> VoiceResp:
        return cc.voice_report(
            self._request(
                "post",
                **voice_report_sync_args(
                    data,
                    self._api_key,
                    base_url=self._base_url,
                ),
            )
        )

    def voice_report_by_file_sync(self, file_path: Union[str, Path]) -> VoiceResp:
        with open(file_path, "rb") as f:
            return self.voice_report_by_blob_sync(f.read())

    def music_report_by_blob_sync(self, data: bytes) -> MusicResp:
        return cc.music_report(
            self._request(
                "post",
                **music_report_sync_args(
                    data,
                    self._api_key,
                    base_url=self._base_url,
                ),
            )
        )

    def music_report_by_file_sync(self, file_path: Union[str, Path]) -> MusicResp:
        with open(file_path, "rb") as f:
            return self.music_report_by_blob_sync(f.read())

    def video_report_by_blob_sync(
        self,
        data: bytes,
        external_id: Optional[str] = None,
        only: Optional[List[str]] = None,
        excluding: Optional[List[str]] = None,
    ) -> VideoResp:
        return cc.video_report(
            self._request(
                "post",
                **video_report_sync_args(
                    data,
                    self._api_key,
                    base_url=self._base_url,
                    external_id=external_id,
                    only=only,
                    excluding=excluding,
                ),
            )
        )

    def video_report_by_file_sync(
        self,
        file_path: Union[str, Path],
        external_id: Optional[str] = None,
        only: Optional[List[str]] = None,
        excluding: Optional[List[str]] = None,
    ) -> VideoResp:
        with open(file_path, "rb") as f:
            return self.video_report_by_blob_sync(
                f.read(), external_id=external_id, only=only, excluding=excluding
            )

    def _request(self, method: str, **kwargs: Any) -> httpx.Response:
        request = getattr(self._client, method)
        last_exc: Optional[httpx.TransportError] = None
        for attempt in range(self._max_retries + 1):
            try:
                response = request(**kwargs)
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise
            else:
                if not self._should_retry_status(response.status_code, attempt):
                    return response

            time.sleep(self._retry_delay(attempt))

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("request retry loop exited without a response")
