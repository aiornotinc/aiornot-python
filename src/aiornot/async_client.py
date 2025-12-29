"""Async client for AIORNOT API."""

import asyncio
import csv
from pathlib import Path
from typing import Callable, Sequence, Union, cast

import aiofiles
import httpx

import aiornot.common_client as cc
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
    BatchResult,
    BatchSummary,
    MusicReportResponse,
    TextReportResponse,
    V2ImageReportResponse,
    VideoReportResponse,
    VoiceReportResponse,
)
from aiornot.types.enums import ImageAnalysisType, VideoAnalysisType

_SHARED_CLIENT: httpx.AsyncClient | None = None


def _get_shared_client() -> httpx.AsyncClient:
    """Get or create the shared async client."""
    global _SHARED_CLIENT
    if _SHARED_CLIENT is None:
        _SHARED_CLIENT = httpx.AsyncClient()
    return _SHARED_CLIENT


class AsyncClient:
    """Async client for AIORNOT API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = 180.0,
    ):
        self._api_key = cast(str, api_key or API_KEY)
        if not self._api_key:
            raise RuntimeError(API_KEY_ERR)
        self._base_url = base_url or BASE_URL
        self._client = client or _get_shared_client()
        self._timeout = timeout

    async def is_live(self) -> bool:
        """Check if the API is live."""
        try:
            resp = await self._client.get(**is_live_args(self._base_url))
            return cc.is_live(resp)
        except httpx.TimeoutException:
            return False

    # Image methods
    async def image_report(
        self,
        data: bytes,
        *,
        only: Sequence[ImageAnalysisType] | None = None,
        excluding: Sequence[ImageAnalysisType] | None = None,
        external_id: str | None = None,
    ) -> V2ImageReportResponse:
        """Analyze an image from bytes."""
        try:
            resp = await self._client.post(
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

    async def image_report_from_file(
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
        async with aiofiles.open(path, "rb") as f:
            data = await f.read()
        return await self.image_report(
            data, only=only, excluding=excluding, external_id=external_id
        )

    # Video methods
    async def video_report(
        self,
        data: bytes,
        *,
        only: Sequence[VideoAnalysisType] | None = None,
        excluding: Sequence[VideoAnalysisType] | None = None,
        external_id: str | None = None,
    ) -> VideoReportResponse:
        """Analyze a video from bytes."""
        try:
            resp = await self._client.post(
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

    async def video_report_from_file(
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
        async with aiofiles.open(path, "rb") as f:
            data = await f.read()
        return await self.video_report(
            data, only=only, excluding=excluding, external_id=external_id
        )

    # Voice methods
    async def voice_report(
        self, data: bytes, *, filename: str = "audio.mp3"
    ) -> VoiceReportResponse:
        """Analyze voice/speech audio from bytes."""
        try:
            resp = await self._client.post(
                **voice_report_args(
                    data=data,
                    api_key=self._api_key,
                    base_url=self._base_url,
                    filename=filename,
                    timeout=int(self._timeout),
                )
            )
            return cc.voice_report(resp)
        except httpx.TimeoutException as e:
            raise AIORNotTimeoutError(f"Voice analysis timed out: {e}") from e

    async def voice_report_from_file(
        self, file_path: Union[str, Path]
    ) -> VoiceReportResponse:
        """Analyze voice/speech audio from a file path."""
        path = Path(file_path)
        if not path.exists():
            raise AIORNotFileError(f"File not found: {path}")
        async with aiofiles.open(path, "rb") as f:
            data = await f.read()
        return await self.voice_report(data, filename=path.name)

    # Music methods
    async def music_report(
        self, data: bytes, *, filename: str = "audio.mp3"
    ) -> MusicReportResponse:
        """Analyze music audio from bytes."""
        try:
            resp = await self._client.post(
                **music_report_args(
                    data=data,
                    api_key=self._api_key,
                    base_url=self._base_url,
                    filename=filename,
                    timeout=int(self._timeout),
                )
            )
            return cc.music_report(resp)
        except httpx.TimeoutException as e:
            raise AIORNotTimeoutError(f"Music analysis timed out: {e}") from e

    async def music_report_from_file(
        self, file_path: Union[str, Path]
    ) -> MusicReportResponse:
        """Analyze music audio from a file path."""
        path = Path(file_path)
        if not path.exists():
            raise AIORNotFileError(f"File not found: {path}")
        async with aiofiles.open(path, "rb") as f:
            data = await f.read()
        return await self.music_report(data, filename=path.name)

    # Text methods
    async def text_report(
        self,
        text: str,
        *,
        include_annotations: bool = False,
        external_id: str | None = None,
    ) -> TextReportResponse:
        """Analyze text content."""
        try:
            resp = await self._client.post(
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

    # Batch methods
    async def image_report_batch(
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
        semaphore = asyncio.Semaphore(max_concurrency)
        results: list[BatchResult[V2ImageReportResponse]] = []
        completed = 0

        async def process_item(
            item: Union[bytes, str, Path], idx: int
        ) -> BatchResult[V2ImageReportResponse]:
            nonlocal completed
            async with semaphore:
                external_id = (
                    f"{external_id_prefix}_{idx}" if external_id_prefix else None
                )
                try:
                    if isinstance(item, (str, Path)):
                        result = await self.image_report_from_file(
                            item,
                            only=only,
                            excluding=excluding,
                            external_id=external_id,
                        )
                    else:
                        result = await self.image_report(
                            item,
                            only=only,
                            excluding=excluding,
                            external_id=external_id,
                        )
                    batch_result = BatchResult(
                        input=item, status="success", result=result
                    )
                except Exception as e:
                    if fail_fast:
                        raise
                    batch_result = BatchResult(
                        input=item,
                        status="error",
                        error=type(e).__name__,
                        message=str(e),
                    )
                finally:
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(items))
                return batch_result

        tasks = [process_item(item, i) for i, item in enumerate(items)]
        results = await asyncio.gather(*tasks)

        return BatchSummary(
            results=list(results),
            total=len(items),
            succeeded=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
        )

    async def video_report_batch(
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
        semaphore = asyncio.Semaphore(max_concurrency)
        results: list[BatchResult[VideoReportResponse]] = []
        completed = 0

        async def process_item(
            item: Union[bytes, str, Path], idx: int
        ) -> BatchResult[VideoReportResponse]:
            nonlocal completed
            async with semaphore:
                external_id = (
                    f"{external_id_prefix}_{idx}" if external_id_prefix else None
                )
                try:
                    if isinstance(item, (str, Path)):
                        result = await self.video_report_from_file(
                            item,
                            only=only,
                            excluding=excluding,
                            external_id=external_id,
                        )
                    else:
                        result = await self.video_report(
                            item,
                            only=only,
                            excluding=excluding,
                            external_id=external_id,
                        )
                    batch_result = BatchResult(
                        input=item, status="success", result=result
                    )
                except Exception as e:
                    if fail_fast:
                        raise
                    batch_result = BatchResult(
                        input=item,
                        status="error",
                        error=type(e).__name__,
                        message=str(e),
                    )
                finally:
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(items))
                return batch_result

        tasks = [process_item(item, i) for i, item in enumerate(items)]
        results = await asyncio.gather(*tasks)

        return BatchSummary(
            results=list(results),
            total=len(items),
            succeeded=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
        )

    async def voice_report_batch(
        self,
        items: Sequence[Union[bytes, str, Path]],
        *,
        max_concurrency: int = 3,
        on_progress: Callable[[int, int], None] | None = None,
        fail_fast: bool = False,
    ) -> BatchSummary[VoiceReportResponse]:
        """Process multiple voice audio files concurrently."""
        semaphore = asyncio.Semaphore(max_concurrency)
        results: list[BatchResult[VoiceReportResponse]] = []
        completed = 0

        async def process_item(
            item: Union[bytes, str, Path],
        ) -> BatchResult[VoiceReportResponse]:
            nonlocal completed
            async with semaphore:
                try:
                    if isinstance(item, (str, Path)):
                        result = await self.voice_report_from_file(item)
                    else:
                        result = await self.voice_report(item)
                    batch_result = BatchResult(
                        input=item, status="success", result=result
                    )
                except Exception as e:
                    if fail_fast:
                        raise
                    batch_result = BatchResult(
                        input=item,
                        status="error",
                        error=type(e).__name__,
                        message=str(e),
                    )
                finally:
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(items))
                return batch_result

        tasks = [process_item(item) for item in items]
        results = await asyncio.gather(*tasks)

        return BatchSummary(
            results=list(results),
            total=len(items),
            succeeded=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
        )

    async def music_report_batch(
        self,
        items: Sequence[Union[bytes, str, Path]],
        *,
        max_concurrency: int = 3,
        on_progress: Callable[[int, int], None] | None = None,
        fail_fast: bool = False,
    ) -> BatchSummary[MusicReportResponse]:
        """Process multiple music audio files concurrently."""
        semaphore = asyncio.Semaphore(max_concurrency)
        results: list[BatchResult[MusicReportResponse]] = []
        completed = 0

        async def process_item(
            item: Union[bytes, str, Path],
        ) -> BatchResult[MusicReportResponse]:
            nonlocal completed
            async with semaphore:
                try:
                    if isinstance(item, (str, Path)):
                        result = await self.music_report_from_file(item)
                    else:
                        result = await self.music_report(item)
                    batch_result = BatchResult(
                        input=item, status="success", result=result
                    )
                except Exception as e:
                    if fail_fast:
                        raise
                    batch_result = BatchResult(
                        input=item,
                        status="error",
                        error=type(e).__name__,
                        message=str(e),
                    )
                finally:
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(items))
                return batch_result

        tasks = [process_item(item) for item in items]
        results = await asyncio.gather(*tasks)

        return BatchSummary(
            results=list(results),
            total=len(items),
            succeeded=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
        )

    async def text_report_batch(
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
        semaphore = asyncio.Semaphore(max_concurrency)
        results: list[BatchResult[TextReportResponse]] = []
        completed = 0

        async def process_item(text: str, idx: int) -> BatchResult[TextReportResponse]:
            nonlocal completed
            async with semaphore:
                external_id = (
                    f"{external_id_prefix}_{idx}" if external_id_prefix else None
                )
                try:
                    result = await self.text_report(
                        text,
                        include_annotations=include_annotations,
                        external_id=external_id,
                    )
                    batch_result = BatchResult(
                        input=text, status="success", result=result
                    )
                except Exception as e:
                    if fail_fast:
                        raise
                    batch_result = BatchResult(
                        input=text,
                        status="error",
                        error=type(e).__name__,
                        message=str(e),
                    )
                finally:
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(texts))
                return batch_result

        tasks = [process_item(text, i) for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)

        return BatchSummary(
            results=list(results),
            total=len(texts),
            succeeded=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
        )

    # Directory batch helpers
    async def image_report_directory(
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

        return await self.image_report_batch(files, **batch_kwargs)

    # CSV input helpers
    async def image_report_from_csv(
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

        return await self.image_report_batch(files, **batch_kwargs)

    async def video_report_from_csv(
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

        return await self.video_report_batch(files, **batch_kwargs)

    async def voice_report_from_csv(
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

        return await self.voice_report_batch(files, **batch_kwargs)

    async def music_report_from_csv(
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

        return await self.music_report_batch(files, **batch_kwargs)
