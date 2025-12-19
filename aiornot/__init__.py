"""AIORNOT Python Client - AI content detection API."""

from aiornot.async_client import AsyncClient
from aiornot.exceptions import (
    AIORNotAPIError,
    AIORNotAuthenticationError,
    AIORNotError,
    AIORNotFileError,
    AIORNotRateLimitError,
    AIORNotServerError,
    AIORNotTimeoutError,
    AIORNotValidationError,
)
from aiornot.sync_client import Client
from aiornot.types import (
    BatchResult,
    BatchSummary,
    ImageAnalysisType,
    MusicReportResponse,
    TextReportResponse,
    V2ImageReportResponse,
    VideoAnalysisType,
    VideoReportResponse,
    VoiceReportResponse,
)

__all__ = [
    # Clients
    "Client",
    "AsyncClient",
    # Response types
    "V2ImageReportResponse",
    "VideoReportResponse",
    "VoiceReportResponse",
    "MusicReportResponse",
    "TextReportResponse",
    # Batch types
    "BatchResult",
    "BatchSummary",
    # Enums
    "ImageAnalysisType",
    "VideoAnalysisType",
    # Exceptions
    "AIORNotError",
    "AIORNotAPIError",
    "AIORNotAuthenticationError",
    "AIORNotValidationError",
    "AIORNotRateLimitError",
    "AIORNotServerError",
    "AIORNotTimeoutError",
    "AIORNotFileError",
]
