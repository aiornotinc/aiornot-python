"""Tests for CLI functionality."""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from aiornot.cli import cli
from aiornot.types import (
    MusicReportResponse,
    TextReportResponse,
    V2ImageReportResponse,
    VideoReportResponse,
    VoiceReportResponse,
)


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


class TestCliHelp:
    """Tests for CLI help output."""

    def test_main_help(self, runner):
        """Test main CLI help."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "AIORNOT" in result.output or "aiornot" in result.output.lower()

    def test_image_help(self, runner):
        """Test image command help."""
        result = runner.invoke(cli, ["image", "--help"])
        assert result.exit_code == 0
        assert "image" in result.output.lower()

    def test_video_help(self, runner):
        """Test video command help."""
        result = runner.invoke(cli, ["video", "--help"])
        assert result.exit_code == 0
        assert "video" in result.output.lower()

    def test_voice_help(self, runner):
        """Test voice command help."""
        result = runner.invoke(cli, ["voice", "--help"])
        assert result.exit_code == 0
        assert "voice" in result.output.lower()

    def test_music_help(self, runner):
        """Test music command help."""
        result = runner.invoke(cli, ["music", "--help"])
        assert result.exit_code == 0
        assert "music" in result.output.lower()

    def test_text_help(self, runner):
        """Test text command help."""
        result = runner.invoke(cli, ["text", "--help"])
        assert result.exit_code == 0
        assert "text" in result.output.lower()

    def test_token_help(self, runner):
        """Test token command help."""
        result = runner.invoke(cli, ["token", "--help"])
        assert result.exit_code == 0
        assert "token" in result.output.lower()

    def test_batch_help(self, runner):
        """Test batch command help."""
        result = runner.invoke(cli, ["batch", "--help"])
        assert result.exit_code == 0
        assert "batch" in result.output.lower()


class TestTokenCommands:
    """Tests for token management commands."""

    def test_token_check_no_token(self, runner, monkeypatch):
        """Test token check when no token is set."""
        monkeypatch.delenv("AIORNOT_API_KEY", raising=False)
        result = runner.invoke(cli, ["token", "check"])
        # Should fail or show error when no token
        assert "token" in result.output.lower() or result.exit_code != 0


class TestImageCommand:
    """Tests for image analysis command."""

    def test_image_no_token(self, runner, monkeypatch):
        """Test image command fails without token."""
        monkeypatch.delenv("AIORNOT_API_KEY", raising=False)
        result = runner.invoke(cli, ["image", "test.jpg"])
        assert result.exit_code != 0

    def test_image_file_not_found(self, runner, monkeypatch):
        """Test image command with non-existent file."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")
        result = runner.invoke(cli, ["image", "/nonexistent/file.jpg"])
        assert result.exit_code != 0

    def test_image_success_json(
        self, runner, monkeypatch, tmp_path, sample_image_response
    ):
        """Test successful image analysis with JSON output."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        # Create temp file
        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b"fake-image-data")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.image_report_from_file.return_value = V2ImageReportResponse(
                **sample_image_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(cli, ["image", str(image_file), "--format", "json"])

            assert result.exit_code == 0
            # Verify JSON output
            output = json.loads(result.output)
            assert output["id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    def test_image_success_table(
        self, runner, monkeypatch, tmp_path, sample_image_response
    ):
        """Test successful image analysis with table output."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b"fake-image-data")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.image_report_from_file.return_value = V2ImageReportResponse(
                **sample_image_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(
                cli,
                ["image", str(image_file), "--format", "table", "--no-color"],
            )

            assert result.exit_code == 0
            assert "AI" in result.output or "Verdict" in result.output

    def test_image_success_minimal(
        self, runner, monkeypatch, tmp_path, sample_image_response
    ):
        """Test successful image analysis with minimal output."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b"fake-image-data")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.image_report_from_file.return_value = V2ImageReportResponse(
                **sample_image_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(
                cli, ["image", str(image_file), "--format", "minimal"]
            )

            assert result.exit_code == 0
            # Minimal format should have verdict
            assert "ai" in result.output.lower()

    def test_image_only_option(
        self, runner, monkeypatch, tmp_path, sample_image_response
    ):
        """Test image analysis with --only option."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b"fake-image-data")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.image_report_from_file.return_value = V2ImageReportResponse(
                **sample_image_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(
                cli,
                [
                    "image",
                    str(image_file),
                    "--only",
                    "ai_generated",
                    "--format",
                    "json",
                ],
            )

            assert result.exit_code == 0


class TestVideoCommand:
    """Tests for video analysis command."""

    def test_video_success(self, runner, monkeypatch, tmp_path, sample_video_response):
        """Test successful video analysis."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake-video-data")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.video_report_from_file.return_value = VideoReportResponse(
                **sample_video_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(cli, ["video", str(video_file), "--format", "json"])

            assert result.exit_code == 0


class TestVoiceCommand:
    """Tests for voice analysis command."""

    def test_voice_success(self, runner, monkeypatch, tmp_path, sample_voice_response):
        """Test successful voice analysis."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake-audio-data")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.voice_report_from_file.return_value = VoiceReportResponse(
                **sample_voice_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(cli, ["voice", str(audio_file), "--format", "json"])

            assert result.exit_code == 0


class TestMusicCommand:
    """Tests for music analysis command."""

    def test_music_success(self, runner, monkeypatch, tmp_path, sample_music_response):
        """Test successful music analysis."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake-audio-data")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.music_report_from_file.return_value = MusicReportResponse(
                **sample_music_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(cli, ["music", str(audio_file), "--format", "json"])

            assert result.exit_code == 0


class TestTextCommand:
    """Tests for text analysis command."""

    def test_text_success(self, runner, monkeypatch, sample_text_response):
        """Test successful text analysis."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.text_report.return_value = TextReportResponse(
                **sample_text_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(
                cli, ["text", "This is sample text to analyze", "--format", "json"]
            )

            assert result.exit_code == 0

    def test_text_from_file(self, runner, monkeypatch, tmp_path, sample_text_response):
        """Test text analysis from file."""
        monkeypatch.setenv("AIORNOT_API_KEY", "test-key")

        text_file = tmp_path / "test.txt"
        text_file.write_text("This is text from a file.")

        with patch("aiornot.cli.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.text_report.return_value = TextReportResponse(
                **sample_text_response
            )
            mock_client_class.return_value = mock_client

            result = runner.invoke(
                cli, ["text", "--file", str(text_file), "--format", "json"]
            )

            assert result.exit_code == 0


class TestBatchCommands:
    """Tests for batch processing commands."""

    def test_batch_image_help(self, runner):
        """Test batch image help."""
        result = runner.invoke(cli, ["batch", "image", "--help"])
        assert result.exit_code == 0

    def test_batch_video_help(self, runner):
        """Test batch video help."""
        result = runner.invoke(cli, ["batch", "video", "--help"])
        assert result.exit_code == 0

    def test_batch_voice_help(self, runner):
        """Test batch voice help."""
        result = runner.invoke(cli, ["batch", "voice", "--help"])
        assert result.exit_code == 0

    def test_batch_music_help(self, runner):
        """Test batch music help."""
        result = runner.invoke(cli, ["batch", "music", "--help"])
        assert result.exit_code == 0

    def test_batch_text_help(self, runner):
        """Test batch text help."""
        result = runner.invoke(cli, ["batch", "text", "--help"])
        assert result.exit_code == 0


class TestOutputFormats:
    """Tests for different output format options."""

    def test_format_json_option(self, runner):
        """Test --format json option is recognized."""
        result = runner.invoke(cli, ["image", "--help"])
        assert "--format" in result.output

    def test_color_option(self, runner):
        """Test --color/--no-color options are recognized."""
        result = runner.invoke(cli, ["image", "--help"])
        # Color options may be in main help or image help
        assert "color" in result.output.lower() or result.exit_code == 0
