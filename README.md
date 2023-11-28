![AIORNOT Logo](./centered_logo_32x32.png)
# AIORNOT Python Client

[![PyPI version](https://badge.fury.io/py/aiornot.svg)](https://badge.fury.io/py/aiornot)

This is a Python client for the [AIORNOT](https://aiornot.com) API.

# Getting Started

## Registration and API Key

Register for an account at [AIORNOT](https://aiornot.com). Then, install the python client,

```bash
pip install aiornot
```

to use the client you will need to set the `AIORNOT_API_KEY` environment variable to your API key. You can find your API key on your [AIORNOT dashboard](https://aiornot.com/dashboard/api).

```bash
AIORNOT_API_KEY=your_api_key
```

> [!WARNING]  
> Never share your API key with anyone. It is a secret.

## Setup and Installation


If you cannot set the environment variable, you can pass it in as an argument to the client,

```python
client = AIOrNot(api_key='your_api_key')
```

## Code Examples

```python
from aiornot import Client

# Create a client (reads AIORNOT_API_KEY env)
client = Client()

# Classify an image by url
client.classify_image_by_url('https://thispersondoesnotexist.com')

# Classify an image by path
client.classify_image_by_path('path/to/image.jpg')

# Classify audio by url
client.classify_audio_by_url('https://www.youtube.com/watch?v=v4WiI4es_UI')

# Classify audio by path
client.classify_audio_by_path('path/to/audio.mp3')

# Check your token
client.check_token()

# Refresh your token
client.refresh_token()

# Revoke your token
client.revoke_token()

# Check if the API is up
client.check_api()
```

There is also an async client that follows the same API as the sync client, but with async methods.

```python
import asyncio
from aiornot import AsyncClient


async def main():
    client = AsyncClient()
    if await client.check_api():
        print('API is up!')
    else:
        print('API is down :(')

if __name__ == '__main__':
    asyncio.run(main())
```


## CLI Usage

You can install the CLI with the following [pipx](https://pypa.github.io/pipx/) command,

```bash
pipx install --upgrade aiornot
```

The CLI also looks for the `AIORNOT_API_KEY` environment variable. But it will also
look for a `~/.aiornot/config.json` file if the environment variable is not set. To
set it up, run the following command,

```bash
aiornot token config
``````

and follow the prompts. Afterwards, you can see a menu of commands with,

```bash
aionot
```

the two most useful ones being,

```bash
aiornot image [url|path]
aionot audio [text]
```