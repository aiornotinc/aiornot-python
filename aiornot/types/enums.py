"""Enum types for AIORNOT API analysis types."""

from enum import Enum


class ImageAnalysisType(str, Enum):
    """Analysis types available for image reports."""

    AI_GENERATED = "ai_generated"
    DEEPFAKE = "deepfake"
    NSFW = "nsfw"
    QUALITY = "quality"
    REVERSE_SEARCH = "reverse_search"


class VideoAnalysisType(str, Enum):
    """Analysis types available for video reports."""

    AI_VIDEO = "ai_video"
    AI_MUSIC = "ai_music"
    AI_VOICE = "ai_voice"
    DEEPFAKE_VIDEO = "deepfake_video"


class Verdict(str, Enum):
    """Verdict for AI detection."""

    AI = "ai"
    HUMAN = "human"
    UNKNOWN = "unknown"


class ReportStatus(str, Enum):
    """Processing status for individual report types."""

    PROCESSED = "processed"
    REJECTED = "rejected"
    ERRORED = "errored"
