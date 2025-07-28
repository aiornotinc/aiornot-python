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

    # Classify an image by file
    resp = client.image_report_by_file_sync("example_image.jpg")
    pprint(resp.model_dump())
    
    # Check if it's AI generated
    if resp.is_ai():
        print("This image is AI generated")
    else:
        print("This image is human created")


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

    # Classify an image by file
    resp = await async_client.image_report_by_file_sync("example_image.jpg")
    pprint(resp.model_dump())
    
    # Check if it's AI generated
    if resp.is_ai():
        print("This image is AI generated")
    else:
        print("This image is human created")


if __name__ == "__main__":
    sync_example()
    asyncio.run(async_example())