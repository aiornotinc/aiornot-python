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

    def image_report_by_file_sync(self, path, external_id=None, only=None, excluding=None):
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


def test_text_csv_jobs_accept_literal_text(tmp_path):
    csv_path = tmp_path / "texts.csv"
    csv_path.write_text("id,text,external_id,include_annotations\none,hello,ext-1,true\n")

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
