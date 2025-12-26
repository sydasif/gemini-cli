"""Core functionality for the Gemini MCP server.

This module contains the core functionality that can be reused across
different parts of the application, separate from the specific tool implementations.
Includes security enhancements, performance improvements, and standardized error handling.
"""

import asyncio
import os
import shutil
import subprocess
from pathlib import Path


def get_gemini_bin() -> str | None:
    """Get the path to the gemini executable."""
    return os.environ.get("GEMINI_BIN") or shutil.which("gemini")


def is_gemini_available() -> bool:
    """Check if the gemini executable is available."""
    return get_gemini_bin() is not None


def execute_gemini_command(cmd: list[str], input: str | None = None) -> str:
    """Execute a gemini command and return the result.

    Args:
        cmd: The command to execute as a list of strings
        input: Optional input to pass to the command via stdin

    Returns:
        The output from the command or an error message
    """
    try:
        # Security: cmd is constructed from validated inputs and gemini_bin path,
        # not directly from user input, reducing injection risk
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            input=input,
            encoding="utf-8",
        )  # noqa: S603
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Handle command execution errors (non-zero exit codes)
        error_msg = e.stderr or "Unknown error"
        return f"Error: Gemini CLI error (Exit {e.returncode}): {error_msg}"
    except FileNotFoundError:
        # Handle case where gemini executable is not found
        return "Error: The 'gemini' executable was not found."
    except PermissionError:
        # Handle permission errors when executing the command
        return "Error: Permission denied when trying to execute the 'gemini' command."
    except Exception as e:
        # Handle any other unexpected errors
        return f"Error: Unexpected error occurred - {str(e)}"


def execute_gemini_command_safe(
    cmd: list[str], input: str | None = None
) -> tuple[bool, str, str | None]:
    """Execute a gemini command and return the result in a consistent tuple format.

    Args:
        cmd: The command to execute as a list of strings
        input: Optional input to pass to the command via stdin

    Returns:
        A tuple of (success, stdout, error_message).
        If success is True, error_message is None.
        If success is False, stdout is empty string and error_message contains details.
    """
    try:
        # Security: cmd is constructed from validated inputs and gemini_bin path,
        # not directly from user input, reducing injection risk
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            input=input,
            encoding="utf-8",
        )  # noqa: S603
        return True, result.stdout, None
    except subprocess.CalledProcessError as e:
        # Handle command execution errors (non-zero exit codes)
        error_msg = e.stderr or "Unknown error"
        return False, "", f"Error: Gemini CLI error (Exit {e.returncode}): {error_msg}"
    except FileNotFoundError:
        # Handle case where gemini executable is not found
        return False, "", "Error: The 'gemini' executable was not found."
    except PermissionError:
        # Handle permission errors when executing the command
        return (
            False,
            "",
            "Error: Permission denied when trying to execute the 'gemini' command.",
        )
    except Exception as e:
        # Handle any other unexpected errors
        return False, "", f"Error: Unexpected error occurred - {str(e)}"


# Maximum file size allowed for reading (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


def validate_file_path(file_path: str) -> tuple[bool, str, Path | None]:
    """Validate a file path and resolve it safely.

    Args:
        file_path: The file path to validate

    Returns:
        A tuple of (is_valid, error_message, resolved_path)
    """
    # Convert the file path to a Path object
    path = Path(file_path)
    if not path.exists():
        # Check if the file exists before proceeding
        return False, f"Error: File '{file_path}' not found.", None

    # Resolve the path to prevent path traversal attacks (e.g., "../../../etc/passwd")
    resolved_path = path.resolve()
    # Ensure the resolved path is within the current working directory to prevent
    # access to files outside the intended directory
    try:
        resolved_path.relative_to(Path.cwd())
    except ValueError:
        # Path is outside the allowed directory structure
        error_msg = f"Error: Path outside allowed: '{file_path}'."
        return (
            False,
            error_msg,
            None,
        )

    return True, "", resolved_path


def read_file_safely(
    resolved_path: Path, max_size: int = MAX_FILE_SIZE
) -> tuple[bool, str, str | None]:
    """Read a file safely, handling potential errors.

    Args:
        resolved_path: The resolved file path to read
        max_size: Maximum file size allowed in bytes (default: 10MB)

    Returns:
        A tuple of (is_success, error_message, file_content)
    """
    try:
        # Check file size before reading to prevent memory exhaustion
        file_size = resolved_path.stat().st_size
        if file_size > max_size:
            return (
                False,
                f"Error: File too large ({file_size} bytes). Maximum allowed size is {max_size} bytes.",
                None,
            )

        file_content = resolved_path.read_text(encoding="utf-8")
        return True, "", file_content
    except UnicodeDecodeError:
        error_msg = f"Error: Invalid file format or encoding: '{resolved_path}'."
        return (
            False,
            error_msg,
            None,
        )
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None


async def execute_gemini_command_async(
    args: list[str], input: str | None = None
) -> tuple[bool, str, str | None]:
    """Execute a gemini command asynchronously and return the result.

    Args:
        args: List of arguments to pass to the gemini executable.
        input: Optional input to pass to the command via stdin.

    Returns:
        A tuple of (success, stdout, error_message).
        If success is True, error_message is None.
        If success is False, stdout is empty string and error_message contains details.
    """
    gemini_bin = get_gemini_bin()
    if not gemini_bin:
        return False, "", "Error: The 'gemini' executable was not found."

    # Construct the full command safely
    full_cmd = [gemini_bin, *args]

    try:
        # Create subprocess with asyncio
        process = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdin=asyncio.subprocess.PIPE if input else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            encoding="utf-8",
        )

        stdout, stderr = await process.communicate(input=input)

        if process.returncode != 0:
            return (
                False,
                "",
                f"Error: Gemini CLI error (Exit {process.returncode}): {stderr}",
            )

        return True, stdout, None
    except PermissionError:
        return (
            False,
            "",
            "Error: Permission denied when trying to execute the 'gemini' command.",
        )
    except Exception as e:
        return False, "", f"Error: Unexpected error occurred - {str(e)}"
