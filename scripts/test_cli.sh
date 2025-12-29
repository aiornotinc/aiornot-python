#!/bin/bash
# Test all CLI commands against the staging API
# Run ./scripts/gen-test-data.sh first to create the test fixtures

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"
PROJECT_DIR="$SCRIPT_DIR/.."

cd "$PROJECT_DIR"

# Check fixtures exist
if [ ! -d "$FIXTURES_DIR" ] || [ -z "$(ls -A "$FIXTURES_DIR" 2>/dev/null)" ]; then
    echo "Error: Test fixtures not found. Run ./scripts/gen-test-data.sh first."
    exit 1
fi

# Set API credentials and base URL
# AIORNOT_API_KEY must be set in environment before running this script
if [ -z "$AIORNOT_API_KEY" ]; then
    echo "Error: AIORNOT_API_KEY environment variable is not set"
    exit 1
fi
export AIORNOT_BASE_URL="${AIORNOT_BASE_URL:-https://api.aiornot.com}"

# Check that token is valid
uv run aiornot token check

# Analyze an image file
uv run aiornot image "$FIXTURES_DIR/dummy_image.jpg"

# Analyze an image with options
uv run aiornot image "$FIXTURES_DIR/dummy_image.png" --only ai_generated --format table

# Analyze an image excluding certain analyses
uv run aiornot image "$FIXTURES_DIR/dummy_image.webp" --excluding nsfw --excluding deepfake --external-id my-tracking-id

# Analyze an image with different output formats
uv run aiornot image "$FIXTURES_DIR/dummy_image.jpg" --format json
uv run aiornot image "$FIXTURES_DIR/dummy_image.jpg" --format table
uv run aiornot image "$FIXTURES_DIR/dummy_image.jpg" --format minimal
uv run aiornot image "$FIXTURES_DIR/dummy_image.jpg" --quiet

# Analyze a video file
uv run aiornot video "$FIXTURES_DIR/dummy_video.mp4"

# Analyze a video with options
uv run aiornot video "$FIXTURES_DIR/dummy_video.mov" --only ai_video --format table

# Analyze a video excluding certain analyses
uv run aiornot video "$FIXTURES_DIR/dummy_video.mp4" --excluding deepfake_video --external-id my-video-id

# Analyze a video with different output formats
uv run aiornot video "$FIXTURES_DIR/dummy_video.mp4" --format json
uv run aiornot video "$FIXTURES_DIR/dummy_video.mp4" --format table
uv run aiornot video "$FIXTURES_DIR/dummy_video.mp4" --format minimal
uv run aiornot video "$FIXTURES_DIR/dummy_video.mp4" --quiet

# Analyze a voice/speech audio file
uv run aiornot voice "$FIXTURES_DIR/dummy_voice.mp3"

# Analyze voice with different output formats
uv run aiornot voice "$FIXTURES_DIR/dummy_voice.wav" --format json
uv run aiornot voice "$FIXTURES_DIR/dummy_voice.wav" --format table
uv run aiornot voice "$FIXTURES_DIR/dummy_voice.wav" --format minimal
uv run aiornot voice "$FIXTURES_DIR/dummy_voice.wav" --quiet

# Analyze a music audio file
uv run aiornot music "$FIXTURES_DIR/dummy_music.mp3"

# Analyze music with different output formats
uv run aiornot music "$FIXTURES_DIR/dummy_music.flac" --format json
uv run aiornot music "$FIXTURES_DIR/dummy_music.flac" --format table
uv run aiornot music "$FIXTURES_DIR/dummy_music.flac" --format minimal
uv run aiornot music "$FIXTURES_DIR/dummy_music.flac" --quiet

# Analyze text directly (string input) - must be at least 250 characters
uv run aiornot text "This is a sample text that needs to be analyzed for AI-generated content detection. The text must be at least two hundred and fifty characters long to meet the minimum requirements of the API. This paragraph contains enough words and characters to pass validation and be processed by the detection system."

# Analyze text with annotations
uv run aiornot text "This is a sample text that needs to be analyzed for AI-generated content detection. The text must be at least two hundred and fifty characters long to meet the minimum requirements of the API. This paragraph contains enough words and characters to pass validation and be processed by the detection system." --annotations

# Analyze text with external ID
uv run aiornot text "This is a sample text that needs to be analyzed for AI-generated content detection. The text must be at least two hundred and fifty characters long to meet the minimum requirements of the API. This paragraph contains enough words and characters to pass validation and be processed by the detection system." --external-id my-text-id

# Analyze text from a file
uv run aiornot text "$FIXTURES_DIR/dummy_text.txt" --file

# Analyze text from file with annotations
uv run aiornot text "$FIXTURES_DIR/dummy_text.txt" --file --annotations

# Analyze text with different output formats
uv run aiornot text "This is a sample text that needs to be analyzed for AI-generated content detection. The text must be at least two hundred and fifty characters long to meet the minimum requirements of the API. This paragraph contains enough words and characters to pass validation and be processed by the detection system." --format json
uv run aiornot text "This is a sample text that needs to be analyzed for AI-generated content detection. The text must be at least two hundred and fifty characters long to meet the minimum requirements of the API. This paragraph contains enough words and characters to pass validation and be processed by the detection system." --format table
uv run aiornot text "This is a sample text that needs to be analyzed for AI-generated content detection. The text must be at least two hundred and fifty characters long to meet the minimum requirements of the API. This paragraph contains enough words and characters to pass validation and be processed by the detection system." --format minimal
uv run aiornot text "This is a sample text that needs to be analyzed for AI-generated content detection. The text must be at least two hundred and fifty characters long to meet the minimum requirements of the API. This paragraph contains enough words and characters to pass validation and be processed by the detection system." --quiet

# Test color options
uv run aiornot image "$FIXTURES_DIR/dummy_image.jpg" --format table --color
uv run aiornot image "$FIXTURES_DIR/dummy_image.jpg" --format table --no-color

echo "All CLI tests passed!"
