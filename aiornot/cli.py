import json
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

import click
from pydantic import BaseModel

from aiornot import operations
from aiornot.sync_client import Client

IMAGE_EXTENSIONS = operations.IMAGE_EXTENSIONS
TEXT_EXTENSIONS = operations.TEXT_EXTENSIONS
VIDEO_EXTENSIONS = operations.VIDEO_EXTENSIONS
AUDIO_EXTENSIONS = operations.AUDIO_EXTENSIONS
BatchJob = operations.BatchJob


@click.group()
def cli():
    """
    CLI for https://aiornot.com

    Analyze image, text, video, voice, and music files with AIORNOT.
    """
    pass


@cli.group()
def token():
    """
    Manage API token.
    """
    pass


@cli.group()
def image():
    """
    Analyze image files.
    """
    pass


@image.command("single")
@click.argument("source")
@click.option("--external-id", help="External ID for tracking")
@click.option("--only", multiple=True, help="Only include specific analysis types")
@click.option("--excluding", multiple=True, help="Exclude specific analysis types")
def image_single(source, external_id, only, excluding):
    """
    Check if an image is AI generated or not.
    """
    client = Client(_load_api_key())
    _print_record_as_json(
        operations.analyze_image_file(
            source,
            external_id=external_id,
            only=_option_list(only),
            excluding=_option_list(excluding),
            client=client,
        )
    )


@image.command("batch-csv")
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--path-column", default="path", show_default=True)
@click.option("--id-column", default="id", show_default=True)
@click.option("--external-id", help="External ID applied to rows without a column value")
@click.option("--only", multiple=True, help="Only include specific analysis types")
@click.option("--excluding", multiple=True, help="Exclude specific analysis types")
@click.option("--resume/--no-resume", default=True, show_default=True)
def image_batch_csv(
    csv_path, output, path_column, id_column, external_id, only, excluding, resume
):
    """
    Analyze image paths from a CSV file and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _csv_jobs(
        "image",
        csv_path,
        path_column,
        id_column,
        external_id=external_id,
        only=_option_list(only),
        excluding=_option_list(excluding),
    )
    _run_batch(jobs, output, resume, lambda job: _analyze_image(client, job))


@image.command("batch-scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--extension", "extensions", multiple=True, help="File extension to include")
@click.option("--recursive/--no-recursive", default=True, show_default=True)
@click.option("--external-id-prefix", help="Prefix for generated external IDs")
@click.option("--only", multiple=True, help="Only include specific analysis types")
@click.option("--excluding", multiple=True, help="Exclude specific analysis types")
@click.option("--resume/--no-resume", default=True, show_default=True)
def image_batch_scan(
    folder,
    output,
    extensions,
    recursive,
    external_id_prefix,
    only,
    excluding,
    resume,
):
    """
    Analyze image files found under a folder and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _scan_jobs(
        "image",
        folder,
        _extensions(extensions, IMAGE_EXTENSIONS),
        recursive,
        external_id_prefix=external_id_prefix,
        only=_option_list(only),
        excluding=_option_list(excluding),
    )
    _run_batch(jobs, output, resume, lambda job: _analyze_image(client, job))


@cli.group()
def text():
    """
    Analyze text files or stdin.
    """
    pass


@text.command("single")
@click.argument("source")
@click.option("--external-id", help="External ID for tracking")
@click.option(
    "--include-annotations",
    is_flag=True,
    help="Include text annotation spans when the API returns them",
)
def text_single(source, external_id, include_annotations):
    """
    Check if text is AI generated.

    SOURCE is a text file path, or '-' to read from stdin.
    """
    client = Client(_load_api_key())
    text_value = sys.stdin.read() if source == "-" else _require_file(source).read_text()
    _print_record_as_json(
        operations.analyze_text_value(
            text_value,
            external_id=external_id,
            include_annotations=include_annotations,
            client=client,
        )
    )


@text.command("batch-csv")
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--path-column", default="path", show_default=True)
@click.option("--text-column", default="text", show_default=True)
@click.option("--id-column", default="id", show_default=True)
@click.option("--external-id", help="External ID applied to rows without a column value")
@click.option(
    "--include-annotations",
    is_flag=True,
    help="Include text annotation spans when the API returns them",
)
@click.option("--resume/--no-resume", default=True, show_default=True)
def text_batch_csv(
    csv_path,
    output,
    path_column,
    text_column,
    id_column,
    external_id,
    include_annotations,
    resume,
):
    """
    Analyze text from CSV rows and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _csv_jobs(
        "text",
        csv_path,
        path_column,
        id_column,
        text_column=text_column,
        external_id=external_id,
        include_annotations=include_annotations,
    )
    _run_batch(jobs, output, resume, lambda job: _analyze_text(client, job))


@text.command("batch-scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--extension", "extensions", multiple=True, help="File extension to include")
@click.option("--recursive/--no-recursive", default=True, show_default=True)
@click.option("--external-id-prefix", help="Prefix for generated external IDs")
@click.option(
    "--include-annotations",
    is_flag=True,
    help="Include text annotation spans when the API returns them",
)
@click.option("--resume/--no-resume", default=True, show_default=True)
def text_batch_scan(
    folder, output, extensions, recursive, external_id_prefix, include_annotations, resume
):
    """
    Analyze text files found under a folder and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _scan_jobs(
        "text",
        folder,
        _extensions(extensions, TEXT_EXTENSIONS),
        recursive,
        external_id_prefix=external_id_prefix,
        include_annotations=include_annotations,
    )
    _run_batch(jobs, output, resume, lambda job: _analyze_text(client, job))


@cli.group()
def video():
    """
    Analyze video files.
    """
    pass


@video.command("single")
@click.argument("source")
@click.option("--external-id", help="External ID for tracking")
@click.option("--only", multiple=True, help="Only include specific analysis types")
@click.option("--excluding", multiple=True, help="Exclude specific analysis types")
def video_single(source, external_id, only, excluding):
    """
    Check if a video is AI generated.
    """
    client = Client(_load_api_key())
    _print_record_as_json(
        operations.analyze_video_file(
            source,
            external_id=external_id,
            only=_option_list(only),
            excluding=_option_list(excluding),
            client=client,
        )
    )


@video.command("batch-csv")
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--path-column", default="path", show_default=True)
@click.option("--id-column", default="id", show_default=True)
@click.option("--external-id", help="External ID applied to rows without a column value")
@click.option("--only", multiple=True, help="Only include specific analysis types")
@click.option("--excluding", multiple=True, help="Exclude specific analysis types")
@click.option("--resume/--no-resume", default=True, show_default=True)
def video_batch_csv(
    csv_path, output, path_column, id_column, external_id, only, excluding, resume
):
    """
    Analyze video paths from a CSV file and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _csv_jobs(
        "video",
        csv_path,
        path_column,
        id_column,
        external_id=external_id,
        only=_option_list(only),
        excluding=_option_list(excluding),
    )
    _run_batch(jobs, output, resume, lambda job: _analyze_video(client, job))


@video.command("batch-scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--extension", "extensions", multiple=True, help="File extension to include")
@click.option("--recursive/--no-recursive", default=True, show_default=True)
@click.option("--external-id-prefix", help="Prefix for generated external IDs")
@click.option("--only", multiple=True, help="Only include specific analysis types")
@click.option("--excluding", multiple=True, help="Exclude specific analysis types")
@click.option("--resume/--no-resume", default=True, show_default=True)
def video_batch_scan(
    folder,
    output,
    extensions,
    recursive,
    external_id_prefix,
    only,
    excluding,
    resume,
):
    """
    Analyze video files found under a folder and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _scan_jobs(
        "video",
        folder,
        _extensions(extensions, VIDEO_EXTENSIONS),
        recursive,
        external_id_prefix=external_id_prefix,
        only=_option_list(only),
        excluding=_option_list(excluding),
    )
    _run_batch(jobs, output, resume, lambda job: _analyze_video(client, job))


@cli.group()
def voice():
    """
    Analyze voice audio files.
    """
    pass


@voice.command("single")
@click.argument("source")
def voice_single(source):
    """
    Check if voice audio is AI generated.
    """
    client = Client(_load_api_key())
    _print_record_as_json(operations.analyze_voice_file(source, client=client))


@voice.command("batch-csv")
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--path-column", default="path", show_default=True)
@click.option("--id-column", default="id", show_default=True)
@click.option("--resume/--no-resume", default=True, show_default=True)
def voice_batch_csv(csv_path, output, path_column, id_column, resume):
    """
    Analyze voice audio paths from a CSV file and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _csv_jobs("voice", csv_path, path_column, id_column)
    _run_batch(jobs, output, resume, lambda job: _analyze_voice(client, job))


@voice.command("batch-scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--extension", "extensions", multiple=True, help="File extension to include")
@click.option("--recursive/--no-recursive", default=True, show_default=True)
@click.option("--resume/--no-resume", default=True, show_default=True)
def voice_batch_scan(folder, output, extensions, recursive, resume):
    """
    Analyze voice audio files found under a folder and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _scan_jobs("voice", folder, _extensions(extensions, AUDIO_EXTENSIONS), recursive)
    _run_batch(jobs, output, resume, lambda job: _analyze_voice(client, job))


@cli.group()
def music():
    """
    Analyze music audio files.
    """
    pass


@music.command("single")
@click.argument("source")
def music_single(source):
    """
    Check if music audio is AI generated.
    """
    client = Client(_load_api_key())
    _print_record_as_json(operations.analyze_music_file(source, client=client))


@music.command("batch-csv")
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--path-column", default="path", show_default=True)
@click.option("--id-column", default="id", show_default=True)
@click.option("--resume/--no-resume", default=True, show_default=True)
def music_batch_csv(csv_path, output, path_column, id_column, resume):
    """
    Analyze music audio paths from a CSV file and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _csv_jobs("music", csv_path, path_column, id_column)
    _run_batch(jobs, output, resume, lambda job: _analyze_music(client, job))


@music.command("batch-scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--extension", "extensions", multiple=True, help="File extension to include")
@click.option("--recursive/--no-recursive", default=True, show_default=True)
@click.option("--resume/--no-resume", default=True, show_default=True)
def music_batch_scan(folder, output, extensions, recursive, resume):
    """
    Analyze music audio files found under a folder and write JSONL output.
    """
    client = Client(_load_api_key())
    jobs = _scan_jobs("music", folder, _extensions(extensions, AUDIO_EXTENSIONS), recursive)
    _run_batch(jobs, output, resume, lambda job: _analyze_music(client, job))


@token.command()
def check():
    """
    Check if your API token is valid.
    """
    _print_record_as_json(operations.check_token(Client(api_key=_load_api_key())))


@token.command()
def config():
    """
    Save your API token.
    """
    click.echo("Go to https://aiornot.com/dashboard/api to get an API key.")

    while True:
        api_key = click.prompt("API key")
        client = Client(api_key=api_key)
        if client.check_token().is_valid:
            break
        click.echo("Invalid API key. Please try again.")

    _save_api_key(api_key)


def _csv_jobs(
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
    return operations.csv_jobs(
        modality,
        csv_path,
        path_column,
        id_column,
        text_column=text_column,
        external_id=external_id,
        only=only,
        excluding=excluding,
        include_annotations=include_annotations,
    )


def _scan_jobs(
    modality: str,
    folder: Path,
    extensions: List[str],
    recursive: bool,
    external_id_prefix: Optional[str] = None,
    only: Optional[List[str]] = None,
    excluding: Optional[List[str]] = None,
    include_annotations: bool = False,
) -> Iterable[BatchJob]:
    return operations.scan_jobs(
        modality,
        folder,
        extensions,
        recursive,
        external_id_prefix=external_id_prefix,
        only=only,
        excluding=excluding,
        include_annotations=include_annotations,
    )


def _run_batch(
    jobs: Iterable[BatchJob],
    output: Path,
    resume: bool,
    analyze: Callable[[BatchJob], BaseModel],
) -> None:
    summary = operations.run_batch(jobs, output, resume, analyze)
    click.echo(
        f"Wrote {summary.processed} records to {summary.output}"
        + (f" ({summary.skipped} skipped by resume)" if summary.skipped else "")
    )


def _run_job(job: BatchJob, analyze: Callable[[BatchJob], BaseModel]) -> Dict[str, object]:
    return operations.run_job(job, analyze)


def _analyze_image(client: Client, job: BatchJob) -> BaseModel:
    return operations.analyze_image_job(client, job)


def _analyze_text(client: Client, job: BatchJob) -> BaseModel:
    return operations.analyze_text_job(client, job)


def _analyze_video(client: Client, job: BatchJob) -> BaseModel:
    return operations.analyze_video_job(client, job)


def _analyze_voice(client: Client, job: BatchJob) -> BaseModel:
    return operations.analyze_voice_job(client, job)


def _analyze_music(client: Client, job: BatchJob) -> BaseModel:
    return operations.analyze_music_job(client, job)


def _existing_path(job: BatchJob) -> Path:
    return operations.existing_path(job)


def _completed_input_ids(output: Path) -> set:
    return operations.completed_input_ids(output)


def _error_record(exc: Exception) -> Dict[str, object]:
    return operations.error_record(exc)


def _split_values(value: Optional[str]) -> Optional[List[str]]:
    return operations.split_values(value)


def _parse_bool(value: Optional[str], default: bool = False) -> bool:
    return operations.parse_bool(value, default)


def _extensions(values: Iterable[str], defaults: set) -> List[str]:
    return operations.extensions(values, defaults)


def _option_list(values: Iterable[str]) -> Optional[List[str]]:
    return operations.option_list(values)


def _load_api_key() -> Optional[str]:
    try:
        return operations.load_api_key()
    except operations.MissingApiKeyError:
        click.echo("No API token found.")
        click.echo(
            "Set `AIORNOT_API_KEY` environment variable or run `aiornot token config`"
        )
        sys.exit(1)


def _save_api_key(api_key: str) -> None:
    config_path = Path.home() / ".aiornot" / "config.json"

    do_save = True

    if config_path.exists():
        do_save = click.confirm("Overwrite existing API token?")
        if not do_save:
            click.echo("Not overwriting existing API token.")
            return
    if do_save:
        operations.save_api_key(api_key)
        click.echo("API Key saved to ~/.aiornot/config.json")


def _require_file(source: str) -> Path:
    try:
        return operations.require_file(source)
    except FileNotFoundError:
        click.echo(f"File {source} does not exist.")
        sys.exit(1)
    except ValueError:
        click.echo(f"{source} is not a file.")
        sys.exit(1)


def _print_record_as_json(record: Dict[str, object]) -> None:
    click.echo(json.dumps(record, indent=4))


if __name__ == "__main__":
    cli()
