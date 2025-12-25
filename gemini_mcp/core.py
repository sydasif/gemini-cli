"""Core functionality for the Gemini MCP server.

This module contains the core functionality that can be reused across
different parts of the application, separate from the specific tool implementations.
"""

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
            input=input
        )  # noqa: S603
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: Gemini CLI error (Exit {e.returncode}): {e.stderr or 'Unknown error'}"
    except FileNotFoundError:
        return "Error: The 'gemini' executable was not found."
    except PermissionError:
        return "Error: Permission denied when trying to execute the 'gemini' command."
    except Exception as e:
        return f"Error: Unexpected error occurred - {str(e)}"


def validate_file_path(file_path: str) -> tuple[bool, str, Path | None]:
    """Validate a file path and resolve it safely.

    Args:
        file_path: The file path to validate

    Returns:
        A tuple of (is_valid, error_message, resolved_path)
    """
    path = Path(file_path)
    if not path.exists():
        return False, f"Error: File '{file_path}' not found.", None

    # Resolve the path to prevent path traversal attacks
    resolved_path = path.resolve()
    # Ensure the resolved path is within the current working directory
    try:
        resolved_path.relative_to(Path.cwd())
    except ValueError:
        return (
            False,
            f"Error: Access denied. File path '{file_path}' is outside the allowed directory.",
            None,
        )

    return True, "", resolved_path


def read_file_safely(resolved_path: Path) -> tuple[bool, str, str | None]:
    """Read a file safely, handling potential errors.

    Args:
        resolved_path: The resolved file path to read

    Returns:
        A tuple of (is_success, error_message, file_content)
    """
    try:
        file_content = resolved_path.read_text(encoding="utf-8")
        return True, "", file_content
    except UnicodeDecodeError:
        return (
            False,
            f"Error: File '{resolved_path}' is not a text file or contains invalid UTF-8 encoding.",
            None,
        )
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None
