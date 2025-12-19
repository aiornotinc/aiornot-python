"""Common/shared types used across multiple response types."""

from typing import Literal

from pydantic import BaseModel, Field


class PredictionBase(BaseModel):
    """Base prediction with detection flag and confidence score."""

    is_detected: bool
    confidence: float = Field(ge=0, le=1)


class GeneratorPrediction(BaseModel):
    """Prediction for a specific AI generator."""

    is_detected: bool
    confidence: float = Field(ge=0, le=1)


class GeneratorScheme(BaseModel):
    """Predictions for known AI image generators."""

    midjourney: GeneratorPrediction
    dall_e: GeneratorPrediction
    stable_diffusion: GeneratorPrediction
    this_person_does_not_exist: GeneratorPrediction
    adobe_firefly: GeneratorPrediction
    flux: GeneratorPrediction
    four_o: GeneratorPrediction

    model_config = {"extra": "allow"}


class AIGeneratedReport(BaseModel):
    """AI generated detection report."""

    verdict: Literal["ai", "human", "unknown"]
    ai: PredictionBase
    human: PredictionBase
    generator: GeneratorScheme | None = None


class BBox(BaseModel):
    """Bounding box coordinates."""

    x1: int
    y1: int
    x2: int
    y2: int


class RoiReport(BaseModel):
    """Region of interest report with bounding box."""

    is_detected: bool
    confidence: float = Field(ge=0, le=1)
    bbox: BBox


class DeepfakeReport(BaseModel):
    """Deepfake detection report."""

    is_detected: bool
    confidence: float = Field(ge=0, le=1)
    rois: list[RoiReport] = Field(default_factory=list)


class DeepfakeVideoReport(BaseModel):
    """Deepfake video detection report."""

    is_detected: bool
    confidence: float = Field(ge=0, le=1)
    no_faces_found: bool = False


class NSFWReport(BaseModel):
    """NSFW content detection report."""

    is_detected: bool
    version: str = "1.0.0"


class QualityReport(BaseModel):
    """Image quality report."""

    is_detected: bool


class ReverseSearchMatch(BaseModel):
    """A match found during reverse image search."""

    domain: str
    image_url: str
    width: int
    height: int
    earliest_crawl_date: str
    earliest_backlink: str


class ReverseSearchReport(BaseModel):
    """Reverse image search report."""

    was_found: bool
    matches: list[ReverseSearchMatch] = Field(default_factory=list)
