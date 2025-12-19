"""Sync client for AIORNOT API."""

import asyncio
import csv
from pathlib import Path
from typing import Callable, Sequence, Union, cast

import httpx

import aiornot.common_client as cc
from aiornot.async_client import AsyncClient
from aiornot.exceptions import AIORNotFileError, AIORNotTimeoutError
from aiornot.req_builders import (
    image_report_args,
    is_live_args,
    music_report_args,
    text_report_args,
    video_report_args,
    voice_report_args,
)
from aiornot.settings import API_KEY, API_KEY_ERR, BASE_URL
from aiornot.types import (
    BatchSummary,
    MusicReportResponse,
    TextReportResponse,
    V2ImageReportResponse,
    VideoReportResponse,
    VoiceReportResponse,
)
from aiornot.types.enums import ImageAnalysisType, VideoAnalysisType


class Client:
    """Sync client for AIORNOT API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        client: httpx.Client | None = None,
        timeout: float = 180.0,
    ):
        self._api_key = cast(str, api_key or API_KEY)
        if not self._api_key:
            raise RuntimeError(API_KEY_ERR)
        self._base_url = base_url or BASE_URL
        self._client = client or httpx
        self._timeout = timeout

    def is_live(self) -> bool:
        """Check if the API is live."""
        try:
            resp = self._client.get(**is_live_args(self._base_url))
            return cc.is_live(resp)
        except httpx.TimeoutException:
            return False

    # Image methods
    def image_report(
        self,
        data: bytes,
        *,
        only: Sequence[ImageAnalysisType] | None = None,
        excluding: Sequence[ImageAnalysisType] | None = None,
        external_id: str | None = None,
    ) -> V2ImageReportResponse:
        """Analyze an image from bytes."""
        try:
            resp = self._client.post(
                **image_report_args(
                    data=data,
                    api_key=self._api_key,
                    base_url=self._base_url,
                    only=only,
                    excluding=excluding,
                    external_id=external_id,
                    timeout=int(self._timeout),
                )
            )
            return cc.image_report(resp)
        except httpx.TimeoutException as e:
            raise AIORNotTimeoutError(f"Image analysis timed out: {e}") from e

    def image_report_from_file(
        self,
        file_path: Union[str, Path],
        *,
        only: Sequence[ImageAnalysisType] | None = None,
        excluding: Sequence[ImageAnalysisType] | None = None,
        external_id: str | None = None,
    ) -> V2ImageReportResponse:
        """Analyze an image from a file path."""
        path = Path(file_path)
        if not path.exists():
            raise AIORNotFileError(f"File not found: {path}")
        with open(path, "rb") as f:
            data = f.read()
        return self.image_report(
            data, only=only, excluding=excluding, external_id=external_id
        )

    # Video methods
    def video_report(
        self,
        data: bytes,
        *,
        only: Sequence[VideoAnalysisType] | None = None,
        excluding: Sequence[VideoAnalysisType] | None = None,
        external_id: str | None = None,
    ) -> VideoReportResponse:
        """Analyze a video from bytes."""
        try:
            resp = self._client.post(
                **video_report_args(
                    data=data,
                    api_key=self._api_key,
                    base_url=self._base_url,
                    only=only,
                    excluding=excluding,
                    external_id=external_id,
                    timeout=int(self._timeout),
                )
            )
            return cc.video_report(resp)
        except httpx.TimeoutException as e:
            raise AIORNotTimeoutError(f"Video analysis timed out: {e}") from e

    def video_report_from_file(
        self,
        file_path: Union[str, Path],
        *,
        only: Sequence[VideoAnalysisType] | None = None,
        excluding: Sequence[VideoAnalysisType] | None = None,
        external_id: str | None = None,
    ) -> VideoReportResponse:
        """Analyze a video from a file path."""
        path = Path(file_path)
        if not path.exists():
            raise AIORNotFileError(f"File not found: {path}")
        with open(path, "rb") as f:
            data = f.read()
        return self.video_report(
            data, only=only, excluding=excluding, external_id=external_id
        )

    # Voice methods
    def voice_report(self, data: bytes) -> VoiceReportResponse:
        """Analyze voice/speech audio from bytes."""
        try:
            resp = self._client.post(
                **voice_report_args(
                    data=data,
                    api_key=self._api_key,
                    base_url=self._base_url,
                    timeout=int(self._timeout),
                )
            )
            return cc.voice_report(resp)
        except httpx.TimeoutException as e:
            raise AIORNotTimeoutError(f"Voice analysis timed out: {e}") from e

    def voice_report_from_file(
        self, file_path: Union[str, Path]
    ) -> VoiceReportResponse:
        """Analyze voice/speech audio from a file path."""
        path = Path(file_path)
        if not path.exists():
            raise AIORNotFileError(f"File not found: {path}")
        with open(path, "rb") as f:
            data = f.read()
        return self.voice_report(data)

    # Music methods
    def music_report(self, data: bytes) -> MusicReportResponse:
        """Analyze music audio from bytes."""
        try:
            resp = self._client.post(
                **music_report_args(
                    data=data,
                    api_key=self._api_key,
                    base_url=self._base_url,
                    timeout=int(self._timeout),
                )
            )
            return cc.music_report(resp)
        except httpx.TimeoutException as e:
            raise AIORNotTimeoutError(f"Music analysis timed out: {e}") from e

    def music_report_from_file(
        self, file_path: Union[str, Path]
    ) -> MusicReportResponse:
        """Analyze music audio from a file path."""
        path = Path(file_path)
        if not path.exists():
            raise AIORNotFileError(f"File not found: {path}")
        with open(path, "rb") as f:
            data = f.read()
        return self.music_report(data)

    # Text methods
    def text_report(
        self,
        text: str,
        *,
        include_annotations: bool = False,
        external_id: str | None = None,
    ) -> TextReportResponse:
        """Analyze text content."""
        try:
            resp = self._client.post(
                **text_report_args(
                    text=text,
                    api_key=self._api_key,
                    base_url=self._base_url,
                    include_annotations=include_annotations,
                    external_id=external_id,
                    timeout=int(self._timeout),
                )
            )
            return cc.text_report(resp)
        except httpx.TimeoutException as e:
            raise AIORNotTimeoutError(f"Text analysis timed out: {e}") from e

    # Batch methods - delegate to async client via asyncio.run
    def image_report_batch(
        self,
        items: Sequence[Union[bytes, str, Path]],
        *,
        only: Sequence[ImageAnalysisType] | None = None,
        excluding: Sequence[ImageAnalysisType] | None = None,
        external_id_prefix: str | None = None,
        max_concurrency: int = 5,
        on_progress: Callable[[int, int], None] | None = None,
        fail_fast: bool = False,
    ) -> BatchSummary[V2ImageReportResponse]:
        """Process multiple images concurrently."""
        async_client = AsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )
        return asyncio.run(
            async_client.image_report_batch(
                items,
                only=only,
                excluding=excluding,
                external_id_prefix=external_id_prefix,
                max_concurrency=max_concurrency,
                on_progress=on_progress,
                fail_fast=fail_fast,
            )
        )

    def video_report_batch(
        self,
        items: Sequence[Union[bytes, str, Path]],
        *,
        only: Sequence[VideoAnalysisType] | None = None,
        excluding: Sequence[VideoAnalysisType] | None = None,
        external_id_prefix: str | None = None,
        max_concurrency: int = 2,
        on_progress: Callable[[int, int], None] | None = None,
        fail_fast: bool = False,
    ) -> BatchSummary[VideoReportResponse]:
        """Process multiple videos concurrently."""
        async_client = AsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )
        return asyncio.run(
            async_client.video_report_batch(
                items,
                only=only,
                excluding=excluding,
                external_id_prefix=external_id_prefix,
                max_concurrency=max_concurrency,
                on_progress=on_progress,
                fail_fast=fail_fast,
            )
        )

    def voice_report_batch(
        self,
        items: Sequence[Union[bytes, str, Path]],
        *,
        max_concurrency: int = 3,
        on_progress: Callable[[int, int], None] | None = None,
        fail_fast: bool = False,
    ) -> BatchSummary[VoiceReportResponse]:
        """Process multiple voice audio files concurrently."""
        async_client = AsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )
        return asyncio.run(
            async_client.voice_report_batch(
                items,
                max_concurrency=max_concurrency,
                on_progress=on_progress,
                fail_fast=fail_fast,
            )
        )

    def music_report_batch(
        self,
        items: Sequence[Union[bytes, str, Path]],
        *,
        max_concurrency: int = 3,
        on_progress: Callable[[int, int], None] | None = None,
        fail_fast: bool = False,
    ) -> BatchSummary[MusicReportResponse]:
        """Process multiple music audio files concurrently."""
        async_client = AsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )
        return asyncio.run(
            async_client.music_report_batch(
                items,
                max_concurrency=max_concurrency,
                on_progress=on_progress,
                fail_fast=fail_fast,
            )
        )

    def text_report_batch(
        self,
        texts: Sequence[str],
        *,
        include_annotations: bool = False,
        external_id_prefix: str | None = None,
        max_concurrency: int = 10,
        on_progress: Callable[[int, int], None] | None = None,
        fail_fast: bool = False,
    ) -> BatchSummary[TextReportResponse]:
        """Process multiple text strings concurrently."""
        async_client = AsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )
        return asyncio.run(
            async_client.text_report_batch(
                texts,
                include_annotations=include_annotations,
                external_id_prefix=external_id_prefix,
                max_concurrency=max_concurrency,
                on_progress=on_progress,
                fail_fast=fail_fast,
            )
        )

    # Directory batch helper
    def image_report_directory(
        self,
        directory: Union[str, Path],
        *,
        pattern: str = "*.{jpg,jpeg,png,webp,heic,heif,tiff}",
        recursive: bool = False,
        **batch_kwargs,
    ) -> BatchSummary[V2ImageReportResponse]:
        """Process all matching images in a directory."""
        path = Path(directory)
        if not path.is_dir():
            raise AIORNotFileError(f"Directory not found: {path}")

        # Handle brace expansion manually since pathlib doesn't support it
        extensions = ["jpg", "jpeg", "png", "webp", "heic", "heif", "tiff"]
        files: list[Path] = []
        for ext in extensions:
            if recursive:
                files.extend(path.rglob(f"*.{ext}"))
            else:
                files.extend(path.glob(f"*.{ext}"))

        return self.image_report_batch(files, **batch_kwargs)

    # CSV input helpers
    def image_report_from_csv(
        self,
        csv_path: Union[str, Path],
        *,
        key: str = "file_path",
        base_directory: Union[str, Path] | None = None,
        **batch_kwargs,
    ) -> BatchSummary[V2ImageReportResponse]:
        """Process images listed in a CSV file."""
        base = Path(base_directory) if base_directory else None
        files: list[Path] = []

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_path = row[key]
                if base:
                    files.append(base / file_path)
                else:
                    files.append(Path(file_path))

        return self.image_report_batch(files, **batch_kwargs)

    def video_report_from_csv(
        self,
        csv_path: Union[str, Path],
        *,
        key: str = "file_path",
        base_directory: Union[str, Path] | None = None,
        **batch_kwargs,
    ) -> BatchSummary[VideoReportResponse]:
        """Process videos listed in a CSV file."""
        base = Path(base_directory) if base_directory else None
        files: list[Path] = []

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_path = row[key]
                if base:
                    files.append(base / file_path)
                else:
                    files.append(Path(file_path))

        return self.video_report_batch(files, **batch_kwargs)

    def voice_report_from_csv(
        self,
        csv_path: Union[str, Path],
        *,
        key: str = "file_path",
        base_directory: Union[str, Path] | None = None,
        **batch_kwargs,
    ) -> BatchSummary[VoiceReportResponse]:
        """Process voice files listed in a CSV file."""
        base = Path(base_directory) if base_directory else None
        files: list[Path] = []

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_path = row[key]
                if base:
                    files.append(base / file_path)
                else:
                    files.append(Path(file_path))

        return self.voice_report_batch(files, **batch_kwargs)

    def music_report_from_csv(
        self,
        csv_path: Union[str, Path],
        *,
        key: str = "file_path",
        base_directory: Union[str, Path] | None = None,
        **batch_kwargs,
    ) -> BatchSummary[MusicReportResponse]:
        """Process music files listed in a CSV file."""
        base = Path(base_directory) if base_directory else None
        files: list[Path] = []

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_path = row[key]
                if base:
                    files.append(base / file_path)
                else:
                    files.append(Path(file_path))

        return self.music_report_batch(files, **batch_kwargs)
