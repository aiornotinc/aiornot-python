import httpx
from aiornot.resp_types import (
    AudioResp,
    CheckTokenResp,
    ImageResp,
    RefreshTokenResp,
    RevokeTokenResp,
)


def is_live(resp: httpx.Response) -> bool:
    resp.raise_for_status()
    return resp.json()["is_live"]


def image_report(resp: httpx.Response) -> ImageResp:
    resp.raise_for_status()
    return ImageResp(**resp.json())


def audio_report(resp: httpx.Response) -> AudioResp:
    resp.raise_for_status()
    return AudioResp(**resp.json())


def check_token(resp: httpx.Response) -> CheckTokenResp:
    if resp.status_code == 401:
        return CheckTokenResp(is_valid=False)
    else:
        resp.raise_for_status()
    return CheckTokenResp(**resp.json())


def refresh_token(resp: httpx.Response) -> RefreshTokenResp:
    resp.raise_for_status()
    return RefreshTokenResp(**resp.json())


def revoke_token(resp: httpx.Response) -> RevokeTokenResp:
    resp.raise_for_status()
    return RevokeTokenResp(**resp.json())
