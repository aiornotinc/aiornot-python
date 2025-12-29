"""Music report response types for v1 API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MusicReport(BaseModel):
    """Music analysis report."""

    verdict: Literal["ai", "human"]
    confidence: float = Field(ge=0, le=1)
    duration: int
    total_bytes: int
    md5: str


class MusicReportResponse(BaseModel):
    """Full response from v1 music analysis endpoint."""

    id: str
    created_at: datetime | None = None
    report: MusicReport

    model_config = {"extra": "allow"}

    @property
    def verdict(self) -> Literal["ai", "human"]:
        """Get the AI detection verdict."""
        return self.report.verdict

    @property
    def confidence(self) -> float:
        """Get the AI detection confidence score."""
        return self.report.confidence

    def is_ai(self) -> bool:
        """Check if the music is detected as AI-generated."""
        return self.report.verdict == "ai"
