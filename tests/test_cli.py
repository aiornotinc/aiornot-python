import json
from typing import Optional

from click.testing import CliRunner
from pydantic import BaseModel

from aiornot.cli import cli


class FakeResp(BaseModel):
    id: str
    external_id: Optional[str] = None


class FakeTokenResp(BaseModel):
    is_valid: bool


class FakeClient:
    image_calls: list[dict[str, object]] = []
    text_calls: list[dict[str, object]] = []

    def __init__(self, api_key):
        self.api_key = api_key

    def image_report_by_file_sync(
        self, path, external_id=None, only=None, excluding=None
    ):
        self.image_calls.append(
            {
                "path": str(path),
                "external_id": external_id,
                "only": only,
                "excluding": excluding,
            }
        )
        return FakeResp(id=f"img-{len(self.image_calls)}", external_id=external_id)

    def text_report_sync(self, text, external_id=None, include_annotations=False):
        self.text_calls.append(
            {
                "text": text,
                "external_id": external_id,
                "include_annotations": include_annotations,
            }
        )
        return FakeResp(id=f"txt-{len(self.text_calls)}", external_id=external_id)

    def check_token(self):
        return FakeTokenResp(is_valid=True)


def test_cli_help_lists_supported_commands():
    result = CliRunner().invoke(cli, ["--help"])

    assert result.exit_code == 0
    for command in ["image", "text", "video", "voice", "music", "token"]:
        assert command in result.output
    assert "Analyze image, text, video, voice, and music files" in result.output


def test_media_help_lists_batch_subcommands():
    for modality in ["image", "text", "video", "voice", "music"]:
        result = CliRunner().invoke(cli, [modality, "--help"])

        assert result.exit_code == 0
        assert "single" in result.output
        assert "batch-csv" in result.output
        assert "batch-scan" in result.output


def test_text_single_help_mentions_stdin_and_annotations():
    result = CliRunner().invoke(cli, ["text", "single", "--help"])

    assert result.exit_code == 0
    assert "SOURCE is a text file path, or '-' to read from stdin." in result.output
    assert "--include-annotations" in result.output


def test_video_batch_csv_help_lists_filter_options():
    result = CliRunner().invoke(cli, ["video", "batch-csv", "--help"])

    assert result.exit_code == 0
    assert "--external-id" in result.output
    assert "--only" in result.output
    assert "--excluding" in result.output


def test_video_from_url_uses_default_duration_and_retains_download(monkeypatch):
    calls = []

    def fake_analyze_video_url(
        url,
        output_dir,
        max_duration,
        delete_after,
        external_id=None,
        only=None,
        excluding=None,
    ):
        calls.append(
            {
                "url": url,
                "output_dir": str(output_dir),
                "max_duration": max_duration,
                "delete_after": delete_after,
                "external_id": external_id,
                "only": only,
                "excluding": excluding,
            }
        )
        return {
            "download": {
                "url": url,
                "path": "aiornot-downloads/Sample [abc123].mp4",
                "deleted": False,
                "max_duration": max_duration,
            },
            "response": {"id": "vid-1", "external_id": external_id},
        }

    monkeypatch.setattr(
        "aiornot.cli.operations.analyze_video_url", fake_analyze_video_url
    )

    result = CliRunner().invoke(
        cli,
        [
            "video",
            "from-url",
            "https://example.com/watch?v=abc123",
            "--external-id",
            "ext-1",
            "--only",
            "ai_video",
            "--excluding",
            "deepfake_video",
        ],
        env={"AIORNOT_API_KEY": "test-token"},
    )

    assert result.exit_code == 0
    assert calls == [
        {
            "url": "https://example.com/watch?v=abc123",
            "output_dir": "aiornot-downloads",
            "max_duration": 120,
            "delete_after": False,
            "external_id": "ext-1",
            "only": ["ai_video"],
            "excluding": ["deepfake_video"],
        }
    ]
    assert json.loads(result.output)["download"]["deleted"] is False


def test_video_from_url_allows_delete_after_and_custom_duration(monkeypatch):
    calls = []

    def fake_analyze_video_url(
        url,
        output_dir,
        max_duration,
        delete_after,
        external_id=None,
        only=None,
        excluding=None,
    ):
        calls.append({"max_duration": max_duration, "delete_after": delete_after})
        return {
            "download": {
                "url": url,
                "path": "aiornot-downloads/Sample [abc123].mp4",
                "deleted": True,
                "max_duration": max_duration,
            },
            "response": {"id": "vid-1"},
        }

    monkeypatch.setattr(
        "aiornot.cli.operations.analyze_video_url", fake_analyze_video_url
    )

    result = CliRunner().invoke(
        cli,
        [
            "video",
            "from-url",
            "https://example.com/watch?v=abc123",
            "--max-duration",
            "300",
            "--delete-after",
        ],
        env={"AIORNOT_API_KEY": "test-token"},
    )

    assert result.exit_code == 0
    assert calls == [{"max_duration": 300, "delete_after": True}]
    assert json.loads(result.output)["download"]["max_duration"] == 300


def test_voice_from_url_uses_audio_default_duration_and_retains_download(monkeypatch):
    calls = []

    def fake_analyze_voice_url(url, output_dir, max_duration, delete_after):
        calls.append(
            {
                "url": url,
                "output_dir": str(output_dir),
                "max_duration": max_duration,
                "delete_after": delete_after,
            }
        )
        return {
            "download": {
                "url": url,
                "path": "aiornot-downloads/Sample [abc123].webm",
                "deleted": False,
                "max_duration": max_duration,
            },
            "response": {"id": "voice-1"},
        }

    monkeypatch.setattr(
        "aiornot.cli.operations.analyze_voice_url", fake_analyze_voice_url
    )

    result = CliRunner().invoke(
        cli,
        ["voice", "from-url", "https://example.com/watch?v=abc123"],
        env={"AIORNOT_API_KEY": "test-token"},
    )

    assert result.exit_code == 0
    assert calls == [
        {
            "url": "https://example.com/watch?v=abc123",
            "output_dir": "aiornot-downloads",
            "max_duration": 3600,
            "delete_after": False,
        }
    ]
    assert json.loads(result.output)["download"]["max_duration"] == 3600


def test_music_from_url_allows_delete_after_and_custom_duration(monkeypatch):
    calls = []

    def fake_analyze_music_url(url, output_dir, max_duration, delete_after):
        calls.append({"max_duration": max_duration, "delete_after": delete_after})
        return {
            "download": {
                "url": url,
                "path": "aiornot-downloads/Sample [abc123].m4a",
                "deleted": True,
                "max_duration": max_duration,
            },
            "response": {"id": "music-1"},
        }

    monkeypatch.setattr(
        "aiornot.cli.operations.analyze_music_url", fake_analyze_music_url
    )

    result = CliRunner().invoke(
        cli,
        [
            "music",
            "from-url",
            "https://example.com/watch?v=abc123",
            "--max-duration",
            "7200",
            "--delete-after",
        ],
        env={"AIORNOT_API_KEY": "test-token"},
    )

    assert result.exit_code == 0
    assert calls == [{"max_duration": 7200, "delete_after": True}]
    assert json.loads(result.output)["download"]["deleted"] is True


def test_token_help_only_lists_current_commands():
    result = CliRunner().invoke(cli, ["token", "--help"])

    assert result.exit_code == 0
    assert "check" in result.output
    assert "config" in result.output
    assert "refresh" not in result.output
    assert "revoke" not in result.output


def test_image_batch_csv_writes_correlatable_jsonl_and_resumes(tmp_path, monkeypatch):
    image_1 = tmp_path / "one.jpg"
    image_2 = tmp_path / "two.jpg"
    image_1.write_bytes(b"image-one")
    image_2.write_bytes(b"image-two")
    csv_path = tmp_path / "images.csv"
    csv_path.write_text(
        "id,path,external_id,only\n"
        f"first,{image_1.name},ext-1,ai_generated;nsfw\n"
        f"second,{image_2.name},ext-2,deepfake\n"
    )
    output = tmp_path / "out.jsonl"
    output.write_text(
        json.dumps(
            {
                "input": {"id": "first", "source": image_1.name},
                "ok": True,
                "response": {"id": "already-done"},
            }
        )
        + "\n"
    )
    FakeClient.image_calls = []
    monkeypatch.setattr("aiornot.cli.Client", FakeClient)

    result = CliRunner().invoke(
        cli,
        [
            "image",
            "batch-csv",
            str(csv_path),
            "--output",
            str(output),
        ],
        env={"AIORNOT_API_KEY": "test-token"},
    )

    assert result.exit_code == 0
    assert len(FakeClient.image_calls) == 1
    assert FakeClient.image_calls[0]["path"] == str(image_2)
    assert FakeClient.image_calls[0]["external_id"] == "ext-2"
    assert FakeClient.image_calls[0]["only"] == ["deepfake"]

    lines = [json.loads(line) for line in output.read_text().splitlines()]
    assert lines[1]["input"]["id"] == "second"
    assert lines[1]["input"]["row_number"] == 3
    assert lines[1]["ok"] is True
    assert lines[1]["response"]["id"] == "img-1"
    assert "[ok] second" in result.output
    assert (
        f"Wrote 1 records to {output} (1 succeeded, 0 failed, 1 skipped by resume)"
        in result.output
    )


def test_text_batch_scan_writes_jsonl(tmp_path, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("hello world")
    output = tmp_path / "text.jsonl"
    FakeClient.text_calls = []
    monkeypatch.setattr("aiornot.cli.Client", FakeClient)

    result = CliRunner().invoke(
        cli,
        [
            "text",
            "batch-scan",
            str(tmp_path),
            "--output",
            str(output),
            "--include-annotations",
        ],
        env={"AIORNOT_API_KEY": "test-token"},
    )

    assert result.exit_code == 0
    assert FakeClient.text_calls == [
        {
            "text": "hello world",
            "external_id": None,
            "include_annotations": True,
        }
    ]
    record = json.loads(output.read_text())
    assert record["input"]["id"] == "sample.txt"
    assert record["input"]["relative_path"] == "sample.txt"
    assert record["ok"] is True


def test_batch_scan_help_lists_relpath_md5_external_id_option():
    result = CliRunner().invoke(cli, ["image", "batch-scan", "--help"])

    assert result.exit_code == 0
    assert "--use-relpath-md5-as-external-id" in result.output
    assert "--external-id-prefix" not in result.output


def test_token_config_hides_entered_api_key(tmp_path, monkeypatch):
    saved = []
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("aiornot.cli.Client", FakeClient)
    monkeypatch.setattr("aiornot.cli.operations.save_api_key", saved.append)

    result = CliRunner().invoke(
        cli,
        ["token", "config"],
        input="secret-token\n",
    )

    assert result.exit_code == 0
    assert saved == ["secret-token"]
    assert "secret-token" not in result.output
