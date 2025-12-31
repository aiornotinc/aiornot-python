"""Integration tests for AIORNOT API.

These tests make real API calls and require AIORNOT_API_KEY to be set.
They are marked with @pytest.mark.integration and skipped by default in CI.

To run integration tests locally:
    AIORNOT_API_KEY=your-key pytest -m integration
"""

import pytest

from aiornot import AsyncClient, Client


@pytest.mark.integration
class TestSyncClientIntegration:
    """Integration tests for sync client."""

    def test_is_live(self, api_key: str):
        """Test that API health check works."""
        client = Client(api_key=api_key)
        result = client.is_live()
        assert result is True

    def test_text_report(self, api_key: str):
        """Test text analysis with real API."""
        client = Client(api_key=api_key)
        result = client.text_report(
            "This is a sample text written by a human for testing purposes. "
            "The quick brown fox jumps over the lazy dog. "
            "Testing integration with the AIORNOT API."
        )
        assert result.id is not None
        assert result.verdict in ["ai", "human"]
        assert 0 <= result.confidence <= 1

    def test_text_report_with_annotations(self, api_key: str):
        """Test text analysis with annotations."""
        client = Client(api_key=api_key)
        result = client.text_report(
            "This is a longer text sample that should have multiple sentences. "
            "Each sentence might be analyzed separately. "
            "The API should return annotations for different parts of the text. "
            "This allows for more granular analysis of AI-generated content.",
            include_annotations=True,
        )
        assert result.id is not None
        # Annotations may or may not be present depending on text length


@pytest.mark.integration
class TestAsyncClientIntegration:
    """Integration tests for async client."""

    async def test_is_live(self, api_key: str):
        """Test that API health check works."""
        client = AsyncClient(api_key=api_key)
        result = await client.is_live()
        assert result is True

    async def test_text_report(self, api_key: str):
        """Test text analysis with real API."""
        client = AsyncClient(api_key=api_key)
        result = await client.text_report(
            "This is a sample text written by a human for testing purposes. "
            "The quick brown fox jumps over the lazy dog."
        )
        assert result.id is not None
        assert result.verdict in ["ai", "human"]
        assert 0 <= result.confidence <= 1

    async def test_text_batch(self, api_key: str):
        """Test batch text analysis."""
        client = AsyncClient(api_key=api_key)
        texts = [
            "First sample text for batch testing.",
            "Second sample text for batch testing.",
        ]
        result = await client.text_report_batch(texts, max_concurrency=2)
        assert result.total == 2
        assert result.succeeded + result.failed == 2


@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling."""

    def test_invalid_api_key(self):
        """Test that invalid API key raises authentication error."""
        from aiornot.exceptions import AIORNotAuthenticationError

        client = Client(api_key="invalid-api-key-12345")
        with pytest.raises(AIORNotAuthenticationError):
            client.text_report("Test text")
