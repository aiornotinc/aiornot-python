from typing import Optional, Set, cast
from aiornot.settings import API_KEY, API_KEY_ERR, BASE_URL

RETRY_STATUS_CODES = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


class BaseClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        retry_backoff: float = 0.25,
        retry_status_codes: Optional[Set[int]] = None,
    ):
        self._api_key = cast(str, api_key or API_KEY)
        if not self._api_key:
            raise RuntimeError(API_KEY_ERR)
        self._base_url = base_url or BASE_URL
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff
        self._retry_status_codes = retry_status_codes or set(RETRY_STATUS_CODES)

    def _should_retry_status(self, status_code: int, attempt: int) -> bool:
        return attempt < self._max_retries and status_code in self._retry_status_codes

    def _retry_delay(self, attempt: int) -> float:
        return self._retry_backoff * (2**attempt)
