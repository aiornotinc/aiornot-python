"""Tests for sync client functionality."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from aiornot import Client
from aiornot.exceptions import (
    AIORNotAuthenticationError,
    AIORNotFileError,
    AIORNotRateLimitError,
    AIORNotServerError,
    AIORNotTimeoutError,
    AIORNotValidationError,
)


class TestClientInit:
    """Tests for client initialization."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        client = Client(api_key="test-key")
        assert client._api_key == "test-key"

    def test_init_with_env_var(self, monkeypatch):
        """Test initialization with API key from environment."""
        # Patch the module-level constant since it's read at import time
        monkeypatch.setattr("aiornot.settings.API_KEY", "env-test-key")
        monkeypatch.setattr("aiornot.sync_client.API_KEY", "env-test-key")
        client = Client()
        assert client._api_key == "env-test-key"

    def test_init_missing_api_key_raises(self, monkeypatch):
        """Test that missing API key raises RuntimeError."""
        monkeypatch.delenv("AIORNOT_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="API key"):
            Client()

    def test_init_custom_base_url(self):
        """Test initialization with custom base URL."""
        client = Client(api_key="test-key", base_url="https://custom.api.com")
        assert client._base_url == "https://custom.api.com"

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        client = Client(api_key="test-key", timeout=60.0)
        assert client._timeout == 60.0

    def test_init_custom_httpx_client(self):
        """Test initialization with custom httpx client."""
        mock_client = MagicMock(spec=httpx.Client)
        client = Client(api_key="test-key", client=mock_client)
        assert client._client is mock_client


class TestIsLive:
    """Tests for is_live health check."""

    def test_is_live_success(self):
        """Test successful health check."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.json.return_value = {"is_live": True}
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        assert client.is_live() is True
        mock_client.get.assert_called_once()

    def test_is_live_false(self):
        """Test health check returns false."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.json.return_value = {"is_live": False}
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        assert client.is_live() is False

    def test_is_live_timeout_returns_false(self):
        """Test that timeout returns False instead of raising."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")

        client = Client(api_key="test-key", client=mock_client)
        assert client.is_live() is False


class TestImageReport:
    """Tests for image analysis."""

    def test_image_report_success(self, sample_image_response: dict[str, Any]):
        """Test successful image analysis."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_image_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.image_report(b"fake-image-data")

        assert result.id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        assert result.is_ai() is True
        mock_client.post.assert_called_once()

    def test_image_report_from_file(
        self, sample_image_response: dict[str, Any], temp_image_file: Path
    ):
        """Test image analysis from file."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_image_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.image_report_from_file(temp_image_file)

        assert result.id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    def test_image_report_from_file_not_found(self):
        """Test file not found raises AIORNotFileError."""
        client = Client(api_key="test-key")
        with pytest.raises(AIORNotFileError, match="File not found"):
            client.image_report_from_file("/nonexistent/path.jpg")

    def test_image_report_timeout(self):
        """Test image analysis timeout raises AIORNotTimeoutError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        client = Client(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotTimeoutError, match="timed out"):
            client.image_report(b"fake-image-data")

    def test_image_report_authentication_error(self):
        """Test 401 raises AIORNotAuthenticationError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_response.text = "Unauthorized"
        mock_response.json.return_value = {"detail": "Invalid API key"}
        mock_client.post.return_value = mock_response

        client = Client(api_key="bad-key", client=mock_client)
        with pytest.raises(AIORNotAuthenticationError):
            client.image_report(b"fake-image-data")

    def test_image_report_validation_error(self):
        """Test 422 raises AIORNotValidationError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.is_success = False
        mock_response.text = "Validation Error"
        mock_response.json.return_value = {"detail": "Invalid image format"}
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotValidationError):
            client.image_report(b"bad-data")

    def test_image_report_rate_limit(self):
        """Test 429 raises AIORNotRateLimitError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.is_success = False
        mock_response.text = "Too Many Requests"
        mock_response.json.return_value = {"detail": "Rate limit exceeded"}
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotRateLimitError):
            client.image_report(b"fake-image-data")

    def test_image_report_server_error(self):
        """Test 5xx raises AIORNotServerError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.is_success = False
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"detail": "Internal error"}
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotServerError):
            client.image_report(b"fake-image-data")


class TestVideoReport:
    """Tests for video analysis."""

    def test_video_report_success(self, sample_video_response: dict[str, Any]):
        """Test successful video analysis."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_video_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.video_report(b"fake-video-data")

        assert result.id == "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        mock_client.post.assert_called_once()

    def test_video_report_from_file(
        self, sample_video_response: dict[str, Any], temp_video_file: Path
    ):
        """Test video analysis from file."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_video_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.video_report_from_file(temp_video_file)

        assert result.id == "b2c3d4e5-f6a7-8901-bcde-f12345678901"

    def test_video_report_timeout(self):
        """Test video analysis timeout raises AIORNotTimeoutError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        client = Client(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotTimeoutError, match="timed out"):
            client.video_report(b"fake-video-data")


class TestVoiceReport:
    """Tests for voice/speech analysis."""

    def test_voice_report_success(self, sample_voice_response: dict[str, Any]):
        """Test successful voice analysis."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_voice_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.voice_report(b"fake-audio-data")

        assert result.id == "c3d4e5f6-a7b8-9012-cdef-123456789012"
        assert result.is_ai() is True
        mock_client.post.assert_called_once()

    def test_voice_report_from_file(
        self, sample_voice_response: dict[str, Any], temp_audio_file: Path
    ):
        """Test voice analysis from file."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_voice_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.voice_report_from_file(temp_audio_file)

        assert result.id == "c3d4e5f6-a7b8-9012-cdef-123456789012"

    def test_voice_report_timeout(self):
        """Test voice analysis timeout raises AIORNotTimeoutError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        client = Client(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotTimeoutError, match="timed out"):
            client.voice_report(b"fake-audio-data")


class TestMusicReport:
    """Tests for music analysis."""

    def test_music_report_success(self, sample_music_response: dict[str, Any]):
        """Test successful music analysis."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_music_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.music_report(b"fake-audio-data")

        assert result.id == "d4e5f6a7-b8c9-0123-def0-234567890123"
        assert result.is_ai() is False
        mock_client.post.assert_called_once()

    def test_music_report_from_file(
        self, sample_music_response: dict[str, Any], temp_audio_file: Path
    ):
        """Test music analysis from file."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_music_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.music_report_from_file(temp_audio_file)

        assert result.id == "d4e5f6a7-b8c9-0123-def0-234567890123"

    def test_music_report_timeout(self):
        """Test music analysis timeout raises AIORNotTimeoutError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        client = Client(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotTimeoutError, match="timed out"):
            client.music_report(b"fake-audio-data")


class TestTextReport:
    """Tests for text analysis."""

    def test_text_report_success(self, sample_text_response: dict[str, Any]):
        """Test successful text analysis."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_text_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.text_report("This is sample text for analysis.")

        assert result.id == "e5f6a7b8-c9d0-1234-ef01-345678901234"
        assert result.is_ai() is True
        mock_client.post.assert_called_once()

    def test_text_report_with_annotations(self, sample_text_response: dict[str, Any]):
        """Test text analysis with annotations requested."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = sample_text_response
        mock_client.post.return_value = mock_response

        client = Client(api_key="test-key", client=mock_client)
        result = client.text_report("Sample text", include_annotations=True)

        assert result.annotations is not None
        assert len(result.annotations) == 3

    def test_text_report_timeout(self):
        """Test text analysis timeout raises AIORNotTimeoutError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        client = Client(api_key="test-key", client=mock_client)
        with pytest.raises(AIORNotTimeoutError, match="timed out"):
            client.text_report("Test text")


class TestDirectoryBatch:
    """Tests for directory batch processing."""

    def test_image_report_directory_not_found(self):
        """Test directory not found raises AIORNotFileError."""
        client = Client(api_key="test-key")
        with pytest.raises(AIORNotFileError, match="Directory not found"):
            client.image_report_directory("/nonexistent/directory")


class TestCsvBatch:
    """Tests for CSV batch processing."""

    def test_image_report_from_csv(self, tmp_path: Path, sample_image_response):
        """Test processing images from CSV."""
        # Create CSV file
        csv_file = tmp_path / "files.csv"
        csv_file.write_text("file_path\nimage1.jpg\nimage2.jpg\n")

        # Create mock files
        (tmp_path / "image1.jpg").write_bytes(b"fake-image-1")
        (tmp_path / "image2.jpg").write_bytes(b"fake-image-2")

        with patch.object(Client, "image_report_batch") as mock_batch:
            mock_batch.return_value = MagicMock()
            client = Client(api_key="test-key")
            client.image_report_from_csv(csv_file, base_directory=tmp_path)

            mock_batch.assert_called_once()
            # Verify two files were passed
            call_args = mock_batch.call_args
            assert len(call_args[0][0]) == 2
