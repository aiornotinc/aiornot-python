from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class BaseReport(BaseModel):
    is_detected: bool
    confidence: float | None = None


class ImageReport(BaseModel):
    verdict: Literal["ai", "human"]
    ai: BaseReport
    human: BaseReport


class Facet(BaseModel):
    is_detected: bool
    version: str
    confidence: float | None = None


class ImageResp(BaseModel):
    id: str = Field(..., alias="id")
    created_at: datetime
    report: ImageReport
    facets: dict[str, Facet]

    def is_ai(self) -> bool:
        return self.report.verdict == "ai"


class CheckTokenResp(BaseModel):
    is_valid: bool
    expires_at: str | None = None


class RefreshTokenResp(BaseModel):
    token: str


class RevokeTokenResp(BaseModel):
    is_revoked: bool


class AudioReport(BaseModel):
    verdict: Literal["ai", "human"]


class AudioResp(BaseModel):
    id: str
    created_at: datetime
    report: AudioReport
