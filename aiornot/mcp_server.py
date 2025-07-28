from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from aiornot import operations
from aiornot.sync_client import Client


def create_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The AIORNOT MCP server requires the optional MCP dependencies. "
            "Install with `pip install 'aiornot[mcp]'` or run with "
            "`uvx --from 'aiornot[mcp]' aiornot-mcp`."
        ) from exc

    mcp = FastMCP("AIORNOT")
    _register_tools(mcp)
    return mcp


def _register_tools(mcp) -> None:
    @mcp.tool()
    def aiornot_check_token() -> dict:
        """Check whether the configured AIORNOT API token is valid."""
        return operations.check_token()

    @mcp.tool()
    def aiornot_analyze_image_file(
        path: str,
        external_id: Optional[str] = None,
        only: Optional[List[str]] = None,
        excluding: Optional[List[str]] = None,
    ) -> dict:
        """Analyze a local image file with AIORNOT."""
        return operations.analyze_image_file(
            path,
            external_id=external_id,
            only=only,
            excluding=excluding,
        )

    @mcp.tool()
    def aiornot_analyze_text(
        text: str,
        external_id: Optional[str] = None,
        include_annotations: bool = False,
    ) -> dict:
        """Analyze text content with AIORNOT."""
        return operations.analyze_text_value(
            text,
            external_id=external_id,
            include_annotations=include_annotations,
        )

    @mcp.tool()
    def aiornot_analyze_text_file(
        path: str,
        external_id: Optional[str] = None,
        include_annotations: bool = False,
    ) -> dict:
        """Analyze a local text file with AIORNOT."""
        return operations.analyze_text_file(
            path,
            external_id=external_id,
            include_annotations=include_annotations,
        )

    @mcp.tool()
    def aiornot_analyze_video_file(
        path: str,
        external_id: Optional[str] = None,
        only: Optional[List[str]] = None,
        excluding: Optional[List[str]] = None,
    ) -> dict:
        """Analyze a local video file with AIORNOT."""
        return operations.analyze_video_file(
            path,
            external_id=external_id,
            only=only,
            excluding=excluding,
        )

    @mcp.tool()
    def aiornot_analyze_voice_file(path: str) -> dict:
        """Analyze a local voice audio file with AIORNOT."""
        return operations.analyze_voice_file(path)

    @mcp.tool()
    def aiornot_analyze_music_file(path: str) -> dict:
        """Analyze a local music audio file with AIORNOT."""
        return operations.analyze_music_file(path)

    @mcp.tool()
    def aiornot_batch_csv(
        modality: str,
        csv_path: str,
        output: str,
        path_column: str = "path",
        text_column: str = "text",
        id_column: str = "id",
        external_id: Optional[str] = None,
        only: Optional[List[str]] = None,
        excluding: Optional[List[str]] = None,
        include_annotations: bool = False,
        resume: bool = True,
    ) -> dict:
        """Analyze paths or text from a CSV file and write JSONL output."""
        client = Client(operations.load_api_key())
        jobs = operations.csv_jobs(
            modality,
            Path(csv_path),
            path_column,
            id_column,
            text_column=text_column,
            external_id=external_id,
            only=only,
            excluding=excluding,
            include_annotations=include_annotations,
        )
        summary = operations.run_batch(
            jobs,
            Path(output),
            resume,
            lambda job: _analyze_batch_job(client, job),
        )
        return {
            "processed": summary.processed,
            "skipped": summary.skipped,
            "output": str(summary.output),
        }

    @mcp.tool()
    def aiornot_batch_scan(
        modality: str,
        folder: str,
        output: str,
        extensions: Optional[List[str]] = None,
        recursive: bool = True,
        external_id_prefix: Optional[str] = None,
        only: Optional[List[str]] = None,
        excluding: Optional[List[str]] = None,
        include_annotations: bool = False,
        resume: bool = True,
    ) -> dict:
        """Analyze files found under a local folder and write JSONL output."""
        client = Client(operations.load_api_key())
        defaults = _default_extensions(modality)
        jobs = operations.scan_jobs(
            modality,
            Path(folder),
            operations.extensions(extensions or [], defaults),
            recursive,
            external_id_prefix=external_id_prefix,
            only=only,
            excluding=excluding,
            include_annotations=include_annotations,
        )
        summary = operations.run_batch(
            jobs,
            Path(output),
            resume,
            lambda job: _analyze_batch_job(client, job),
        )
        return {
            "processed": summary.processed,
            "skipped": summary.skipped,
            "output": str(summary.output),
        }


def _analyze_batch_job(client: Client, job: operations.BatchJob):
    if job.modality == "image":
        return operations.analyze_image_job(client, job)
    if job.modality == "text":
        return operations.analyze_text_job(client, job)
    if job.modality == "video":
        return operations.analyze_video_job(client, job)
    if job.modality == "voice":
        return operations.analyze_voice_job(client, job)
    if job.modality == "music":
        return operations.analyze_music_job(client, job)
    raise ValueError(
        "modality must be one of image, text, video, voice, or music"
    )


def _default_extensions(modality: str) -> set:
    if modality == "image":
        return operations.IMAGE_EXTENSIONS
    if modality == "text":
        return operations.TEXT_EXTENSIONS
    if modality == "video":
        return operations.VIDEO_EXTENSIONS
    if modality in {"voice", "music"}:
        return operations.AUDIO_EXTENSIONS
    raise ValueError(
        "modality must be one of image, text, video, voice, or music"
    )


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
