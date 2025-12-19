"""CLI for AIORNOT API."""

import json
import os
import sys
from pathlib import Path

import click
from pydantic import BaseModel

from aiornot.exceptions import AIORNotError
from aiornot.sync_client import Client
from aiornot.types import (
    MusicReportResponse,
    TextReportResponse,
    V2ImageReportResponse,
    VideoReportResponse,
    VoiceReportResponse,
)
from aiornot.types.enums import ImageAnalysisType, VideoAnalysisType


# Color codes
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    """Apply color to text if colors are enabled."""
    if use_color:
        return f"{color}{text}{Colors.RESET}"
    return text


def _verdict_color(verdict: str) -> str:
    """Get color for a verdict."""
    if verdict == "ai":
        return Colors.RED
    elif verdict == "human":
        return Colors.GREEN
    else:
        return Colors.YELLOW


def _format_confidence(confidence: float) -> str:
    """Format confidence as percentage."""
    return f"{confidence * 100:.1f}%"


def _output_json(model: BaseModel) -> None:
    """Output model as pretty JSON."""
    click.echo(model.model_dump_json(indent=2))


def _output_minimal(verdict: str, confidence: float | None) -> None:
    """Output minimal verdict + confidence."""
    if confidence is not None:
        click.echo(f"{verdict} {confidence:.4f}")
    else:
        click.echo(verdict)


def _output_quiet(verdict: str) -> None:
    """Output just the verdict."""
    click.echo(verdict)


def _output_image_table(resp: V2ImageReportResponse, use_color: bool) -> None:
    """Output image analysis as table."""
    report = resp.report
    verdict = "unknown"
    confidence = 0.0

    if report.ai_generated:
        verdict = report.ai_generated.verdict
        confidence = report.ai_generated.ai.confidence

    verdict_display = _colorize(verdict.upper(), _verdict_color(verdict), use_color)
    conf_display = _format_confidence(confidence)

    click.echo(f"{'='*60}")
    click.echo(f"  Image Analysis: {resp.id}")
    click.echo(f"{'='*60}")
    click.echo(f"  Verdict:      {verdict_display}")
    click.echo(f"  Confidence:   {conf_display}")

    if report.ai_generated and report.ai_generated.generator:
        # Find top generator
        gen = report.ai_generated.generator
        generators = [
            ("Midjourney", gen.midjourney),
            ("DALL-E", gen.dall_e),
            ("Stable Diffusion", gen.stable_diffusion),
            ("This Person Does Not Exist", gen.this_person_does_not_exist),
            ("Adobe Firefly", gen.adobe_firefly),
            ("Flux", gen.flux),
            ("4o", gen.four_o),
        ]
        top_gen = max(generators, key=lambda x: x[1].confidence)
        if top_gen[1].is_detected:
            click.echo(
                f"  Generator:    {top_gen[0]} ({_format_confidence(top_gen[1].confidence)})"
            )

    click.echo(f"{'-'*60}")

    if report.deepfake:
        df_status = (
            _colorize("DETECTED", Colors.RED, use_color)
            if report.deepfake.is_detected
            else _colorize("Not detected", Colors.GREEN, use_color)
        )
        click.echo(f"  Deepfake:     {df_status}")

    if report.nsfw:
        nsfw_status = (
            _colorize("DETECTED", Colors.RED, use_color)
            if report.nsfw.is_detected
            else _colorize("Not detected", Colors.GREEN, use_color)
        )
        click.echo(f"  NSFW:         {nsfw_status}")

    if report.quality:
        quality_status = (
            _colorize("High", Colors.GREEN, use_color)
            if report.quality.is_detected
            else _colorize("Low", Colors.YELLOW, use_color)
        )
        click.echo(f"  Quality:      {quality_status}")

    click.echo(f"{'='*60}")


def _output_video_table(resp: VideoReportResponse, use_color: bool) -> None:
    """Output video analysis as table."""
    report = resp.report

    click.echo(f"{'='*60}")
    click.echo(f"  Video Analysis: {resp.id}")
    click.echo(f"{'='*60}")

    # AI Video
    video_verdict = "AI" if report.ai_video.is_detected else "Human"
    video_color = Colors.RED if report.ai_video.is_detected else Colors.GREEN
    click.echo(
        f"  Video:        {_colorize(video_verdict, video_color, use_color)} "
        f"({_format_confidence(report.ai_video.confidence)})"
    )

    # AI Voice
    if report.ai_voice:
        voice_verdict = "AI" if report.ai_voice.is_detected else "Human"
        voice_color = Colors.RED if report.ai_voice.is_detected else Colors.GREEN
        click.echo(
            f"  Voice:        {_colorize(voice_verdict, voice_color, use_color)} "
            f"({_format_confidence(report.ai_voice.confidence)})"
        )

    # AI Music
    if report.ai_music:
        music_verdict = "AI" if report.ai_music.is_detected else "Human"
        music_color = Colors.RED if report.ai_music.is_detected else Colors.GREEN
        click.echo(
            f"  Music:        {_colorize(music_verdict, music_color, use_color)} "
            f"({_format_confidence(report.ai_music.confidence)})"
        )

    # Deepfake
    if report.deepfake_video:
        df_verdict = "DETECTED" if report.deepfake_video.is_detected else "Not detected"
        df_color = Colors.RED if report.deepfake_video.is_detected else Colors.GREEN
        click.echo(
            f"  Deepfake:     {_colorize(df_verdict, df_color, use_color)} "
            f"({_format_confidence(report.deepfake_video.confidence)})"
        )

    click.echo(f"{'-'*60}")
    click.echo(f"  Duration:     {report.meta.duration}s")
    click.echo(f"{'='*60}")


def _output_audio_table(
    resp: VoiceReportResponse | MusicReportResponse, label: str, use_color: bool
) -> None:
    """Output voice/music analysis as table."""
    report = resp.report
    verdict_color = _verdict_color(report.verdict)

    click.echo(f"{'='*60}")
    click.echo(f"  {label} Analysis: {resp.id}")
    click.echo(f"{'='*60}")
    click.echo(
        f"  Verdict:      {_colorize(report.verdict.upper(), verdict_color, use_color)}"
    )
    click.echo(f"  Confidence:   {_format_confidence(report.confidence)}")
    click.echo(f"{'-'*60}")
    click.echo(f"  Duration:     {report.duration}s")
    click.echo(f"{'='*60}")


def _output_text_table(resp: TextReportResponse, use_color: bool) -> None:
    """Output text analysis as table."""
    report = resp.report.ai_text
    verdict = "ai" if report.is_detected else "human"
    verdict_color = _verdict_color(verdict)

    click.echo(f"{'='*60}")
    click.echo(f"  Text Analysis: {resp.id}")
    click.echo(f"{'='*60}")
    click.echo(
        f"  Verdict:      {_colorize(verdict.upper(), verdict_color, use_color)}"
    )
    click.echo(f"  Confidence:   {_format_confidence(report.confidence)}")
    click.echo(f"{'-'*60}")
    click.echo(f"  Words:        {resp.metadata.word_count}")
    click.echo(f"  Characters:   {resp.metadata.character_count}")

    if report.annotations:
        click.echo(f"{'-'*60}")
        click.echo("  Annotations:")
        for text_block, conf in report.annotations[:5]:  # Show first 5
            truncated = text_block[:50] + "..." if len(text_block) > 50 else text_block
            click.echo(f"    [{_format_confidence(conf)}] {truncated}")
        if len(report.annotations) > 5:
            click.echo(f"    ... and {len(report.annotations) - 5} more")

    click.echo(f"{'='*60}")


@click.group()
def cli():
    """
    CLI for https://aiornot.com

    Detect AI-generated content in images, videos, audio, and text.
    """
    pass


@cli.group()
def token():
    """Manage API token."""
    pass


# Format options decorator
def format_options(f):
    """Add common format options to a command."""
    f = click.option(
        "--format",
        "output_format",
        type=click.Choice(["json", "table", "minimal"]),
        default="json",
        help="Output format",
    )(f)
    f = click.option("--quiet", "-q", is_flag=True, help="Only output verdict")(f)
    f = click.option("--color/--no-color", default=None, help="Enable/disable colors")(
        f
    )
    return f


def _get_use_color(color_flag: bool | None) -> bool:
    """Determine if colors should be used."""
    if color_flag is not None:
        return color_flag
    return sys.stdout.isatty()


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--only",
    "only_types",
    multiple=True,
    type=click.Choice(["ai_generated", "deepfake", "nsfw", "quality", "reverse_search"]),
    help="Only run these analysis types",
)
@click.option(
    "--excluding",
    "excluding_types",
    multiple=True,
    type=click.Choice(["ai_generated", "deepfake", "nsfw", "quality", "reverse_search"]),
    help="Exclude these analysis types",
)
@click.option("--external-id", help="External tracking ID")
@format_options
def image(
    file: str,
    only_types: tuple[str, ...],
    excluding_types: tuple[str, ...],
    external_id: str | None,
    output_format: str,
    quiet: bool,
    color: bool | None,
):
    """Analyze an image file for AI-generated content."""
    client = Client(api_key=_load_api_key())
    use_color = _get_use_color(color)

    only = [ImageAnalysisType(t) for t in only_types] if only_types else None
    excluding = (
        [ImageAnalysisType(t) for t in excluding_types] if excluding_types else None
    )

    try:
        resp = client.image_report_from_file(
            file, only=only, excluding=excluding, external_id=external_id
        )

        if quiet:
            _output_quiet(resp.verdict or "unknown")
        elif output_format == "json":
            _output_json(resp)
        elif output_format == "minimal":
            _output_minimal(resp.verdict or "unknown", resp.confidence)
        else:
            _output_image_table(resp, use_color)

    except AIORNotError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--only",
    "only_types",
    multiple=True,
    type=click.Choice(["ai_video", "ai_music", "ai_voice", "deepfake_video"]),
    help="Only run these analysis types",
)
@click.option(
    "--excluding",
    "excluding_types",
    multiple=True,
    type=click.Choice(["ai_video", "ai_music", "ai_voice", "deepfake_video"]),
    help="Exclude these analysis types",
)
@click.option("--external-id", help="External tracking ID")
@format_options
def video(
    file: str,
    only_types: tuple[str, ...],
    excluding_types: tuple[str, ...],
    external_id: str | None,
    output_format: str,
    quiet: bool,
    color: bool | None,
):
    """Analyze a video file for AI-generated content."""
    client = Client(api_key=_load_api_key())
    use_color = _get_use_color(color)

    only = [VideoAnalysisType(t) for t in only_types] if only_types else None
    excluding = (
        [VideoAnalysisType(t) for t in excluding_types] if excluding_types else None
    )

    try:
        resp = client.video_report_from_file(
            file, only=only, excluding=excluding, external_id=external_id
        )

        if quiet:
            verdict = "ai" if resp.ai_video_detected else "human"
            _output_quiet(verdict)
        elif output_format == "json":
            _output_json(resp)
        elif output_format == "minimal":
            verdict = "ai" if resp.ai_video_detected else "human"
            _output_minimal(verdict, resp.ai_video_confidence)
        else:
            _output_video_table(resp, use_color)

    except AIORNotError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@format_options
def voice(file: str, output_format: str, quiet: bool, color: bool | None):
    """Analyze a voice/speech audio file for AI-generated content."""
    client = Client(api_key=_load_api_key())
    use_color = _get_use_color(color)

    try:
        resp = client.voice_report_from_file(file)

        if quiet:
            _output_quiet(resp.verdict)
        elif output_format == "json":
            _output_json(resp)
        elif output_format == "minimal":
            _output_minimal(resp.verdict, resp.confidence)
        else:
            _output_audio_table(resp, "Voice", use_color)

    except AIORNotError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@format_options
def music(file: str, output_format: str, quiet: bool, color: bool | None):
    """Analyze a music audio file for AI-generated content."""
    client = Client(api_key=_load_api_key())
    use_color = _get_use_color(color)

    try:
        resp = client.music_report_from_file(file)

        if quiet:
            _output_quiet(resp.verdict)
        elif output_format == "json":
            _output_json(resp)
        elif output_format == "minimal":
            _output_minimal(resp.verdict, resp.confidence)
        else:
            _output_audio_table(resp, "Music", use_color)

    except AIORNotError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("source")
@click.option("--file", "-f", is_flag=True, help="Read text from a file")
@click.option(
    "--annotations", "-a", is_flag=True, help="Include block-level annotations"
)
@click.option("--external-id", help="External tracking ID")
@format_options
def text(
    source: str,
    file: bool,
    annotations: bool,
    external_id: str | None,
    output_format: str,
    quiet: bool,
    color: bool | None,
):
    """Analyze text for AI-generated content.

    SOURCE can be the text itself or a file path (with --file flag).
    """
    client = Client(api_key=_load_api_key())
    use_color = _get_use_color(color)

    if file:
        path = Path(source)
        if not path.exists():
            click.echo(f"File not found: {source}", err=True)
            sys.exit(1)
        with open(path) as f:
            text_content = f.read()
    else:
        text_content = source

    try:
        resp = client.text_report(
            text_content, include_annotations=annotations, external_id=external_id
        )

        if quiet:
            verdict = "ai" if resp.is_detected else "human"
            _output_quiet(verdict)
        elif output_format == "json":
            _output_json(resp)
        elif output_format == "minimal":
            verdict = "ai" if resp.is_detected else "human"
            _output_minimal(verdict, resp.confidence)
        else:
            _output_text_table(resp, use_color)

    except AIORNotError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@token.command()
def check():
    """Check if your API token is valid by making a health check request."""
    api_key = _load_api_key()
    client = Client(api_key=api_key)

    try:
        if client.is_live():
            click.echo("API is live and your token is configured.")
        else:
            click.echo("API is not responding.", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@token.command()
def config():
    """Save your API token to ~/.aiornot/config.json"""
    click.echo("Go to https://aiornot.com/dashboard/api to get an API key.")

    api_key = click.prompt("API key")

    # Verify the key works
    client = Client(api_key=api_key)
    if not client.is_live():
        click.echo("Warning: Could not verify API key (API may be down).")
        if not click.confirm("Save anyway?"):
            return

    _save_api_key(api_key)


def _load_api_key() -> str:
    """Load API key from environment or config file."""
    # Check environment variables
    key = os.getenv("AIORNOT_API_KEY") or os.getenv("AIORNOT_API_TOKEN")
    if key:
        return key

    # Check config file
    config_path = Path.home() / ".aiornot" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            key = config.get("api_key") or config.get("api_token")
            if key:
                return key

    click.echo("No API token found.", err=True)
    click.echo(
        "Set AIORNOT_API_KEY environment variable or run `aiornot token config`",
        err=True,
    )
    sys.exit(1)


def _save_api_key(api_key: str) -> None:
    """Save API key to config file."""
    config_path = Path.home() / ".aiornot" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        if not click.confirm("Overwrite existing API token?"):
            click.echo("Not overwriting existing API token.")
            return

    with open(config_path, "w") as f:
        json.dump({"api_key": api_key}, f)
    click.echo(f"API key saved to {config_path}")


if __name__ == "__main__":
    cli()
