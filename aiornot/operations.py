from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

from httpx import HTTPStatusError
from pydantic import BaseModel

from aiornot.sync_client import Client
from aiornot.validation import validate_external_id

IMAGE_EXTENSIONS = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}
TEXT_EXTENSIONS = {".csv", ".html", ".json", ".jsonl", ".md", ".rtf", ".text", ".txt"}
VIDEO_EXTENSIONS = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".webm"}
AUDIO_EXTENSIONS = {".aac", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".webm"}
DEFAULT_VIDEO_URL_OUTPUT_DIR = Path("aiornot-downloads")
DEFAULT_VIDEO_URL_MAX_DURATION_SECONDS = 120
DEFAULT_AUDIO_URL_MAX_DURATION_SECONDS = 3600
VIDEO_URL_OUTPUT_TEMPLATE = "%(title).200B [%(id)s].%(ext)s"


class MissingApiKeyError(RuntimeError):
    pass


@dataclass
class BatchJob:
    input_id: str
    modality: str
    source: str
    path: Optional[Path] = None
    text: Optional[str] = None
    row_number: Optional[int] = None
    relative_path: Optional[str] = None
    external_id: Optional[str] = None
    only: Optional[List[str]] = None
    excluding: Optional[List[str]] = None
    include_annotations: bool = False
    preflight_error: Optional[str] = None

    def input_record(self) -> Dict[str, object]:
        record: Dict[str, object] = {
            "id": self.input_id,
            "modality": self.modality,
            "source": self.source,
        }
        if self.path is not None:
            record["path"] = str(self.path)
        if self.row_number is not None:
            record["row_number"] = self.row_number
        if self.relative_path is not None:
            record["relative_path"] = self.relative_path
        if self.external_id is not None:
            record["external_id"] = self.external_id
        if self.only:
            record["only"] = self.only
        if self.excluding:
            record["excluding"] = self.excluding
        if self.modality == "text":
            record["include_annotations"] = self.include_annotations
            if self.text is not None:
                record["text_chars"] = len(self.text)
        return record


@dataclass
class BatchSummary:
    processed: int
    succeeded: int
    failed: int
    skipped: int
    output: Path


def load_api_key() -> Optional[str]:
    token = os.getenv("AIORNOT_API_TOKEN") or os.getenv("AIORNOT_API_KEY")
    if token is not None:
        return token

    config_path = Path.home() / ".aiornot" / "config.json"
    if config_path.exists():
        with config_path.open("r") as f:
            config = json.load(f)
            return config.get("api_token")

    raise MissingApiKeyError(
        "No API token found. Set AIORNOT_API_KEY or run `aiornot token config`."
    )


def save_api_key(api_key: str) -> None:
    config_path = Path.home() / ".aiornot" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"api_token": api_key}, f)
    os.chmod(config_path, 0o600)


def client_from_config() -> Client:
    return Client(load_api_key())


def require_file(source: str | Path) -> Path:
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File {source} does not exist.")
    if not path.is_file():
        raise ValueError(f"{source} is not a file.")
    return path


def model_to_record(model: BaseModel) -> Dict[str, object]:
    return model.model_dump(mode="json")


def check_token(client: Optional[Client] = None) -> Dict[str, object]:
    client = client or client_from_config()
    return model_to_record(client.check_token())


def analyze_image_file(
    source: str | Path,
    external_id: Optional[str] = None,
    only: Optional[List[str]] = None,
    excluding: Optional[List[str]] = None,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    client = client or client_from_config()
    return model_to_record(
        client.image_report_by_file_sync(
            require_file(source),
            external_id=external_id,
            only=only,
            excluding=excluding,
        )
    )


def analyze_text_value(
    text: str,
    external_id: Optional[str] = None,
    include_annotations: bool = False,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    client = client or client_from_config()
    return model_to_record(
        client.text_report_sync(
            text,
            external_id=external_id,
            include_annotations=include_annotations,
        )
    )


def analyze_text_file(
    source: str | Path,
    external_id: Optional[str] = None,
    include_annotations: bool = False,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    return analyze_text_value(
        require_file(source).read_text(),
        external_id=external_id,
        include_annotations=include_annotations,
        client=client,
    )


def analyze_video_file(
    source: str | Path,
    external_id: Optional[str] = None,
    only: Optional[List[str]] = None,
    excluding: Optional[List[str]] = None,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    client = client or client_from_config()
    return model_to_record(
        client.video_report_by_file_sync(
            require_file(source),
            external_id=external_id,
            only=only,
            excluding=excluding,
        )
    )


def analyze_video_url(
    url: str,
    output_dir: str | Path = DEFAULT_VIDEO_URL_OUTPUT_DIR,
    max_duration: int = DEFAULT_VIDEO_URL_MAX_DURATION_SECONDS,
    delete_after: bool = False,
    external_id: Optional[str] = None,
    only: Optional[List[str]] = None,
    excluding: Optional[List[str]] = None,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    client = client or client_from_config()
    downloaded_path = download_video_url(
        url,
        output_dir=output_dir,
        max_duration=max_duration,
    )
    deleted = False
    try:
        response = client.video_report_by_file_sync(
            require_file(downloaded_path),
            external_id=external_id,
            only=only,
            excluding=excluding,
        )
    finally:
        if delete_after and downloaded_path.exists():
            downloaded_path.unlink()
            deleted = True

    return {
        "download": {
            "url": url,
            "path": str(downloaded_path),
            "deleted": deleted,
            "max_duration": max_duration,
        },
        "response": model_to_record(response),
    }


def analyze_voice_url(
    url: str,
    output_dir: str | Path = DEFAULT_VIDEO_URL_OUTPUT_DIR,
    max_duration: int = DEFAULT_AUDIO_URL_MAX_DURATION_SECONDS,
    delete_after: bool = False,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    client = client or client_from_config()
    return _analyze_audio_url(
        url,
        output_dir=output_dir,
        max_duration=max_duration,
        delete_after=delete_after,
        analyze=client.voice_report_by_file_sync,
    )


def analyze_music_url(
    url: str,
    output_dir: str | Path = DEFAULT_VIDEO_URL_OUTPUT_DIR,
    max_duration: int = DEFAULT_AUDIO_URL_MAX_DURATION_SECONDS,
    delete_after: bool = False,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    client = client or client_from_config()
    return _analyze_audio_url(
        url,
        output_dir=output_dir,
        max_duration=max_duration,
        delete_after=delete_after,
        analyze=client.music_report_by_file_sync,
    )


def _analyze_audio_url(
    url: str,
    output_dir: str | Path,
    max_duration: int,
    delete_after: bool,
    analyze: Callable[[Path], BaseModel],
) -> Dict[str, object]:
    downloaded_path = download_audio_url(
        url,
        output_dir=output_dir,
        max_duration=max_duration,
    )
    deleted = False
    try:
        response = analyze(require_file(downloaded_path))
    finally:
        if delete_after and downloaded_path.exists():
            downloaded_path.unlink()
            deleted = True

    return {
        "download": {
            "url": url,
            "path": str(downloaded_path),
            "deleted": deleted,
            "max_duration": max_duration,
        },
        "response": model_to_record(response),
    }


def download_video_url(
    url: str,
    output_dir: str | Path = DEFAULT_VIDEO_URL_OUTPUT_DIR,
    max_duration: int = DEFAULT_VIDEO_URL_MAX_DURATION_SECONDS,
) -> Path:
    return _download_url(
        url,
        output_dir=output_dir,
        max_duration=max_duration,
        format_selector="bv*+ba/b",
    )


def download_audio_url(
    url: str,
    output_dir: str | Path = DEFAULT_VIDEO_URL_OUTPUT_DIR,
    max_duration: int = DEFAULT_AUDIO_URL_MAX_DURATION_SECONDS,
) -> Path:
    return _download_url(
        url,
        output_dir=output_dir,
        max_duration=max_duration,
        format_selector="ba",
    )


def _download_url(
    url: str,
    output_dir: str | Path,
    max_duration: int,
    format_selector: str,
) -> Path:
    if max_duration < 0:
        raise ValueError("max_duration must be 0 or greater")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    cmd = [
        "uvx",
        "yt-dlp@latest",
        "-f",
        format_selector,
        "--no-playlist",
        "--paths",
        str(output_path),
        "-o",
        VIDEO_URL_OUTPUT_TEMPLATE,
        "--print",
        "after_move:filepath",
    ]
    if max_duration > 0:
        cmd.extend(["--download-sections", f"*0:00-{max_duration}"])
    cmd.append(url)

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "`uvx` is required to download videos from URLs. Install uv from "
            "https://docs.astral.sh/uv/ and retry."
        ) from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or str(exc)).strip()
        raise RuntimeError(f"yt-dlp failed: {message}") from exc

    downloaded_path = _downloaded_path_from_yt_dlp_output(result.stdout)
    return require_file(downloaded_path)


def analyze_voice_file(
    source: str | Path,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    client = client or client_from_config()
    return model_to_record(client.voice_report_by_file_sync(require_file(source)))


def analyze_music_file(
    source: str | Path,
    client: Optional[Client] = None,
) -> Dict[str, object]:
    client = client or client_from_config()
    return model_to_record(client.music_report_by_file_sync(require_file(source)))


def csv_jobs(
    modality: str,
    csv_path: Path,
    path_column: str,
    id_column: str,
    text_column: str = "text",
    external_id: Optional[str] = None,
    only: Optional[List[str]] = None,
    excluding: Optional[List[str]] = None,
    include_annotations: bool = False,
) -> Iterable[BatchJob]:
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row_number, row in enumerate(reader, start=2):
            source = _row_value(row, path_column, "source", "file")
            literal_text = _row_value(row, text_column) if modality == "text" else None
            row_external_id = validate_external_id(
                _row_value(row, "external_id") or external_id
            )
            row_only = split_values(_row_value(row, "only")) or only
            row_excluding = split_values(_row_value(row, "excluding")) or excluding
            row_annotations = parse_bool(
                _row_value(row, "include_annotations"), include_annotations
            )

            preflight_error = None
            path = None
            if literal_text is None:
                if not source:
                    preflight_error = (
                        f"row must include '{path_column}', 'source', or 'file'"
                    )
                else:
                    path = Path(source)
                    if not path.is_absolute():
                        path = csv_path.parent / path

            input_id = (
                _row_value(row, id_column)
                or row_external_id
                or source
                or f"row-{row_number}"
            )
            yield BatchJob(
                input_id=input_id,
                modality=modality,
                source=source or f"row-{row_number}",
                path=path,
                text=literal_text,
                row_number=row_number,
                external_id=row_external_id,
                only=row_only,
                excluding=row_excluding,
                include_annotations=row_annotations,
                preflight_error=preflight_error,
            )


def scan_jobs(
    modality: str,
    folder: Path,
    extensions: List[str],
    recursive: bool,
    use_relpath_md5_as_external_id: bool = False,
    only: Optional[List[str]] = None,
    excluding: Optional[List[str]] = None,
    include_annotations: bool = False,
) -> Iterable[BatchJob]:
    paths = folder.rglob("*") if recursive else folder.glob("*")
    for path in sorted(paths):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        relative_path = path.relative_to(folder).as_posix()
        external_id = None
        if use_relpath_md5_as_external_id:
            external_id = hashlib.md5(relative_path.encode("utf-8")).hexdigest()
        yield BatchJob(
            input_id=relative_path,
            modality=modality,
            source=str(path),
            path=path,
            relative_path=relative_path,
            external_id=external_id,
            only=only,
            excluding=excluding,
            include_annotations=include_annotations,
        )


def run_batch(
    jobs: Iterable[BatchJob],
    output: Path,
    resume: bool,
    analyze: Callable[[BatchJob], BaseModel],
    progress: Optional[Callable[[Dict[str, object]], None]] = None,
) -> BatchSummary:
    output.parent.mkdir(parents=True, exist_ok=True)
    output_path = output.resolve()
    completed = completed_input_ids(output) if resume else set()
    processed = 0
    succeeded = 0
    failed = 0
    skipped = 0

    with output.open("a") as f:
        for job in jobs:
            if job.path is not None and job.path.resolve() == output_path:
                continue
            if job.input_id in completed:
                skipped += 1
                continue
            record = run_job(job, analyze)
            f.write(json.dumps(record, sort_keys=True) + "\n")
            f.flush()
            processed += 1
            if record.get("ok") is True:
                succeeded += 1
            else:
                failed += 1
            if progress is not None:
                progress(record)

    return BatchSummary(
        processed=processed,
        succeeded=succeeded,
        failed=failed,
        skipped=skipped,
        output=output,
    )


def run_job(
    job: BatchJob, analyze: Callable[[BatchJob], BaseModel]
) -> Dict[str, object]:
    record: Dict[str, object] = {"input": job.input_record(), "ok": False}
    try:
        if job.preflight_error:
            raise ValueError(job.preflight_error)
        response = analyze(job)
    except Exception as exc:  # noqa: BLE001 - batch output records per-row failures.
        record["error"] = error_record(exc)
    else:
        record["ok"] = True
        record["response"] = model_to_record(response)
    return record


def analyze_image_job(client: Client, job: BatchJob) -> BaseModel:
    return client.image_report_by_file_sync(
        existing_path(job),
        external_id=job.external_id,
        only=job.only,
        excluding=job.excluding,
    )


def analyze_text_job(client: Client, job: BatchJob) -> BaseModel:
    text_value = job.text if job.text is not None else existing_path(job).read_text()
    return client.text_report_sync(
        text_value,
        external_id=job.external_id,
        include_annotations=job.include_annotations,
    )


def analyze_video_job(client: Client, job: BatchJob) -> BaseModel:
    return client.video_report_by_file_sync(
        existing_path(job),
        external_id=job.external_id,
        only=job.only,
        excluding=job.excluding,
    )


def analyze_voice_job(client: Client, job: BatchJob) -> BaseModel:
    return client.voice_report_by_file_sync(existing_path(job))


def analyze_music_job(client: Client, job: BatchJob) -> BaseModel:
    return client.music_report_by_file_sync(existing_path(job))


def existing_path(job: BatchJob) -> Path:
    if job.path is None:
        raise ValueError("input path is required")
    return require_file(job.path)


def completed_input_ids(output: Path) -> set:
    if not output.exists():
        return set()
    completed = set()
    with output.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("ok") is True:
                input_id = record.get("input", {}).get("id")
                if input_id is not None:
                    completed.add(input_id)
    return completed


def error_record(exc: Exception) -> Dict[str, object]:
    error: Dict[str, object] = {
        "type": exc.__class__.__name__,
        "message": str(exc),
    }
    if isinstance(exc, HTTPStatusError):
        error["status_code"] = exc.response.status_code
        error["response"] = _response_body(exc)
    return error


def _downloaded_path_from_yt_dlp_output(stdout: str) -> Path:
    for line in reversed(stdout.splitlines()):
        value = line.strip()
        if value:
            return Path(value).expanduser()
    raise RuntimeError("yt-dlp did not report a downloaded file path")


def _response_body(exc: HTTPStatusError) -> object:
    try:
        return exc.response.json()
    except ValueError:
        return exc.response.text


def _row_value(row: Dict[str, str], *columns: str) -> Optional[str]:
    for column in columns:
        value = row.get(column)
        if value:
            return value
    return None


def split_values(value: Optional[str]) -> Optional[List[str]]:
    if value is None:
        return None
    normalized = value.replace(";", ",")
    values = [part.strip() for part in normalized.split(",") if part.strip()]
    return values or None


def parse_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def extensions(values: Iterable[str], defaults: set) -> List[str]:
    selected = values or defaults
    return sorted(
        value.lower() if value.startswith(".") else f".{value.lower()}"
        for value in selected
    )


def option_list(values: Iterable[str]) -> Optional[List[str]]:
    option_values = list(values)
    return option_values or None
