"""Shared pytest fixtures for AIORNOT tests."""

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture file."""
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


@pytest.fixture
def sample_image_response() -> dict[str, Any]:
    """Load sample image analysis response."""
    return load_fixture("image_response.json")


@pytest.fixture
def sample_video_response() -> dict[str, Any]:
    """Load sample video analysis response."""
    return load_fixture("video_response.json")


@pytest.fixture
def sample_voice_response() -> dict[str, Any]:
    """Load sample voice analysis response."""
    return load_fixture("voice_response.json")


@pytest.fixture
def sample_music_response() -> dict[str, Any]:
    """Load sample music analysis response."""
    return load_fixture("music_response.json")


@pytest.fixture
def sample_text_response() -> dict[str, Any]:
    """Load sample text analysis response."""
    return load_fixture("text_response.json")


@pytest.fixture
def mock_httpx_response() -> MagicMock:
    """Create a mock httpx response factory."""

    def _create_response(
        status_code: int = 200,
        json_data: dict[str, Any] | None = None,
        text: str = "",
    ) -> MagicMock:
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.is_success = 200 <= status_code < 300
        response.text = text or json.dumps(json_data or {})
        response.json.return_value = json_data or {}
        return response

    return _create_response


@pytest.fixture
def mock_httpx_client(mock_httpx_response) -> MagicMock:
    """Create a mock httpx.Client for testing sync client."""
    client = MagicMock(spec=httpx.Client)
    return client


@pytest.fixture
def mock_async_httpx_client(mock_httpx_response) -> MagicMock:
    """Create a mock httpx.AsyncClient for testing async client."""
    client = MagicMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def api_key() -> str:
    """Get API key from environment or skip test."""
    key = os.environ.get("AIORNOT_API_KEY")
    if not key:
        pytest.skip("AIORNOT_API_KEY not set")
    return key


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Sample image bytes for testing."""
    # Minimal valid JPEG header
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"


@pytest.fixture
def sample_audio_bytes() -> bytes:
    """Sample audio bytes for testing."""
    # Minimal valid MP3 header (ID3 tag)
    return b"ID3\x04\x00\x00\x00\x00\x00\x00"


@pytest.fixture
def sample_video_bytes() -> bytes:
    """Sample video bytes for testing."""
    # Minimal MP4 header
    return b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41"


@pytest.fixture
def temp_image_file(tmp_path: Path, sample_image_bytes: bytes) -> Path:
    """Create a temporary image file for testing."""
    file_path = tmp_path / "test_image.jpg"
    file_path.write_bytes(sample_image_bytes)
    return file_path


@pytest.fixture
def temp_audio_file(tmp_path: Path, sample_audio_bytes: bytes) -> Path:
    """Create a temporary audio file for testing."""
    file_path = tmp_path / "test_audio.mp3"
    file_path.write_bytes(sample_audio_bytes)
    return file_path


@pytest.fixture
def temp_video_file(tmp_path: Path, sample_video_bytes: bytes) -> Path:
    """Create a temporary video file for testing."""
    file_path = tmp_path / "test_video.mp4"
    file_path.write_bytes(sample_video_bytes)
    return file_path
