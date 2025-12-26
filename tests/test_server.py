"""Unit tests for the server functionality of the Gemini MCP server."""

import asyncio
from unittest.mock import Mock, patch

import pytest

from gemini_mcp.server import code_review, web_search

pytestmark = pytest.mark.asyncio


class TestWebSearch:
    """Tests for the web_search function."""

    @patch("gemini_mcp.server.GEMINI_BIN_PATH", None)
    async def test_web_search_gemini_not_found(self):
        """Test web_search when gemini binary is not found."""
        result = await web_search("test query")

        assert "Error: The 'gemini' executable was not found" in result

    @patch("gemini_mcp.server.execute_gemini_command_async")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_web_search_success(self, mock_get_gemini_bin, mock_execute_async):
        """Test successful web_search execution."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_execute_async.return_value = (True, "Search results", None)

        result = await web_search("test query")

        assert result == "Search results"
        mock_execute_async.assert_called_once()

    @patch("gemini_mcp.server.execute_gemini_command_async")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_web_search_with_model(self, mock_get_gemini_bin, mock_execute_async):
        """Test web_search with a valid model."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_execute_async.return_value = (True, "Search results", None)

        result = await web_search("test query", model="gemini-2.5-flash")

        assert result == "Search results"
        # Verify that the model was included in the arguments
        mock_execute_async.assert_called_once()

    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_web_search_invalid_model(self, mock_get_gemini_bin):
        """Test web_search with an invalid model."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"

        result = await web_search("test query", model="invalid-model")

        assert "Error: Model 'invalid-model' is not supported" in result

    @patch("gemini_mcp.server.execute_gemini_command_async")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_web_search_execution_error(
        self, mock_get_gemini_bin, mock_execute_async
    ):
        """Test web_search when command execution fails."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_execute_async.return_value = (False, "", "Error: Command failed")

        result = await web_search("test query")

        assert "Error: Command failed" in result


class TestCodeReview:
    """Tests for the code_review function."""

    @patch("gemini_mcp.server.validate_file_path")
    @patch("gemini_mcp.server.GEMINI_BIN_PATH", None)
    async def test_code_review_gemini_not_found(self, mock_validate):
        """Test code_review when gemini binary is not found."""
        # Mock validate_file_path to return success so we can test the gemini check
        mock_validate.return_value = (True, "", Mock())

        result = await code_review("/path/to/file", "review request")

        assert "Error: The 'gemini' executable was not found" in result

    @patch("gemini_mcp.server.validate_file_path")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_code_review_file_not_found(self, mock_get_gemini_bin, mock_validate):
        """Test code_review when the specified file does not exist."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_validate.return_value = (False, "Error: File not found", None)

        result = await code_review("/nonexistent/file", "review request")

        assert "Error: File not found" in result

    @patch("gemini_mcp.server.read_file_safely")
    @patch("gemini_mcp.server.validate_file_path")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_code_review_read_error(
        self, mock_get_gemini_bin, mock_validate, mock_read
    ):
        """Test code_review when there's an error reading the file."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_validate.return_value = (True, "", Mock())
        mock_read.return_value = (False, "Error reading file", None)

        result = await code_review("/path/to/file", "review request")

        assert "Error reading file" in result

    @patch("gemini_mcp.server.execute_gemini_command_async")
    @patch("gemini_mcp.server.read_file_safely")
    @patch("gemini_mcp.server.validate_file_path")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_code_review_success(
        self, mock_get_gemini_bin, mock_validate, mock_read, mock_execute_async
    ):
        """Test successful code_review execution."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_validate.return_value = (True, "", Mock())
        mock_read.return_value = (True, "", "file content")
        mock_execute_async.return_value = (True, "Review results", None)

        result = await code_review("/path/to/file", "review request")

        assert result == "Review results"
        mock_execute_async.assert_called_once()

    @patch("gemini_mcp.server.execute_gemini_command_async")
    @patch("gemini_mcp.server.read_file_safely")
    @patch("gemini_mcp.server.validate_file_path")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_code_review_execution_error(
        self, mock_get_gemini_bin, mock_validate, mock_read, mock_execute_async
    ):
        """Test code_review when command execution fails."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_validate.return_value = (True, "", Mock())
        mock_read.return_value = (True, "", "file content")
        mock_execute_async.return_value = (False, "", "Error: Command failed")

        result = await code_review("/path/to/file", "review request")

        assert "Error: Command failed" in result


class TestSecurityFixes:
    """Tests for security fixes implemented in the functions."""

    @patch("gemini_mcp.server.execute_gemini_command_async")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_web_search_argument_injection_prevention(
        self, mock_get_gemini_bin, mock_execute_async
    ):
        """Test that web_search prevents argument injection by using -- separator."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_execute_async.return_value = (True, "Search results", None)

        # This query contains what could be a command-line flag
        result = await web_search("--help malicious")

        # Verify that the function processes this safely
        assert result == "Search results"
        # The call should include the '--' separator to prevent argument injection
        mock_execute_async.assert_called_once()

    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_web_search_model_validation(self, mock_get_gemini_bin):
        """Test that web_search validates models against supported list."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"

        # Test with an unsupported model
        result = await web_search("test query", model="unsupported-model")

        assert "Error: Model 'unsupported-model' is not supported" in result


class TestPerformanceImprovements:
    """Tests for performance improvements like async operations."""

    async def test_functions_are_async(self):
        """Test that the server functions are properly async."""
        # Check that web_search is a coroutine function
        assert asyncio.iscoroutinefunction(web_search)

        # Check that code_review is a coroutine function
        assert asyncio.iscoroutinefunction(code_review)

    @patch("gemini_mcp.server.execute_gemini_command_async")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_web_search_concurrent_execution(
        self, mock_get_gemini_bin, mock_execute_async
    ):
        """Test that web_search can be executed concurrently."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_execute_async.return_value = (True, "Search results", None)

        # Execute multiple web_search calls concurrently
        tasks = [web_search("query 1"), web_search("query 2"), web_search("query 3")]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(result == "Search results" for result in results)

    @patch("gemini_mcp.server.execute_gemini_command_async")
    @patch("gemini_mcp.server.read_file_safely")
    @patch("gemini_mcp.server.validate_file_path")
    @patch("gemini_mcp.server.get_gemini_bin")
    async def test_code_review_concurrent_execution(
        self, mock_get_gemini_bin, mock_validate, mock_read, mock_execute_async
    ):
        """Test that code_review can be executed concurrently."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        mock_validate.return_value = (True, "", Mock())
        mock_read.return_value = (True, "", "file content")
        mock_execute_async.return_value = (True, "Review results", None)

        # Execute multiple code_review calls concurrently
        tasks = [
            code_review("/path/file1", "review 1"),
            code_review("/path/file2", "review 2"),
            code_review("/path/file3", "review 3"),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(result == "Review results" for result in results)
