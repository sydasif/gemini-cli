"""Unit tests for the core functionality of the Gemini MCP server."""

import asyncio
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from gemini_mcp.core import (
    execute_gemini_command,
    execute_gemini_command_async,
    execute_gemini_command_safe,
    get_gemini_bin,
    is_gemini_available,
    read_file_safely,
    validate_file_path,
)


class TestGetGeminiBin:
    """Tests for get_gemini_bin function."""

    @patch("gemini_mcp.core.shutil.which")
    def test_get_gemini_bin_from_env_var(self, mock_which):
        """Test getting gemini binary from environment variable."""
        with patch.dict("os.environ", {"GEMINI_BIN": "/custom/path/gemini"}):
            result = get_gemini_bin()
            assert result == "/custom/path/gemini"
            mock_which.assert_not_called()

    @patch("gemini_mcp.core.shutil.which")
    def test_get_gemini_bin_from_path(self, mock_which):
        """Test getting gemini binary from PATH."""
        mock_which.return_value = "/usr/bin/gemini"
        with patch.dict("os.environ", {}, clear=True):
            result = get_gemini_bin()
            assert result == "/usr/bin/gemini"
            mock_which.assert_called_once_with("gemini")

    @patch("gemini_mcp.core.shutil.which")
    def test_get_gemini_bin_not_found(self, mock_which):
        """Test when gemini binary is not found."""
        mock_which.return_value = None
        with patch.dict("os.environ", {}, clear=True):
            result = get_gemini_bin()
            assert result is None


class TestIsGeminiAvailable:
    """Tests for is_gemini_available function."""

    @patch("gemini_mcp.core.get_gemini_bin")
    def test_gemini_available(self, mock_get_gemini_bin):
        """Test when gemini is available."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"
        assert is_gemini_available() is True

    @patch("gemini_mcp.core.get_gemini_bin")
    def test_gemini_not_available(self, mock_get_gemini_bin):
        """Test when gemini is not available."""
        mock_get_gemini_bin.return_value = None
        assert is_gemini_available() is False


class TestValidateFilePath:
    """Tests for validate_file_path function."""

    def test_valid_file_path(self, tmp_path):
        """Test validating a valid file path."""
        # Create a test file in a subdirectory of the current working directory for the test

        # Create a temporary file in the current directory for the test
        test_file = Path(tmp_path) / "test.txt"
        test_file.write_text("test content")

        # Since tmp_path is typically outside the project directory, we need to handle the relative_to check
        # Let's just test the existence and path resolution
        is_valid, error_msg, resolved_path = validate_file_path(str(test_file))

        # The test may fail due to the relative path check, so let's check if it's the expected error
        if not is_valid:
            # If it's a "path outside allowed" error, the file exists but is outside the working directory
            # This is expected behavior for pytest tmp_path
            if "outside allowed" in error_msg:
                # For this test, let's create a file in a more appropriate location
                # Create a file in the project directory for this test
                current_dir_file = Path(".") / "test_temp_file.txt"
                current_dir_file.write_text("test content")

                is_valid, error_msg, resolved_path = validate_file_path(
                    str(current_dir_file)
                )

                # Clean up
                current_dir_file.unlink(missing_ok=True)

                assert is_valid is True
                assert error_msg == ""
                assert resolved_path == current_dir_file.resolve()
            else:
                # If it's a different error, fail the test
                assert is_valid is True
        else:
            # If the path validation passed, check the results
            assert is_valid is True
            assert error_msg == ""
            assert resolved_path == test_file.resolve()

    def test_nonexistent_file_path(self, tmp_path):
        """Test validating a nonexistent file path."""
        nonexistent_file = tmp_path / "nonexistent.txt"

        is_valid, error_msg, resolved_path = validate_file_path(str(nonexistent_file))

        assert is_valid is False
        assert "not found" in error_msg
        assert resolved_path is None

    def test_path_traversal_attempt(self, tmp_path):
        """Test preventing path traversal attacks."""
        # Create a file in a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.txt"
        test_file.write_text("test content")

        # Try to access the file from a parent directory context
        malicious_path = tmp_path / "subdir" / ".." / ".." / "etc" / "passwd"

        is_valid, error_msg, resolved_path = validate_file_path(str(malicious_path))

        # The path won't exist, so it should fail for that reason first
        assert is_valid is False
        assert "not found" in error_msg or "outside allowed" in error_msg


class TestReadFileSafely:
    """Tests for read_file_safely function."""

    def test_read_valid_file(self, tmp_path):
        """Test reading a valid file."""
        test_file = tmp_path / "test.txt"
        expected_content = "Hello, World!"
        test_file.write_text(expected_content)

        is_success, error_msg, file_content = read_file_safely(test_file)

        assert is_success is True
        assert error_msg == ""
        assert file_content == expected_content

    def test_read_large_file(self, tmp_path):
        """Test reading a file that exceeds the size limit."""
        test_file = tmp_path / "large.txt"
        # Create a file larger than the default 10MB limit
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        test_file.write_text(large_content)

        is_success, error_msg, file_content = read_file_safely(
            test_file, max_size=10 * 1024 * 1024
        )  # 10MB limit

        assert is_success is False
        assert "File too large" in error_msg
        assert file_content is None

    def test_read_binary_file(self, tmp_path):
        """Test handling a binary file that can't be decoded as UTF-8."""
        test_file = tmp_path / "binary.bin"
        # Write some binary data that will cause a UnicodeDecodeError
        # Use content that's more likely to cause a decode error
        test_file.write_bytes(b"\x80\x81\x82\x83")

        is_success, error_msg, file_content = read_file_safely(test_file)

        # This should fail with a UnicodeDecodeError, which is caught
        assert is_success is False
        assert "Invalid file format or encoding" in error_msg
        assert file_content is None


class TestExecuteGeminiCommand:
    """Tests for execute_gemini_command function (original version)."""

    @patch("gemini_mcp.core.subprocess.run")
    def test_execute_success(self, mock_run):
        """Test successful command execution."""
        mock_result = Mock()
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch("gemini_mcp.core.get_gemini_bin", return_value="/usr/bin/gemini"):
            result = execute_gemini_command(["test", "arg"])

            # Original function returns a string, not a tuple
            assert result == "Command output"
            mock_run.assert_called_once()

    @patch("gemini_mcp.core.subprocess.run")
    def test_execute_command_error(self, mock_run):
        """Test command execution with CalledProcessError."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["cmd"], stderr="Error message"
        )

        with patch("gemini_mcp.core.get_gemini_bin", return_value="/usr/bin/gemini"):
            result = execute_gemini_command(["test", "arg"])

            # Should return an error string
            assert "Error: Gemini CLI error" in result

    @patch("gemini_mcp.core.subprocess.run")
    def test_execute_gemini_not_found(self, mock_run):
        """Test when gemini binary is not found during execution."""
        mock_run.side_effect = FileNotFoundError()

        result = execute_gemini_command(["/nonexistent/gemini", "test", "arg"])

        # Should return an error string
        assert "Error: The 'gemini' executable was not found." in result


class TestExecuteGeminiCommandSafe:
    """Tests for execute_gemini_command_safe function."""

    @patch("gemini_mcp.core.subprocess.run")
    def test_execute_safe_success(self, mock_run):
        """Test successful command execution with safe function."""
        mock_result = Mock()
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch("gemini_mcp.core.get_gemini_bin", return_value="/usr/bin/gemini"):
            success, stdout, error_msg = execute_gemini_command_safe(["test", "arg"])

            assert success is True
            assert stdout == "Command output"
            assert error_msg is None
            mock_run.assert_called_once()

    @patch("gemini_mcp.core.subprocess.run")
    def test_execute_safe_command_error(self, mock_run):
        """Test command execution with CalledProcessError using safe function."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["cmd"], stderr="Error message"
        )

        with patch("gemini_mcp.core.get_gemini_bin", return_value="/usr/bin/gemini"):
            success, stdout, error_msg = execute_gemini_command_safe(["test", "arg"])

            assert success is False
            assert stdout == ""
            assert "Error: Gemini CLI error" in error_msg


class TestExecuteGeminiCommandAsync:
    """Tests for execute_gemini_command_async function."""

    @pytest.mark.asyncio
    @patch("gemini_mcp.core.asyncio.create_subprocess_exec")
    @patch("gemini_mcp.core.get_gemini_bin")
    async def test_execute_async_success(
        self, mock_get_gemini_bin, mock_create_subprocess
    ):
        """Test successful async command execution."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"

        # Mock the process object with the correct interface
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=("stdout", "stderr"))
        mock_process.returncode = 0
        mock_create_subprocess.return_value = mock_process

        success, stdout, error_msg = await execute_gemini_command_async(["test", "arg"])

        assert success is True
        assert stdout == "stdout"
        assert error_msg is None
        mock_create_subprocess.assert_called_once()

    @pytest.mark.asyncio
    @patch("gemini_mcp.core.asyncio.create_subprocess_exec")
    @patch("gemini_mcp.core.get_gemini_bin")
    async def test_execute_async_error(
        self, mock_get_gemini_bin, mock_create_subprocess
    ):
        """Test async command execution with error."""
        mock_get_gemini_bin.return_value = "/usr/bin/gemini"

        # Simulate an exception during subprocess creation
        mock_create_subprocess.side_effect = Exception("Process creation failed")

        success, stdout, error_msg = await execute_gemini_command_async(["test", "arg"])

        assert success is False
        assert stdout == ""
        assert "Error: Unexpected error occurred" in error_msg


# Run async tests using pytest-asyncio
@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Async tests for the core module."""

    @pytest.mark.parametrize("func", [execute_gemini_command_async])
    async def test_async_functions_exist(self, func):
        """Ensure async functions are properly defined."""
        assert asyncio.iscoroutinefunction(func)
