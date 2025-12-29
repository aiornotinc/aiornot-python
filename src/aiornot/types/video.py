"""Video report response types for v2 API."""

from datetime import datetime

from pydantic import BaseModel

from aiornot.types.common import DeepfakeVideoReport, PredictionBase


class VideoMetadata(BaseModel):
    """Metadata about the analyzed video."""

    duration: int
    total_bytes: int
    md5: str
    audio: str
    video: str


class VideoReport(BaseModel):
    """Video analysis report."""

    ai_video: PredictionBase
    ai_voice: PredictionBase | None = None
    ai_music: PredictionBase | None = None
    deepfake_video: DeepfakeVideoReport | None = None
    meta: VideoMetadata

    model_config = {"extra": "allow"}


class VideoReportResponse(BaseModel):
    """Full response from v2 video analysis endpoint."""

    id: str
    created_at: datetime | None = None
    report: VideoReport
    external_id: str | None = None

    model_config = {"extra": "allow"}

    @property
    def ai_video_detected(self) -> bool:
        """Check if AI-generated video was detected."""
        return self.report.ai_video.is_detected

    @property
    def ai_video_confidence(self) -> float:
        """Get AI video detection confidence."""
        return self.report.ai_video.confidence

    @property
    def ai_voice_detected(self) -> bool | None:
        """Check if AI-generated voice was detected."""
        if self.report.ai_voice:
            return self.report.ai_voice.is_detected
        return None

    @property
    def ai_music_detected(self) -> bool | None:
        """Check if AI-generated music was detected."""
        if self.report.ai_music:
            return self.report.ai_music.is_detected
        return None

    @property
    def deepfake_detected(self) -> bool | None:
        """Check if deepfake video was detected."""
        if self.report.deepfake_video:
            return self.report.deepfake_video.is_detected
        return None
