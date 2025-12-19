"""Tests for response type parsing."""

import json
from pathlib import Path

import pytest

from aiornot.types import (
    MusicReportResponse,
    TextReportResponse,
    V2ImageReportResponse,
    VideoReportResponse,
    VoiceReportResponse,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a JSON fixture file."""
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


class TestV2ImageReportResponse:
    """Tests for V2 image response parsing."""

    def test_parse_full_response(self):
        """Test parsing a complete image response."""
        data = load_fixture("image_response.json")
        resp = V2ImageReportResponse(**data)

        assert resp.id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        assert resp.external_id == "test-external-id"
        assert resp.verdict == "ai"
        assert resp.is_ai() is True
        assert resp.confidence == pytest.approx(0.952, rel=0.001)

    def test_ai_generated_report(self):
        """Test AI generated detection parsing."""
        data = load_fixture("image_response.json")
        resp = V2ImageReportResponse(**data)

        ai_gen = resp.report.ai_generated
        assert ai_gen is not None
        assert ai_gen.verdict == "ai"
        assert ai_gen.ai.is_detected is True
        assert ai_gen.human.is_detected is False

    def test_generator_prediction(self):
        """Test generator prediction parsing."""
        data = load_fixture("image_response.json")
        resp = V2ImageReportResponse(**data)

        gen = resp.report.ai_generated.generator
        assert gen is not None
        assert gen.midjourney.is_detected is True
        assert gen.midjourney.confidence == pytest.approx(0.85, rel=0.001)
        assert gen.dall_e.is_detected is False

    def test_deepfake_report(self):
        """Test deepfake detection parsing."""
        data = load_fixture("image_response.json")
        resp = V2ImageReportResponse(**data)

        assert resp.is_deepfake() is False
        assert resp.report.deepfake is not None
        assert resp.report.deepfake.confidence == pytest.approx(0.12, rel=0.001)

    def test_nsfw_report(self):
        """Test NSFW detection parsing."""
        data = load_fixture("image_response.json")
        resp = V2ImageReportResponse(**data)

        assert resp.is_nsfw() is False

    def test_metadata(self):
        """Test image metadata parsing."""
        data = load_fixture("image_response.json")
        resp = V2ImageReportResponse(**data)

        meta = resp.report.meta
        assert meta.width == 1024
        assert meta.height == 768
        assert meta.format == "jpeg"


class TestVideoReportResponse:
    """Tests for video response parsing."""

    def test_parse_response(self):
        """Test parsing a video response."""
        data = load_fixture("video_response.json")
        resp = VideoReportResponse(**data)

        assert resp.id == "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        assert resp.ai_video_detected is True
        assert resp.ai_video_confidence == pytest.approx(0.89, rel=0.001)

    def test_audio_tracks(self):
        """Test audio track detection."""
        data = load_fixture("video_response.json")
        resp = VideoReportResponse(**data)

        assert resp.ai_voice_detected is False
        assert resp.ai_music_detected is False

    def test_metadata(self):
        """Test video metadata parsing."""
        data = load_fixture("video_response.json")
        resp = VideoReportResponse(**data)

        assert resp.report.meta.duration == 45


class TestVoiceReportResponse:
    """Tests for voice response parsing."""

    def test_parse_response(self):
        """Test parsing a voice response."""
        data = load_fixture("voice_response.json")
        resp = VoiceReportResponse(**data)

        assert resp.id == "c3d4e5f6-a7b8-9012-cdef-123456789012"
        assert resp.verdict == "ai"
        assert resp.is_ai() is True
        assert resp.confidence == pytest.approx(0.78, rel=0.001)


class TestMusicReportResponse:
    """Tests for music response parsing."""

    def test_parse_response(self):
        """Test parsing a music response."""
        data = load_fixture("music_response.json")
        resp = MusicReportResponse(**data)

        assert resp.id == "d4e5f6a7-b8c9-0123-def0-234567890123"
        assert resp.verdict == "human"
        assert resp.is_ai() is False
        assert resp.confidence == pytest.approx(0.92, rel=0.001)


class TestTextReportResponse:
    """Tests for text response parsing."""

    def test_parse_response(self):
        """Test parsing a text response."""
        data = load_fixture("text_response.json")
        resp = TextReportResponse(**data)

        assert resp.id == "e5f6a7b8-c9d0-1234-ef01-345678901234"
        assert resp.is_detected is True
        assert resp.is_ai() is True
        assert resp.confidence == pytest.approx(0.85, rel=0.001)

    def test_annotations(self):
        """Test text annotations parsing."""
        data = load_fixture("text_response.json")
        resp = TextReportResponse(**data)

        annotations = resp.annotations
        assert annotations is not None
        assert len(annotations) == 3
        assert annotations[0][1] == pytest.approx(0.92, rel=0.001)

    def test_metadata(self):
        """Test text metadata parsing."""
        data = load_fixture("text_response.json")
        resp = TextReportResponse(**data)

        assert resp.metadata.word_count == 150
        assert resp.metadata.character_count == 850
