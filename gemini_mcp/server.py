"""MCP server implementation that exposes research capabilities.

This module implements the MCP (Model Context Protocol) server using FastMCP that exposes
web_search tool with integrated research functionality.
"""

import os
import shutil
import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Gemini Research")


@mcp.tool()
def web_search(
    query: str, model: str | None = None, allowed_tools: str = "google_web_search"
) -> str:
    """Perform a web search using the Gemini CLI.

    This tool wraps the research functionality to provide web search capabilities
    through the MCP interface.

    Args:
        query: The search query to execute
        model: Available model to use (
        "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
        "gemini-3-pro-preview", "gemini-3-flash-preview",
        )
        allowed_tools: The tools allowed for the research (default: "google_web_search")

    Returns:
        str: The search results or an error message if execution fails
    """
    # Use shutil to find the executable in the system PATH
    gemini_bin = os.environ.get("GEMINI_BIN") or shutil.which("gemini")

    if not gemini_bin:
        error_msg = "The 'gemini' executable was not found in PATH. Please install the Gemini CLI."
        return f"Error: {error_msg}. Please ensure the 'gemini' CLI is installed and in PATH."

    # Build the command
    cmd = [gemini_bin]

    if model:
        cmd.extend(["-m", model])

    cmd.extend(["--allowed-tools", allowed_tools])
    cmd.append(query)

    # Capture output strictly
    # The cmd is constructed with the provided inputs
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        error_message = f"Gemini CLI error (Exit {e.returncode}): {error_msg}"
        return f"Error: Gemini CLI execution failed - {error_message}"
    except Exception as e:
        return f"Error: Unexpected error occurred - {str(e)}"


def main() -> None:
    """
    Initializes and runs the FastMCP server to expose the web_search tool.
    """
    mcp.run()


if __name__ == "__main__":
    main()
