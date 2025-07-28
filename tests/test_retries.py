import asyncio

import httpx

from aiornot import AsyncClient, Client


class FakeSyncHttp:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def get(self, **kwargs):
        self.calls += 1
        return self.responses.pop(0)


class FakeAsyncHttp:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    async def get(self, **kwargs):
        self.calls += 1
        return self.responses.pop(0)


def test_sync_client_retries_retryable_status_codes():
    fake_http = FakeSyncHttp([httpx.Response(503), httpx.Response(200, json={})])
    client = Client("token", client=fake_http, max_retries=1, retry_backoff=0)

    assert client.check_token().is_valid
    assert fake_http.calls == 2


def test_sync_client_does_not_retry_non_retryable_status_codes():
    fake_http = FakeSyncHttp([httpx.Response(401), httpx.Response(200, json={})])
    client = Client("token", client=fake_http, max_retries=1, retry_backoff=0)

    assert not client.check_token().is_valid
    assert fake_http.calls == 1


def test_async_client_retries_retryable_status_codes():
    async def run():
        fake_http = FakeAsyncHttp([httpx.Response(429), httpx.Response(200, json={})])
        client = AsyncClient("token", client=fake_http, max_retries=1, retry_backoff=0)

        assert (await client.check_token()).is_valid
        assert fake_http.calls == 2

    asyncio.run(run())
