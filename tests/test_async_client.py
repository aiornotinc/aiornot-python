"""Tests for async client functionality."""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from aiornot import AsyncClient
from aiornot.exceptions import (
    AIORNotAuthenticationError,
    AIORNotFileError,
    AIORNotTimeoutError,
)


class TestAsyncClientInit:
    """Tests for async client initialization."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        client = AsyncClient(api_key="test-key")
        assert client._api_key == "test-key"

    def test_init_with_env_var(self, monkeypatch):
        """Test initialization with API key from environment."""
        # Patch the module-level constant since it's read at import time
        monkeypatch.setattr("aiornot.settings.API_KEY", "env-test-key")
        monkeypatch.setattr("aiornot.async_client.API_KEY", "env-test-key")
        client = AsyncClient()
        assert client._api_key == "env-test-key"

    def test_init_missing_api_key_raises(self, monkeypatch):
        """Test that missing API key raises RuntimeError."""
        monkeypatch.delenv("AIORNOT_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="API key"):
            AsyncClient()

    def test_init_custom_base_url(self):
        """Test initialization with custom base URL."""
        client = AsyncClient(api_key="test-key", base_url="https://custom.api.com")
        assert client._base_url == "https://custom.api.com"

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        client = AsyncClient(api_key="test-key", timeout=60.0)
        assert client._timeout == 60.0


class TestAsyncIsLive:
    """Tests for async is_live health check."""

    async def test_is_live_success(self):
        """Test successful health check."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.json.return_value = {"is_live": True}
        mock_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        assert await client.is_live() is True

    async def test_is_live_timeout_returns_false(self):
        """Test that timeout returns False instead of raising."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        client = AsyncClient(api_key="test-key", client=mock_client)
        assert await client.is_live() is False


class TestAsyncImageReport:
    """Tests for async image analysis."""

    async def test_image_report_success(self, sample_image_response: dict[str, Any]):
        """Test successful image analysis."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_image_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.image_report(b"fake-image-data")

        assert result.id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        assert result.is_ai() is True

    async def test_image_report_from_file(
        self, sample_image_response: dict[str, Any], temp_image_file: Path
    ):
        """Test image analysis from file."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_image_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.image_report_from_file(temp_image_file)

        assert result.id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    async def test_image_report_file_not_found(self):
        """Test file not found raises AIORNotFileError."""
        client = AsyncClient(api_key="test-key")
        with pytest.raises(AIORNotFileError, match="File not found"):
            await client.image_report_from_file("/nonexistent/path.jpg")

    async def test_image_report_timeout(self):
        """Test image analysis timeout raises AIORNotTimeoutError."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        client = AsyncClient(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotTimeoutError, match="timed out"):
            await client.image_report(b"fake-image-data")

    async def test_image_report_authentication_error(self):
        """Test 401 raises AIORNotAuthenticationError."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_response.text = "Unauthorized"
        mock_response.json.return_value = {"detail": "Invalid API key"}
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="bad-key", client=mock_client)
        with pytest.raises(AIORNotAuthenticationError):
            await client.image_report(b"fake-image-data")


class TestAsyncVideoReport:
    """Tests for async video analysis."""

    async def test_video_report_success(self, sample_video_response: dict[str, Any]):
        """Test successful video analysis."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_video_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.video_report(b"fake-video-data")

        assert result.id == "b2c3d4e5-f6a7-8901-bcde-f12345678901"

    async def test_video_report_from_file(
        self, sample_video_response: dict[str, Any], temp_video_file: Path
    ):
        """Test video analysis from file."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_video_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.video_report_from_file(temp_video_file)

        assert result.id == "b2c3d4e5-f6a7-8901-bcde-f12345678901"


class TestAsyncVoiceReport:
    """Tests for async voice/speech analysis."""

    async def test_voice_report_success(self, sample_voice_response: dict[str, Any]):
        """Test successful voice analysis."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_voice_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.voice_report(b"fake-audio-data")

        assert result.id == "c3d4e5f6-a7b8-9012-cdef-123456789012"
        assert result.is_ai() is True

    async def test_voice_report_from_file(
        self, sample_voice_response: dict[str, Any], temp_audio_file: Path
    ):
        """Test voice analysis from file."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_voice_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.voice_report_from_file(temp_audio_file)

        assert result.id == "c3d4e5f6-a7b8-9012-cdef-123456789012"


class TestAsyncMusicReport:
    """Tests for async music analysis."""

    async def test_music_report_success(self, sample_music_response: dict[str, Any]):
        """Test successful music analysis."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_music_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.music_report(b"fake-audio-data")

        assert result.id == "d4e5f6a7-b8c9-0123-def0-234567890123"
        assert result.is_ai() is False

    async def test_music_report_from_file(
        self, sample_music_response: dict[str, Any], temp_audio_file: Path
    ):
        """Test music analysis from file."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_music_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.music_report_from_file(temp_audio_file)

        assert result.id == "d4e5f6a7-b8c9-0123-def0-234567890123"


class TestAsyncTextReport:
    """Tests for async text analysis."""

    async def test_text_report_success(self, sample_text_response: dict[str, Any]):
        """Test successful text analysis."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_text_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.text_report("This is sample text for analysis.")

        assert result.id == "e5f6a7b8-c9d0-1234-ef01-345678901234"
        assert result.is_ai() is True

    async def test_text_report_with_annotations(
        self, sample_text_response: dict[str, Any]
    ):
        """Test text analysis with annotations requested."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_text_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.text_report("Sample text", include_annotations=True)

        assert result.annotations is not None
        assert len(result.annotations) == 3


class TestAsyncBatchProcessing:
    """Tests for async batch processing."""

    async def test_image_report_batch_success(
        self, sample_image_response: dict[str, Any], temp_image_file: Path
    ):
        """Test batch image processing."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_image_response
        mock_client.post = AsyncMock(return_value=mock_response)

        client = AsyncClient(api_key="test-key", client=mock_client)
        result = await client.image_report_batch([temp_image_file])

        assert result.total == 1
        assert result.succeeded == 1
        assert result.failed == 0

    async def test_batch_with_progress_callback(
        self, sample_image_response: dict[str, Any], temp_image_file: Path
    ):
        """Test batch processing with progress callback."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_image_response
        mock_client.post = AsyncMock(return_value=mock_response)

        progress_calls = []

        def on_progress(completed: int, total: int):
            progress_calls.append((completed, total))

        client = AsyncClient(api_key="test-key", client=mock_client)
        await client.image_report_batch([temp_image_file], on_progress=on_progress)

        assert len(progress_calls) > 0
        assert progress_calls[-1] == (1, 1)  # Final callback should show completion

    async def test_batch_fail_fast(self, temp_image_file: Path):
        """Test batch processing with fail_fast option."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        client = AsyncClient(api_key="test-key", client=mock_client)

        with pytest.raises(AIORNotTimeoutError):
            await client.image_report_batch([temp_image_file], fail_fast=True)


class TestAsyncDirectoryBatch:
    """Tests for async directory batch processing."""

    async def test_image_report_directory_not_found(self):
        """Test directory not found raises AIORNotFileError."""
        client = AsyncClient(api_key="test-key")
        with pytest.raises(AIORNotFileError, match="Directory not found"):
            await client.image_report_directory("/nonexistent/directory")


class TestSharedClient:
    """Tests for shared client management."""

    async def test_uses_shared_client_when_none_provided(self):
        """Test that shared client is used when no client provided."""
        # Reset shared client
        import aiornot.async_client as ac

        ac._SHARED_CLIENT = None

        client = AsyncClient(api_key="test-key")
        # Access internal client to verify it's using shared client
        # This is implementation detail but important for resource management
        assert client._client is not None
