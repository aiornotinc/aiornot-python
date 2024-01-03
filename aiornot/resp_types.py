from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class BaseReport(BaseModel):
    is_detected: bool
    confidence: float = -1


class ImageReport(BaseModel):
    verdict: Literal["ai", "human"]
    ai: BaseReport
    human: BaseReport
    # Generator is an empty dict if the image is human
    generator: dict[str, BaseReport] = Field(default_factory=dict)


class Facet(BaseModel):
    is_detected: bool
    version: str
    confidence: float = -1


class ImageResp(BaseModel):
    id: str = Field(..., alias="id")
    created_at: datetime
    report: ImageReport
    facets: dict[str, Facet]

    def is_ai(self) -> bool:
        return self.report.verdict == "ai"


class CheckTokenResp(BaseModel):
    is_valid: bool
    expires_at: Optional[str] = None


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
