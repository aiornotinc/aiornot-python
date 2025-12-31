"""Tests for request builder functions."""

from aiornot.req_builders import (
    image_report_args,
    is_live_args,
    music_report_args,
    text_report_args,
    video_report_args,
    voice_report_args,
)
from aiornot.types.enums import ImageAnalysisType, VideoAnalysisType


class TestIsLiveArgs:
    """Tests for is_live_args builder."""

    def test_builds_correct_url(self):
        """Test health check URL is built correctly."""
        args = is_live_args("https://api.aiornot.com")
        assert args["url"] == "https://api.aiornot.com/v1/system/live"

    def test_default_timeout(self):
        """Test default timeout is 5 seconds."""
        args = is_live_args("https://api.aiornot.com")
        assert args["timeout"] == 5

    def test_custom_timeout(self):
        """Test custom timeout is respected."""
        args = is_live_args("https://api.aiornot.com", timeout=10)
        assert args["timeout"] == 10


class TestImageReportArgs:
    """Tests for image_report_args builder."""

    def test_builds_correct_url(self):
        """Test image report URL is built correctly."""
        args = image_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["url"] == "https://api.aiornot.com/v2/image/sync"

    def test_includes_auth_header(self):
        """Test authorization header is included."""
        args = image_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["headers"]["Authorization"] == "Bearer test-key"

    def test_includes_image_data(self):
        """Test image data is included in files."""
        args = image_report_args(
            data=b"fake-image-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["files"]["image"] == b"fake-image-data"

    def test_default_timeout(self):
        """Test default timeout is 180 seconds."""
        args = image_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["timeout"] == 180

    def test_custom_timeout(self):
        """Test custom timeout is respected."""
        args = image_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            timeout=60,
        )
        assert args["timeout"] == 60

    def test_no_params_by_default(self):
        """Test params is None when no filters specified."""
        args = image_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["params"] is None

    def test_only_filter(self):
        """Test only parameter filters analysis types."""
        args = image_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            only=[ImageAnalysisType.AI_GENERATED, ImageAnalysisType.DEEPFAKE],
        )
        assert args["params"]["only"] == ["ai_generated", "deepfake"]

    def test_excluding_filter(self):
        """Test excluding parameter filters analysis types."""
        args = image_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            excluding=[ImageAnalysisType.NSFW],
        )
        assert args["params"]["excluding"] == ["nsfw"]

    def test_external_id(self):
        """Test external_id is included in params."""
        args = image_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            external_id="my-custom-id",
        )
        assert args["params"]["external_id"] == "my-custom-id"


class TestVideoReportArgs:
    """Tests for video_report_args builder."""

    def test_builds_correct_url(self):
        """Test video report URL is built correctly."""
        args = video_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["url"] == "https://api.aiornot.com/v2/video/sync"

    def test_includes_auth_header(self):
        """Test authorization header is included."""
        args = video_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["headers"]["Authorization"] == "Bearer test-key"

    def test_includes_video_data(self):
        """Test video data is included in files."""
        args = video_report_args(
            data=b"fake-video-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["files"]["video"] == b"fake-video-data"

    def test_only_filter(self):
        """Test only parameter filters analysis types."""
        args = video_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            only=[VideoAnalysisType.AI_VIDEO],
        )
        assert args["params"]["only"] == ["ai_video"]

    def test_excluding_filter(self):
        """Test excluding parameter filters analysis types."""
        args = video_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            excluding=[VideoAnalysisType.AI_VOICE, VideoAnalysisType.AI_MUSIC],
        )
        assert args["params"]["excluding"] == ["ai_voice", "ai_music"]


class TestVoiceReportArgs:
    """Tests for voice_report_args builder."""

    def test_builds_correct_url(self):
        """Test voice report URL is built correctly."""
        args = voice_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["url"] == "https://api.aiornot.com/v1/reports/voice"

    def test_includes_auth_header(self):
        """Test authorization header is included."""
        args = voice_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["headers"]["Authorization"] == "Bearer test-key"

    def test_default_filename(self):
        """Test default filename is audio.mp3."""
        args = voice_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        # Files should be (filename, data) tuple
        assert args["files"]["file"][0] == "audio.mp3"

    def test_custom_filename(self):
        """Test custom filename is respected."""
        args = voice_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            filename="my_recording.wav",
        )
        assert args["files"]["file"][0] == "my_recording.wav"

    def test_includes_audio_data(self):
        """Test audio data is included in files."""
        args = voice_report_args(
            data=b"fake-audio-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["files"]["file"][1] == b"fake-audio-data"


class TestMusicReportArgs:
    """Tests for music_report_args builder."""

    def test_builds_correct_url(self):
        """Test music report URL is built correctly."""
        args = music_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["url"] == "https://api.aiornot.com/v1/reports/music"

    def test_includes_auth_header(self):
        """Test authorization header is included."""
        args = music_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["headers"]["Authorization"] == "Bearer test-key"

    def test_default_filename(self):
        """Test default filename is audio.mp3."""
        args = music_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["files"]["file"][0] == "audio.mp3"

    def test_custom_filename(self):
        """Test custom filename is respected."""
        args = music_report_args(
            data=b"fake-data",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            filename="song.mp3",
        )
        assert args["files"]["file"][0] == "song.mp3"


class TestTextReportArgs:
    """Tests for text_report_args builder."""

    def test_builds_correct_url(self):
        """Test text report URL is built correctly."""
        args = text_report_args(
            text="Sample text",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["url"] == "https://api.aiornot.com/v2/text/sync"

    def test_includes_auth_header(self):
        """Test authorization header is included."""
        args = text_report_args(
            text="Sample text",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["headers"]["Authorization"] == "Bearer test-key"

    def test_includes_content_type(self):
        """Test content-type header is form-urlencoded."""
        args = text_report_args(
            text="Sample text",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["headers"]["Content-Type"] == "application/x-www-form-urlencoded"

    def test_includes_text_data(self):
        """Test text is included in data."""
        args = text_report_args(
            text="This is my sample text",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        assert args["data"]["text"] == "This is my sample text"

    def test_default_no_annotations(self):
        """Test annotations are not requested by default."""
        args = text_report_args(
            text="Sample text",
            api_key="test-key",
            base_url="https://api.aiornot.com",
        )
        # When include_annotations is False (default), it should still be in params
        # because we explicitly pass it
        assert args["params"]["include_annotations"] is False

    def test_include_annotations(self):
        """Test annotations can be requested."""
        args = text_report_args(
            text="Sample text",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            include_annotations=True,
        )
        assert args["params"]["include_annotations"] is True

    def test_external_id(self):
        """Test external_id is included in params."""
        args = text_report_args(
            text="Sample text",
            api_key="test-key",
            base_url="https://api.aiornot.com",
            external_id="my-text-id",
        )
        assert args["params"]["external_id"] == "my-text-id"
