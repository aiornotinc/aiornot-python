"""AIORNOT API response types."""

from aiornot.types.batch import BatchResult, BatchSummary
from aiornot.types.common import (
    AIGeneratedReport,
    BBox,
    DeepfakeReport,
    DeepfakeVideoReport,
    GeneratorPrediction,
    GeneratorScheme,
    NSFWReport,
    PredictionBase,
    QualityReport,
    ReverseSearchMatch,
    ReverseSearchReport,
    RoiReport,
)
from aiornot.types.enums import (
    ImageAnalysisType,
    ReportStatus,
    Verdict,
    VideoAnalysisType,
)
from aiornot.types.image import (
    ImageMetadata,
    V2ImageReport,
    V2ImageReportResponse,
)
from aiornot.types.music import MusicReport, MusicReportResponse
from aiornot.types.text import (
    AITextReport,
    TextMetadata,
    TextReport,
    TextReportResponse,
)
from aiornot.types.video import VideoMetadata, VideoReport, VideoReportResponse
from aiornot.types.voice import VoiceReport, VoiceReportResponse

__all__ = [
    # Enums
    "ImageAnalysisType",
    "VideoAnalysisType",
    "Verdict",
    "ReportStatus",
    # Common types
    "PredictionBase",
    "GeneratorPrediction",
    "GeneratorScheme",
    "AIGeneratedReport",
    "BBox",
    "RoiReport",
    "DeepfakeReport",
    "DeepfakeVideoReport",
    "NSFWReport",
    "QualityReport",
    "ReverseSearchMatch",
    "ReverseSearchReport",
    # Image types
    "ImageMetadata",
    "V2ImageReport",
    "V2ImageReportResponse",
    # Video types
    "VideoMetadata",
    "VideoReport",
    "VideoReportResponse",
    # Voice types
    "VoiceReport",
    "VoiceReportResponse",
    # Music types
    "MusicReport",
    "MusicReportResponse",
    # Text types
    "AITextReport",
    "TextMetadata",
    "TextReport",
    "TextReportResponse",
    # Batch types
    "BatchResult",
    "BatchSummary",
]
