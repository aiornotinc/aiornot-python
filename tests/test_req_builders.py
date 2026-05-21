import httpx
import pytest

from aiornot.common_client import check_token
from aiornot.req_builders import (
    check_token_args,
    classify_image_blob_args,
    is_live_args,
    music_report_sync_args,
    text_report_sync_args,
    video_report_sync_args,
    voice_report_sync_args,
)
from aiornot.settings import BASE_URL


def test_default_base_url_is_gateway_root():
    assert BASE_URL == "https://api.aiornot.com"


def test_report_builders_use_v2_sibling_routes():
    base_url = "https://api.example.test"

    live = is_live_args(base_url)
    image = classify_image_blob_args(b"image", "token", base_url=base_url)
    voice = voice_report_sync_args(b"audio", "token", base_url=base_url)
    music = music_report_sync_args(b"audio", "token", base_url=base_url)
    text = text_report_sync_args(
        "hello world",
        "token",
        base_url=base_url,
        external_id="ext-1",
        include_annotations=True,
    )
    video = video_report_sync_args(b"video", "token", base_url=base_url)

    assert live["url"] == "https://api.example.test/v1/system/live"
    assert image["url"] == "https://api.example.test/v2/image/sync"
    assert voice["url"] == "https://api.example.test/v1/reports/voice"
    assert voice["files"] == {"file": b"audio"}
    assert music["url"] == "https://api.example.test/v1/reports/music"
    assert music["files"] == {"file": b"audio"}
    assert video["url"] == "https://api.example.test/v2/video/sync"
    assert text["url"] == "https://api.example.test/v2/text/sync"
    assert text["files"] == {"text": (None, "hello world")}
    assert text["params"] == {
        "external_id": "ext-1",
        "include_annotations": True,
    }
    assert "json" not in text


def test_report_builders_omit_default_external_id():
    image = classify_image_blob_args(b"image", "token")
    text = text_report_sync_args("hello world", "token")
    video = video_report_sync_args(b"video", "token")

    assert "params" not in image
    assert "params" not in text
    assert "params" not in video


def test_external_id_is_limited_to_uuid_length():
    max_length_external_id = "x" * 36
    too_long_external_id = "x" * 37

    assert (
        classify_image_blob_args(b"image", "token", external_id=max_length_external_id)[
            "params"
        ]["external_id"]
        == max_length_external_id
    )
    with pytest.raises(ValueError, match="external_id"):
        classify_image_blob_args(b"image", "token", external_id=too_long_external_id)
    with pytest.raises(ValueError, match="external_id"):
        text_report_sync_args("hello world", "token", external_id=too_long_external_id)
    with pytest.raises(ValueError, match="external_id"):
        video_report_sync_args(b"video", "token", external_id=too_long_external_id)


def test_check_token_uses_authenticated_gateway_probe():
    args = check_token_args("token", base_url="https://api.example.test")

    assert args["url"] == "https://api.example.test/v2/billing/balance"
    assert args["headers"] == {"Authorization": "Bearer token"}


def test_check_token_status_mapping():
    assert not check_token(httpx.Response(401)).is_valid
    assert not check_token(httpx.Response(403)).is_valid

    missing_account = httpx.Response(
        404,
        json={
            "error": "NOT_FOUND",
            "message": "billing account not found",
            "details": {},
        },
    )
    assert check_token(missing_account).is_valid

    assert check_token(httpx.Response(200, json={})).is_valid
