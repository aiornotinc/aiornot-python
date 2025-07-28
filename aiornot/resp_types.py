from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Literal, Optional, List, Union
from datetime import datetime

ReportStatus = Literal["processed", "rejected", "errored"]


class BaseReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool
    confidence: float = -1


class Generator(BaseModel):
    model_config = ConfigDict(extra="allow")

    ai: Optional[BaseReport] = None
    human: Optional[BaseReport] = None
    midjourney: Optional[Union[BaseReport, float]] = None
    dall_e: Optional[Union[BaseReport, float]] = None
    stable_diffusion: Optional[Union[BaseReport, float]] = None
    this_person_does_not_exist: Optional[Union[BaseReport, float]] = None
    adobe_firefly: Optional[Union[BaseReport, float]] = None
    flux: Optional[Union[BaseReport, float]] = None
    four_o: Optional[Union[BaseReport, float]] = None
    nano_banana: Optional[Union[BaseReport, float]] = None


class AiGenerated(BaseModel):
    model_config = ConfigDict(extra="allow")

    verdict: Literal["ai", "human", "unknown"]
    ai: BaseReport
    human: BaseReport
    generator: Generator = Field(default_factory=Generator)


class BoundingBox(BaseModel):
    model_config = ConfigDict(extra="allow")

    x1: int
    y1: int
    x2: int
    y2: int


class ROI(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool
    confidence: float
    bbox: BoundingBox


class Deepfake(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool
    confidence: float
    rois: List[ROI] = Field(default_factory=list)


class NSFW(BaseModel):
    model_config = ConfigDict(extra="allow")

    version: Optional[str] = None
    is_detected: bool


class Quality(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool


class ReverseSearchMatch(BaseModel):
    model_config = ConfigDict(extra="allow")

    domain: str
    image_url: str
    width: Optional[int] = None
    height: Optional[int] = None
    earliest_crawl_date: Optional[str] = None
    earliest_backlink: Optional[str] = None


class ReverseSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    was_found: bool
    matches: List[ReverseSearchMatch] = Field(default_factory=list)


class ProcessingStatus(BaseModel):
    model_config = ConfigDict(extra="allow")

    ai_generated: Optional[ReportStatus] = None
    deepfake: Optional[ReportStatus] = None
    nsfw: Optional[ReportStatus] = None
    quality: Optional[ReportStatus] = None
    reverse_search: Optional[ReportStatus] = None


class Meta(BaseModel):
    model_config = ConfigDict(extra="allow")

    width: int
    height: int
    format: str
    size_bytes: int
    md5: str
    processing_status: ProcessingStatus


class ImageReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    ai_generated: Optional[AiGenerated] = None
    deepfake: Optional[Deepfake] = None
    nsfw: Optional[NSFW] = None
    quality: Optional[Quality] = None
    reverse_search: Optional[ReverseSearch] = None
    meta: Meta


class ImageResp(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    created_at: datetime
    report: ImageReport
    external_id: Optional[str] = None

    def is_ai(self) -> bool:
        return (
            self.report.ai_generated is not None
            and self.report.ai_generated.verdict == "ai"
        )


class CheckTokenResp(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_valid: bool
    expires_at: Optional[str] = None


# Text Response Types
class TextMeta(BaseModel):
    model_config = ConfigDict(extra="allow")

    word_count: int
    character_count: int
    token_count: int
    md5: Optional[str] = None


class AiText(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool
    confidence: float


class TextReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    ai_text: AiText


class TextResp(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    created_at: datetime
    report: TextReport
    metadata: TextMeta
    external_id: Optional[str] = None

    def is_ai(self) -> bool:
        return self.report.ai_text.is_detected


# V1 Voice/Music Response Types
AudioVerdict = Literal["ai", "human"]


class V1AudioReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    verdict: AudioVerdict
    confidence: float
    duration: int
    total_bytes: int
    md5: str
    generator: Optional[Any] = None


class VoiceResp(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    created_at: datetime
    report: V1AudioReport

    def is_ai(self) -> bool:
        return self.report.verdict == "ai"


class MusicResp(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    created_at: datetime
    report: V1AudioReport

    def is_ai(self) -> bool:
        return self.report.verdict == "ai"


# Video Response Types
class VideoProcessingStatus(BaseModel):
    model_config = ConfigDict(extra="allow")

    ai_video: Optional[ReportStatus] = None
    ai_music: Optional[ReportStatus] = None
    ai_voice: Optional[ReportStatus] = None
    deepfake_video: Optional[ReportStatus] = None


class VideoMeta(BaseModel):
    model_config = ConfigDict(extra="allow")

    duration: float
    total_bytes: int
    md5: str
    audio: ReportStatus
    video: ReportStatus
    processing_status: Optional[VideoProcessingStatus] = None


class AiVideo(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool
    confidence: float


class AiMusic(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool
    confidence: float


class AiVoice(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool
    confidence: float


class DeepfakeVideo(BaseModel):
    model_config = ConfigDict(extra="allow")

    is_detected: bool
    confidence: float
    no_faces_found: Optional[bool] = None


class VideoReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    ai_video: Optional[AiVideo] = None
    ai_music: Optional[AiMusic] = None
    ai_voice: Optional[AiVoice] = None
    deepfake_video: Optional[DeepfakeVideo] = None
    meta: VideoMeta


class VideoResp(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    created_at: datetime
    report: VideoReport
    external_id: Optional[str] = None

    def is_ai(self) -> bool:
        # Consider video AI if any component is detected as AI
        checks = []
        if self.report.ai_video:
            checks.append(self.report.ai_video.is_detected)
        if self.report.ai_music:
            checks.append(self.report.ai_music.is_detected)
        if self.report.ai_voice:
            checks.append(self.report.ai_voice.is_detected)
        if self.report.deepfake_video:
            checks.append(self.report.deepfake_video.is_detected)
        return any(checks) if checks else False
