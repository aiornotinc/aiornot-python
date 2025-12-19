"""Example usage of the AIORNOT Python client."""

import asyncio
from pathlib import Path
from pprint import pprint

from aiornot import AsyncClient, Client, ImageAnalysisType


def sync_example():
    """Synchronous client usage examples."""
    # Create a client (reads AIORNOT_API_KEY env)
    client = Client()

    # Check if the API is up
    if not client.is_live():
        print("API is down")
        exit(1)

    # Analyze an image file
    # resp = client.image_report_from_file("path/to/image.jpg")
    # print(f"Verdict: {resp.verdict}")
    # print(f"Confidence: {resp.confidence}")
    # print(f"Is AI: {resp.is_ai()}")

    # Analyze with specific analysis types only
    # resp = client.image_report_from_file(
    #     "path/to/image.jpg",
    #     only=[ImageAnalysisType.AI_GENERATED, ImageAnalysisType.DEEPFAKE]
    # )

    # Analyze text
    # resp = client.text_report("This is some text to analyze for AI generation.")
    # print(f"Is AI: {resp.is_ai()}")
    # print(f"Confidence: {resp.confidence}")

    # Batch processing
    # images = ["image1.jpg", "image2.jpg", "image3.jpg"]
    # results = client.image_report_batch(images)
    # print(f"Processed {results.total} images")
    # print(f"Success rate: {results.success_rate:.1%}")

    print("Sync client initialized successfully")


async def async_example():
    """Asynchronous client usage examples."""
    # Create an async client (reads AIORNOT_API_KEY env)
    async_client = AsyncClient()

    # Check if the API is up
    if not await async_client.is_live():
        print("API is down")
        exit(1)

    # Analyze an image file
    # resp = await async_client.image_report_from_file("path/to/image.jpg")
    # print(f"Verdict: {resp.verdict}")
    # print(f"Is AI: {resp.is_ai()}")

    # Batch processing with progress callback
    # def on_progress(completed, total):
    #     print(f"Progress: {completed}/{total}")
    #
    # images = list(Path("images").glob("*.jpg"))
    # results = await async_client.image_report_batch(
    #     images,
    #     max_concurrency=5,
    #     on_progress=on_progress
    # )
    # print(f"Processed {results.total} images")

    # Process a directory
    # results = await async_client.image_report_directory(
    #     "path/to/images",
    #     recursive=True
    # )

    print("Async client initialized successfully")


if __name__ == "__main__":
    sync_example()
    asyncio.run(async_example())
