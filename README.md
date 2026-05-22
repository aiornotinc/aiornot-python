![AIORNOT Logo](./media/centered_logo_32x32.png)
# AIORNOT Python Client

![Tests](https://github.com/aiornotinc/aiornot-python/actions/workflows/test.yaml/badge.svg)
[![PyPI version](https://badge.fury.io/py/aiornot.svg)](https://badge.fury.io/py/aiornot)
[![Better Stack Badge](https://uptime.betterstack.com/status-badges/v2/monitor/y3x3.svg)](https://uptime.betterstack.com/?utm_source=status_badge)

This is a Python client for the [AIORNOT](https://aiornot.com) API.

# Getting Started

## Account Registration and API Key Generation

Register for an account at [AIORNOT](https://aiornot.com). After creating an account,
you can generate an API token via your [dashboard](https://aiornot.com/dashboard/api).

Click the `Create New API Token` button. A dialog opens where you can configure the token:

![](./media/create_token.png)

- **Token Name (Optional)** — a label to help you identify the token later (e.g. `cli-token`).
- **Set custom expiration date** — check this to choose your own expiration date. Tokens
  expire in 5 years by default; if you set a custom date, it must be in the future.

Click `Create Token` to generate the token, then copy it to your clipboard.

> [!WARNING]  
> Never share your API token with anyone. It is like a password. Copy it as soon as it is
> created, since you will not be able to view it again afterwards.

## Installing the Python Package

To install the python package, run the following command,

```bash
# If using uv (recommended)
uv add aiornot

# If using pip
pip install aiornot
```

Using the client requires an API token. You can set the API token in two ways.

The easier and more flexible way is to set an environment variable,

```bash
AIORNOT_API_KEY=your_api_key
```

Otherwise, you can pass the API token in as an argument to the client,

```python
from aiornot import Client, AsyncClient


client = Client(api_key='your_api_token')               # sync client
async_client = AsyncClient(api_key='your_api_token')    # async client
```

Failure to set either the environment variable or the API token argument will result in a runtime error.

## CLI Usage

AIOrNot also comes with a CLI. You can use it easily via [uv](https://docs.astral.sh/uv/),

```bash
# For fresh install
uvx aiornot

# Or install globally
uv tool install aiornot

# For upgrade
uv tool upgrade aiornot
```

The CLI looks for `AIORNOT_API_KEY` or `AIORNOT_API_TOKEN`. It will also look
for a `~/.aiornot/config.json` file if neither environment variable is set. To
set it up, run the following command,

```bash
uvx aiornot token config
```

and follow the prompts. Afterwards, you can see a menu of commands with,

```bash
uvx aiornot
```

Common commands:

```bash
# Classify an image by path
uvx aiornot image single path/to/image.jpg

# With optional parameters
uvx aiornot image single path/to/image.jpg --external-id my-id --only ai_generated --only deepfake

# Classify text from a file or stdin
uvx aiornot text single path/to/text.txt
cat path/to/text.txt | uvx aiornot text single -

# Classify a video by path
uvx aiornot video single path/to/video.mp4
uvx aiornot video single path/to/video.mp4 --only ai_video --only deepfake_video

# Download the first ~120 seconds of a video URL, classify it, and keep the file
uvx aiornot video from-url "https://example.com/video"

# Choose a different cap, download the full video, or delete the download afterwards
uvx aiornot video from-url "https://example.com/video" --max-duration 300
uvx aiornot video from-url "https://example.com/video" --max-duration 0
uvx aiornot video from-url "https://example.com/video" --delete-after

# Classify voice or music audio by path
uvx aiornot voice single path/to/voice.mp3
uvx aiornot music single path/to/music.mp3

# Download the first ~1 hour of audio from a URL, classify it, and keep the file
uvx aiornot voice from-url "https://example.com/video-or-audio"
uvx aiornot music from-url "https://example.com/video-or-audio"

# Choose a different cap, download the full audio, or delete the download afterwards
uvx aiornot voice from-url "https://example.com/video-or-audio" --max-duration 1800
uvx aiornot music from-url "https://example.com/video-or-audio" --max-duration 0
uvx aiornot music from-url "https://example.com/video-or-audio" --delete-after

# Batch from CSV files. The CSV should include a path column by default.
uvx aiornot image batch-csv images.csv --output image-results.jsonl
uvx aiornot text batch-csv texts.csv --output text-results.jsonl

# Batch by scanning folders. Resume is enabled by default and skips successful
# input IDs already present in the JSONL output file.
uvx aiornot video batch-scan ./videos --output video-results.jsonl
uvx aiornot voice batch-scan ./voice --output voice-results.jsonl
uvx aiornot music batch-scan ./music --output music-results.jsonl

# Generate stable external IDs from scanned relative paths.
uvx aiornot image batch-scan ./images --output image-results.jsonl --use-relpath-md5-as-external-id
```

Each media command has `single`, `batch-csv`, and `batch-scan` subcommands. Video,
voice, and music also have `from-url` subcommands. Batch commands append JSONL
records with an `input` object for correlation, an `ok` flag, and either a `response`
object or an `error` object. CSV batches use `path`, `source`, or `file` columns for
files; text CSV batches can also use a `text` column for literal text. Optional CSV
columns include `id` and `external_id`; `external_id` must be 36 characters or fewer.
Image and video CSV batches can also include `only` and `excluding` columns. Text CSV
batches can include `include_annotations`.

For `batch-scan`, external IDs are not generated by default. Pass
`--use-relpath-md5-as-external-id` to send the MD5 hex digest of each file's
relative path as its external ID.

`video from-url` shells out to `uvx yt-dlp@latest`, so `uvx` must be available
on `PATH`. It asks yt-dlp for the best available video and audio format, downloads
only the current video rather than a playlist, and writes the retained file under
`aiornot-downloads/` by default using a readable title-and-id filename. The default
`--max-duration` is `120` seconds; pass `--max-duration 0` to download the full
video. Duration limiting uses yt-dlp/ffmpeg download sections without forcing a
re-encode, so cuts may align to keyframe or container boundaries rather than being
exact to the millisecond. Pass `--delete-after` to remove the downloaded file after
analysis.

`voice from-url` and `music from-url` use the same `uvx yt-dlp@latest` flow, but
request only yt-dlp's best audio-only format. They default to `--max-duration 3600`
seconds. Pass `--max-duration 0` to download the full audio and `--delete-after` to
remove the downloaded file after analysis.

The client retries transient request failures by default, including HTTP 408, 409,
425, 429, 500, 502, 503, and 504 responses.

## MCP Server

AIORNOT can also run as a local stdio MCP server for clients that support the
Model Context Protocol. The MCP server requires Python 3.10 or newer, exposes
the same analysis operations as the CLI, and reads the API key from
`AIORNOT_API_KEY`, `AIORNOT_API_TOKEN`, or `~/.aiornot/config.json`.

Install the optional MCP dependencies when running the server:

```bash
uvx --from "aiornot[mcp]" aiornot-mcp
```

Example local MCP client configuration:

```json
{
  "mcpServers": {
    "aiornot": {
      "command": "uvx",
      "args": ["--from", "aiornot[mcp]", "aiornot-mcp"],
      "env": {
        "AIORNOT_API_KEY": "your_api_key"
      }
    }
  }
}
```

The server provides these tools:

- `aiornot_check_token`
- `aiornot_analyze_image_file`
- `aiornot_analyze_text`
- `aiornot_analyze_text_file`
- `aiornot_analyze_video_file`
- `aiornot_analyze_video_url`
- `aiornot_analyze_voice_file`
- `aiornot_analyze_voice_url`
- `aiornot_analyze_music_file`
- `aiornot_analyze_music_url`
- `aiornot_batch_csv`
- `aiornot_batch_scan`

The `aiornot_analyze_video_url` tool accepts `url`, `output_dir`, `max_duration`,
`delete_after`, `external_id`, `only`, and `excluding`, matching the CLI URL workflow.
The `aiornot_analyze_voice_url` and `aiornot_analyze_music_url` tools accept `url`,
`output_dir`, `max_duration`, and `delete_after`. The batch tools write the same JSONL
records as the CLI.

## View from 10,000 feet

```python
from aiornot import Client

# Create a client (reads AIORNOT_API_KEY env)
client = Client()

# Classify an image by path
resp = client.image_report_by_file_sync('path/to/image.jpg')

# Classify voice or music audio by path
voice_resp = client.voice_report_by_file_sync('path/to/voice.mp3')
music_resp = client.music_report_by_file_sync('path/to/music.mp3')

# Check if it's AI generated
if resp.is_ai():
    print("This image is AI generated")
else:
    print("This image is human created")

# Get detailed report info
print(f"Verdict: {resp.report.ai_generated.verdict}")
print(f"AI confidence: {resp.report.ai_generated.ai.confidence}")
print(f"Human confidence: {resp.report.ai_generated.human.confidence}")

# Check your token
resp = client.check_token()

# Check if the API is up
if client.is_live():
    print('API is up!')
```

There is also an async client that has the same methods as the sync client:

```python
import asyncio
from aiornot import AsyncClient


async def main():
    client = AsyncClient()
    if await client.is_live():
        print('API is up!')
    else:
        print('API is down :(')
    
    # Classify an image
    resp = await client.image_report_by_file_sync('path/to/image.jpg')
    print(f"AI generated: {resp.is_ai()}")


if __name__ == '__main__':
    asyncio.run(main())
```

## Optional Parameters

Image and video analysis support optional filters:

```python
# Sync client
resp = client.image_report_by_file_sync(
    'path/to/image.jpg',
    external_id='my-tracking-id',  # Optional tracking ID
    only=['ai_generated', 'deepfake'],  # Only include specific analysis types
    excluding=['nsfw']  # Exclude specific analysis types
)

# Async client
resp = await async_client.image_report_by_file_sync(
    'path/to/image.jpg',
    external_id='my-tracking-id',
    only=['ai_generated'],
    excluding=['nsfw', 'quality']
)
```

Valid image filter values are `ai_generated`, `deepfake`, `nsfw`, `quality`, and
`reverse_search`. Valid video filter values are `ai_video`, `ai_music`,
`ai_voice`, and `deepfake_video`.

Image, text, and video analysis also support an optional `external_id` for your
own tracking. It is sent only when explicitly provided, and must be 36 characters
or fewer.

Text analysis supports optional annotations:

```python
text_resp = client.text_report_sync(
    'Text to analyze',
    include_annotations=True,
    external_id='my-tracking-id',
)
```

## Response Structure

The API returns comprehensive reports with forward compatibility (new fields can be added):

```python
# Main response
resp.id  # Unique report ID
resp.created_at  # Timestamp
resp.external_id  # Your tracking ID (if provided)

# AI Generation Detection
resp.report.ai_generated.verdict  # 'ai', 'human', or 'unknown'
resp.report.ai_generated.ai.is_detected  # Boolean
resp.report.ai_generated.ai.confidence  # Float 0-1
resp.report.ai_generated.human.is_detected  # Boolean
resp.report.ai_generated.human.confidence  # Float 0-1

# Generator probabilities (if AI detected)
resp.report.ai_generated.generator.midjourney  # Float or None
resp.report.ai_generated.generator.dall_e  # Float or None
# ... and other generators

# Other analysis (if requested)
resp.report.deepfake  # Deepfake detection
resp.report.nsfw  # NSFW content detection
resp.report.quality  # Image quality assessment

# Image metadata
resp.report.meta.width  # Image width
resp.report.meta.height  # Image height
resp.report.meta.format  # File format
resp.report.meta.size_bytes  # File size
resp.report.meta.md5  # MD5 hash

# Text metadata is top-level
text_resp.metadata.word_count
text_resp.metadata.character_count
text_resp.metadata.token_count

# Video metadata
video_resp.report.meta.duration
video_resp.report.meta.total_bytes
video_resp.report.deepfake_video  # Deepfake video detection, if requested
```
