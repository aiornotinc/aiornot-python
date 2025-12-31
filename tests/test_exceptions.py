"""Tests for exception handling."""

from unittest.mock import MagicMock

import httpx
import pytest

from aiornot.common_client import _handle_error_response
from aiornot.exceptions import (
    AIORNotAPIError,
    AIORNotAuthenticationError,
    AIORNotError,
    AIORNotFileError,
    AIORNotRateLimitError,
    AIORNotServerError,
    AIORNotTimeoutError,
    AIORNotValidationError,
)


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_base_exception(self):
        """Test AIORNotError is base exception."""
        err = AIORNotError("Base error")
        assert str(err) == "Base error"
        assert isinstance(err, Exception)

    def test_api_error_attributes(self):
        """Test AIORNotAPIError has status_code and response."""
        err = AIORNotAPIError(
            "API error", status_code=400, response={"detail": "Bad request"}
        )
        assert err.status_code == 400
        assert err.response == {"detail": "Bad request"}
        assert "[400] API error" in str(err)

    def test_api_error_without_status_code(self):
        """Test AIORNotAPIError without status code."""
        err = AIORNotAPIError("API error")
        assert err.status_code is None
        assert str(err) == "API error"

    def test_authentication_error_inherits_from_api_error(self):
        """Test AIORNotAuthenticationError is APIError subclass."""
        err = AIORNotAuthenticationError("Invalid key", status_code=401)
        assert isinstance(err, AIORNotAPIError)
        assert isinstance(err, AIORNotError)

    def test_validation_error_inherits_from_api_error(self):
        """Test AIORNotValidationError is APIError subclass."""
        err = AIORNotValidationError("Invalid input", status_code=422)
        assert isinstance(err, AIORNotAPIError)

    def test_rate_limit_error_inherits_from_api_error(self):
        """Test AIORNotRateLimitError is APIError subclass."""
        err = AIORNotRateLimitError("Rate limited", status_code=429)
        assert isinstance(err, AIORNotAPIError)

    def test_server_error_inherits_from_api_error(self):
        """Test AIORNotServerError is APIError subclass."""
        err = AIORNotServerError("Server error", status_code=500)
        assert isinstance(err, AIORNotAPIError)

    def test_timeout_error_inherits_from_base(self):
        """Test AIORNotTimeoutError is base exception subclass."""
        err = AIORNotTimeoutError("Timeout")
        assert isinstance(err, AIORNotError)
        assert not isinstance(err, AIORNotAPIError)

    def test_file_error_inherits_from_base(self):
        """Test AIORNotFileError is base exception subclass."""
        err = AIORNotFileError("File not found")
        assert isinstance(err, AIORNotError)
        assert not isinstance(err, AIORNotAPIError)


class TestErrorResponseHandling:
    """Tests for _handle_error_response function."""

    def test_401_raises_authentication_error(self):
        """Test 401 response raises AIORNotAuthenticationError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.json.return_value = {"detail": "Invalid API key"}

        with pytest.raises(AIORNotAuthenticationError) as exc_info:
            _handle_error_response(mock_response)

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)

    def test_422_raises_validation_error(self):
        """Test 422 response raises AIORNotValidationError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 422
        mock_response.text = "Validation Error"
        mock_response.json.return_value = {"detail": "Invalid image format"}

        with pytest.raises(AIORNotValidationError) as exc_info:
            _handle_error_response(mock_response)

        assert exc_info.value.status_code == 422

    def test_422_with_list_detail(self):
        """Test 422 with list-style validation errors."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 422
        mock_response.text = "Validation Error"
        mock_response.json.return_value = {
            "detail": [
                {"loc": ["body", "image"], "msg": "field required"},
                {"loc": ["body", "text"], "msg": "invalid format"},
            ]
        }

        with pytest.raises(AIORNotValidationError) as exc_info:
            _handle_error_response(mock_response)

        # Should join multiple errors
        error_msg = str(exc_info.value)
        assert "field required" in error_msg
        assert "invalid format" in error_msg

    def test_429_raises_rate_limit_error(self):
        """Test 429 response raises AIORNotRateLimitError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_response.json.return_value = {"detail": "Rate limit exceeded"}

        with pytest.raises(AIORNotRateLimitError) as exc_info:
            _handle_error_response(mock_response)

        assert exc_info.value.status_code == 429

    def test_500_raises_server_error(self):
        """Test 500 response raises AIORNotServerError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"detail": "Internal error"}

        with pytest.raises(AIORNotServerError) as exc_info:
            _handle_error_response(mock_response)

        assert exc_info.value.status_code == 500

    def test_502_raises_server_error(self):
        """Test 502 response raises AIORNotServerError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 502
        mock_response.text = "Bad Gateway"
        mock_response.json.return_value = {"detail": "Bad gateway"}

        with pytest.raises(AIORNotServerError):
            _handle_error_response(mock_response)

    def test_503_raises_server_error(self):
        """Test 503 response raises AIORNotServerError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_response.json.return_value = {"detail": "Service unavailable"}

        with pytest.raises(AIORNotServerError):
            _handle_error_response(mock_response)

    def test_other_4xx_raises_api_error(self):
        """Test other 4xx responses raise generic AIORNotAPIError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.json.return_value = {"detail": "Access denied"}

        with pytest.raises(AIORNotAPIError) as exc_info:
            _handle_error_response(mock_response)

        assert exc_info.value.status_code == 403
        # Should not be a more specific subclass
        assert type(exc_info.value) is AIORNotAPIError

    def test_json_parse_failure_uses_text(self):
        """Test that JSON parse failure falls back to response text."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.text = "Plain text error message"
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with pytest.raises(AIORNotServerError) as exc_info:
            _handle_error_response(mock_response)

        # Should use text as the message since JSON failed
        assert exc_info.value.response == {"detail": "Plain text error message"}
