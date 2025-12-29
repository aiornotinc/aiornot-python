"""Text report response types for v2 API."""

from datetime import datetime

from pydantic import BaseModel, Field


class TextMetadata(BaseModel):
    """Metadata about the analyzed text."""

    word_count: int
    character_count: int
    token_count: int
    md5: str


class AITextReport(BaseModel):
    """AI text detection report."""

    is_detected: bool
    confidence: float = Field(ge=0, le=1)
    annotations: list[tuple[str, float]] | None = None


class TextReport(BaseModel):
    """Text analysis report."""

    ai_text: AITextReport


class TextReportResponse(BaseModel):
    """Full response from v2 text analysis endpoint."""

    id: str
    created_at: datetime | None = None
    report: TextReport
    metadata: TextMetadata
    external_id: str | None = None

    model_config = {"extra": "allow"}

    @property
    def is_detected(self) -> bool:
        """Check if AI-generated text was detected."""
        return self.report.ai_text.is_detected

    @property
    def confidence(self) -> float:
        """Get the AI detection confidence score."""
        return self.report.ai_text.confidence

    def is_ai(self) -> bool:
        """Check if the text is detected as AI-generated."""
        return self.report.ai_text.is_detected

    @property
    def annotations(self) -> list[tuple[str, float]] | None:
        """Get block-level annotations if available."""
        return self.report.ai_text.annotations
