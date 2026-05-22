import hashlib
import subprocess
import stat
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from aiornot import operations


class FakeResp(BaseModel):
    id: str
    external_id: Optional[str] = None


class FakeClient:
    def __init__(self):
        self.image_calls = []
        self.text_calls = []
        self.video_calls = []
        self.voice_calls = []
        self.music_calls = []

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
        return FakeResp(id="img-1", external_id=external_id)

    def text_report_sync(self, text, external_id=None, include_annotations=False):
        self.text_calls.append(
            {
                "text": text,
                "external_id": external_id,
                "include_annotations": include_annotations,
            }
        )
        return FakeResp(id="txt-1", external_id=external_id)

    def video_report_by_file_sync(
        self, path, external_id=None, only=None, excluding=None
    ):
        self.video_calls.append(
            {
                "path": str(path),
                "external_id": external_id,
                "only": only,
                "excluding": excluding,
            }
        )
        return FakeResp(id="vid-1", external_id=external_id)

    def voice_report_by_file_sync(self, path):
        self.voice_calls.append({"path": str(path)})
        return FakeResp(id="voice-1")

    def music_report_by_file_sync(self, path):
        self.music_calls.append({"path": str(path)})
        return FakeResp(id="music-1")


def test_analyze_image_file_returns_json_safe_record(tmp_path):
    source = tmp_path / "sample.jpg"
    source.write_bytes(b"image")
    client = FakeClient()

    record = operations.analyze_image_file(
        source,
        external_id="ext-1",
        only=["ai_generated"],
        excluding=["nsfw"],
        client=client,
    )

    assert record == {"id": "img-1", "external_id": "ext-1"}
    assert client.image_calls == [
        {
            "path": str(source),
            "external_id": "ext-1",
            "only": ["ai_generated"],
            "excluding": ["nsfw"],
        }
    ]


def test_analyze_video_url_downloads_first_120_seconds_and_retains_file(
    tmp_path, monkeypatch
):
    downloaded = tmp_path / "downloads" / "Sample [abc123].mp4"
    calls = []

    def fake_run(cmd, check, capture_output, text):
        calls.append(
            {
                "cmd": cmd,
                "check": check,
                "capture_output": capture_output,
                "text": text,
            }
        )
        downloaded.parent.mkdir(exist_ok=True)
        downloaded.write_bytes(b"video")
        return subprocess.CompletedProcess(cmd, 0, stdout=f"{downloaded}\n")

    monkeypatch.setattr("aiornot.operations.subprocess.run", fake_run)
    client = FakeClient()

    record = operations.analyze_video_url(
        "https://example.com/watch?v=abc123",
        output_dir=tmp_path / "downloads",
        external_id="ext-1",
        only=["ai_video"],
        excluding=["deepfake_video"],
        client=client,
    )

    cmd = calls[0]["cmd"]
    assert cmd[:2] == ["uvx", "yt-dlp@latest"]
    assert cmd[cmd.index("-f") + 1] == "bv*+ba/b"
    assert "--no-playlist" in cmd
    assert cmd[cmd.index("--download-sections") + 1] == "*0:00-120"
    assert cmd[cmd.index("--print") + 1] == "after_move:filepath"
    assert cmd[-1] == "https://example.com/watch?v=abc123"
    assert client.video_calls == [
        {
            "path": str(downloaded),
            "external_id": "ext-1",
            "only": ["ai_video"],
            "excluding": ["deepfake_video"],
        }
    ]
    assert record == {
        "download": {
            "url": "https://example.com/watch?v=abc123",
            "path": str(downloaded),
            "deleted": False,
            "max_duration": 120,
        },
        "response": {"id": "vid-1", "external_id": "ext-1"},
    }
    assert downloaded.exists()


def test_analyze_video_url_can_delete_downloaded_file_after_analysis(
    tmp_path, monkeypatch
):
    downloaded = tmp_path / "downloads" / "Sample [abc123].mp4"

    def fake_run(cmd, check, capture_output, text):
        downloaded.parent.mkdir(exist_ok=True)
        downloaded.write_bytes(b"video")
        return subprocess.CompletedProcess(cmd, 0, stdout=f"{downloaded}\n")

    monkeypatch.setattr("aiornot.operations.subprocess.run", fake_run)

    record = operations.analyze_video_url(
        "https://example.com/watch?v=abc123",
        output_dir=tmp_path / "downloads",
        delete_after=True,
        client=FakeClient(),
    )

    assert record["download"]["deleted"] is True
    assert not downloaded.exists()


def test_analyze_voice_url_downloads_audio_only_first_hour_and_retains_file(
    tmp_path, monkeypatch
):
    downloaded = tmp_path / "downloads" / "Sample [abc123].webm"
    calls = []

    def fake_run(cmd, check, capture_output, text):
        calls.append(cmd)
        downloaded.parent.mkdir(exist_ok=True)
        downloaded.write_bytes(b"audio")
        return subprocess.CompletedProcess(cmd, 0, stdout=f"{downloaded}\n")

    monkeypatch.setattr("aiornot.operations.subprocess.run", fake_run)
    client = FakeClient()

    record = operations.analyze_voice_url(
        "https://example.com/watch?v=abc123",
        output_dir=tmp_path / "downloads",
        client=client,
    )

    cmd = calls[0]
    assert cmd[:2] == ["uvx", "yt-dlp@latest"]
    assert cmd[cmd.index("-f") + 1] == "ba"
    assert "--no-playlist" in cmd
    assert cmd[cmd.index("--download-sections") + 1] == "*0:00-3600"
    assert client.voice_calls == [{"path": str(downloaded)}]
    assert record == {
        "download": {
            "url": "https://example.com/watch?v=abc123",
            "path": str(downloaded),
            "deleted": False,
            "max_duration": 3600,
        },
        "response": {"id": "voice-1", "external_id": None},
    }


def test_analyze_music_url_can_delete_downloaded_audio_after_analysis(
    tmp_path, monkeypatch
):
    downloaded = tmp_path / "downloads" / "Sample [abc123].m4a"

    def fake_run(cmd, check, capture_output, text):
        downloaded.parent.mkdir(exist_ok=True)
        downloaded.write_bytes(b"audio")
        return subprocess.CompletedProcess(cmd, 0, stdout=f"{downloaded}\n")

    monkeypatch.setattr("aiornot.operations.subprocess.run", fake_run)
    client = FakeClient()

    record = operations.analyze_music_url(
        "https://example.com/watch?v=abc123",
        output_dir=tmp_path / "downloads",
        delete_after=True,
        client=client,
    )

    assert client.music_calls == [{"path": str(downloaded)}]
    assert record["download"]["deleted"] is True
    assert not downloaded.exists()


def test_text_csv_jobs_accept_literal_text(tmp_path):
    csv_path = tmp_path / "texts.csv"
    csv_path.write_text(
        "id,text,external_id,include_annotations\none,hello,ext-1,true\n"
    )

    jobs = list(
        operations.csv_jobs(
            "text",
            csv_path,
            path_column="path",
            id_column="id",
            include_annotations=False,
        )
    )

    assert len(jobs) == 1
    assert jobs[0].path is None
    assert jobs[0].text == "hello"
    assert jobs[0].external_id == "ext-1"
    assert jobs[0].include_annotations is True


def test_require_file_rejects_directories(tmp_path):
    try:
        operations.require_file(Path(tmp_path))
    except ValueError as exc:
        assert "is not a file" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_scan_jobs_can_use_relative_path_md5_as_external_id(tmp_path):
    source_dir = tmp_path / "images"
    nested_dir = source_dir / "nested"
    nested_dir.mkdir(parents=True)
    source = nested_dir / "sample.jpg"
    source.write_bytes(b"image")

    jobs = list(
        operations.scan_jobs(
            "image",
            source_dir,
            [".jpg"],
            recursive=True,
            use_relpath_md5_as_external_id=True,
        )
    )

    assert len(jobs) == 1
    assert jobs[0].relative_path == "nested/sample.jpg"
    assert jobs[0].external_id == hashlib.md5(b"nested/sample.jpg").hexdigest()
    assert len(jobs[0].external_id) == 32


def test_save_api_key_uses_owner_only_file_permissions(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    operations.save_api_key("secret-token")

    config_path = tmp_path / ".aiornot" / "config.json"
    assert config_path.read_text() == '{"api_token": "secret-token"}'
    assert stat.S_IMODE(config_path.stat().st_mode) == 0o600
