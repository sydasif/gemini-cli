"""MCP server implementation that exposes research and code review capabilities.

This module implements the MCP (Model Context Protocol) server using FastMCP that exposes
web_search and code_review tools.
"""

import os
import shutil
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Gemini Research")


@mcp.tool()
def web_search(
    query: str, model: str | None = None, allowed_tools: str = "google_web_search"
) -> str:
    """Perform a web search using the Gemini CLI.

    Args:
        query: The search query to execute
        model: Available model to use (e.g., "gemini-1.5-pro", "gemini-1.5-flash")
        allowed_tools: The tools allowed for the research (default: "google_web_search")
    """
    gemini_bin = os.environ.get("GEMINI_BIN") or shutil.which("gemini")

    if not gemini_bin:
        return "Error: The 'gemini' executable was not found in PATH."

    cmd = [gemini_bin]
    if model:
        cmd.extend(["-m", model])

    cmd.extend(["--allowed-tools", allowed_tools])
    cmd.append(query)

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: Gemini CLI error (Exit {e.returncode}): {e.stderr or 'Unknown error'}"
    except Exception as e:
        return f"Error: Unexpected error occurred - {str(e)}"


@mcp.tool()
def code_review(file_path: str, query: str) -> str:
    """Analyze a local source code file using the Gemini CLI.

    Args:
        file_path: The path to the file to be processed.
        query: The instruction or question about the code (e.g., "Review for security issues").
    """
    gemini_bin = os.environ.get("GEMINI_BIN") or shutil.which("gemini")

    if not gemini_bin:
        return "Error: The 'gemini' executable was not found in PATH."

    path = Path(file_path)
    if not path.exists():
        return f"Error: File '{file_path}' not found."

    try:
        # Read file content to pipe into stdin
        file_content = path.read_text(encoding="utf-8")

        # Execute: cat file | gemini -p "query"
        cmd = [gemini_bin, "-p", query]

        result = subprocess.run(
            cmd, input=file_content, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: Code review failed (Exit {e.returncode}): {e.stderr or 'Unknown error'}"
    except Exception as e:
        return f"Error: {str(e)}"


def main() -> None:
    """
    Initializes and runs the FastMCP server.
    """
    mcp.run()


if __name__ == "__main__":
    main()
