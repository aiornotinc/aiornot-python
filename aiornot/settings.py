"""AIORNOT client settings."""

import os

API_KEY = os.environ.get("AIORNOT_API_KEY")
API_KEY_ERR = (
    "API key required. Set AIORNOT_API_KEY env var or pass api_key to Client()"
)

# Base URL without version path - endpoints specify their own version
# Override with AIORNOT_BASE_URL for testing/staging environments
BASE_URL = os.environ.get("AIORNOT_BASE_URL", "https://api.aiornot.com")
