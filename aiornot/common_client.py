import httpx
from aiornot.resp_types import (
    CheckTokenResp,
    ImageResp,
    MusicResp,
    TextResp,
    VideoResp,
    VoiceResp,
)


def is_live(resp: httpx.Response) -> bool:
    resp.raise_for_status()
    return resp.json()["is_live"]


def image_report(resp: httpx.Response) -> ImageResp:
    resp.raise_for_status()
    return ImageResp(**resp.json())


def check_token(resp: httpx.Response) -> CheckTokenResp:
    if resp.status_code in {401, 403}:
        return CheckTokenResp(is_valid=False)
    if resp.status_code == 404:
        try:
            message = resp.json().get("message", "")
        except ValueError:
            message = ""
        if "billing account" in message:
            return CheckTokenResp(is_valid=True)
    if 200 <= resp.status_code < 300:
        return CheckTokenResp(is_valid=True)
    resp.raise_for_status()
    return CheckTokenResp(is_valid=True)


def text_report(resp: httpx.Response) -> TextResp:
    resp.raise_for_status()
    return TextResp(**resp.json())


def voice_report(resp: httpx.Response) -> VoiceResp:
    resp.raise_for_status()
    return VoiceResp(**resp.json())


def music_report(resp: httpx.Response) -> MusicResp:
    resp.raise_for_status()
    return MusicResp(**resp.json())


def video_report(resp: httpx.Response) -> VideoResp:
    resp.raise_for_status()
    return VideoResp(**resp.json())
