import asyncio
from aiornot import Client, AsyncClient
from pprint import pprint


def sync_example():
    # Create a client (reads AIORNOT_API_KEY env)
    client = Client()

    # Check if the API is up
    if not client.is_live():
        print("API is down")
        exit(1)

    # Check your token
    resp = client.check_token()
    if not resp.is_valid:
        print("Token is invalid")
        exit(1)

    # Classify an image by url
    resp = client.image_report_by_url("https://thispersondoesnotexist.com")
    pprint(resp)

    # Classify audio by url
    resp = client.audio_report_by_url("https://www.youtube.com/watch?v=v4WiI4es_UI")
    pprint(resp)


async def async_example():
    # Create a client (reads AIORNOT_API_KEY env)
    async_client = AsyncClient()

    # Check if the API is up
    if not await async_client.is_live():
        print("API is down")
        exit(1)

    # Check your token
    resp = await async_client.check_token()
    if not resp.is_valid:
        print("Token is invalid")
        exit(1)

    # Classify an image by url
    resp = await async_client.image_report_by_url("https://thispersondoesnotexist.com")
    pprint(resp)

    # Classify audio by url
    resp = await async_client.audio_report_by_url(
        "https://www.youtube.com/watch?v=v4WiI4es_UI"
    )
    pprint(resp)


if __name__ == "__main__":
    sync_example()
    asyncio.run(async_example())
