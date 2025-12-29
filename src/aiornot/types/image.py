"""Image report response types for v2 API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from aiornot.types.common import (
    AIGeneratedReport,
    DeepfakeReport,
    NSFWReport,
    QualityReport,
    ReverseSearchReport,
)
from aiornot.types.enums import ReportStatus


class ImageMetadata(BaseModel):
    """Metadata about the analyzed image."""

    width: int | None = None
    height: int | None = None
    format: str | None = None
    size_bytes: int | None = None
    md5: str | None = None
    processing_status: dict[str, ReportStatus] = Field(default_factory=dict)


class V2ImageReport(BaseModel):
    """V2 image analysis report containing all analysis types."""

    ai_generated: AIGeneratedReport | None = None
    deepfake: DeepfakeReport | None = None
    nsfw: NSFWReport | None = None
    quality: QualityReport | None = None
    reverse_search: ReverseSearchReport | None = None
    meta: ImageMetadata

    model_config = {"extra": "allow"}


class V2ImageReportResponse(BaseModel):
    """Full response from v2 image analysis endpoint."""

    id: str
    created_at: datetime | None = None
    report: V2ImageReport
    external_id: str | None = None

    model_config = {"extra": "allow"}

    @property
    def verdict(self) -> Literal["ai", "human", "unknown"] | None:
        """Get the AI detection verdict."""
        if self.report.ai_generated:
            return self.report.ai_generated.verdict
        return None

    @property
    def confidence(self) -> float | None:
        """Get the AI detection confidence score."""
        if self.report.ai_generated:
            return self.report.ai_generated.ai.confidence
        return None

    def is_ai(self) -> bool:
        """Check if the image is detected as AI-generated."""
        return self.verdict == "ai"

    def is_deepfake(self) -> bool:
        """Check if deepfake was detected."""
        if self.report.deepfake:
            return self.report.deepfake.is_detected
        return False

    def is_nsfw(self) -> bool:
        """Check if NSFW content was detected."""
        if self.report.nsfw:
            return self.report.nsfw.is_detected
        return False
