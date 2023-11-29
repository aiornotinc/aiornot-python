import os


API_KEY = os.environ.get("AIORNOT_API_KEY")
API_KEY_ERR = (
    "API key must be provided or set as an environment variable AIORNOT_API_KEY"
)
BASE_URL = os.environ.get("AIORNOT_BASE_URL", "https://api.aiornot.com/v1")
