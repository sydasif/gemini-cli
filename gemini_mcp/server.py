"""MCP server implementation that exposes research and code review capabilities.

This module implements the MCP (Model Context Protocol) server using FastMCP
that exposes web_search and code_review tools.
"""

from mcp.server.fastmcp import FastMCP

from .core import (
    execute_gemini_command,
    get_gemini_bin,
    read_file_safely,
    validate_file_path,
)

mcp = FastMCP("Gemini Research")


@mcp.tool()
def web_search(
    query: str, model: str | None = None, allowed_tools: str = "google_web_search"
) -> str:
    """Perform a web search using the Gemini CLI.

    Args:
        query: The search query to execute
        model: Optional default: None. The Gemini model to use for the search.
        Supported models are: ("gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
        "gemini-3-pro-preview", "gemini-3-flash-preview")

        allowed_tools: The tools allowed for the research (default: "google_web_search")
    """
    gemini_bin = get_gemini_bin()

    if not gemini_bin:
        return "Error: The 'gemini' executable was not found in PATH."

    cmd = [gemini_bin]
    if model:
        cmd.extend(["-m", model])

    cmd.extend(["--allowed-tools", allowed_tools, query])

    return execute_gemini_command(cmd)


@mcp.tool()
def code_review(
    file_path: str, query: str, allowed_tools: str = "codebase_investigator"
) -> str:
    """Analyze a local source code file using the Gemini CLI.

    Args:
        file_path: The path to the file to be processed.
        query: The instruction or question about the code (e.g., "Review for
            security issues").
        allowed_tools: The tools allowed for the code review (default:
            "codebase_investigator")
    """
    gemini_bin = get_gemini_bin()

    if not gemini_bin:
        return "Error: The 'gemini' executable was not found in PATH."

    # Validate the file path
    is_valid, error_msg, resolved_path = validate_file_path(file_path)
    if not is_valid:
        return error_msg

    # Read the file safely
    is_success, error_msg, file_content = read_file_safely(resolved_path)
    if not is_success:
        return error_msg

    # Execute: cat file | gemini -p "query" --allowed-tools "allowed_tools"
    cmd = [gemini_bin, "--allowed-tools", allowed_tools, "-p", query]

    return execute_gemini_command(cmd, input=file_content)


def main() -> None:
    """
    Initializes and runs the FastMCP server.
    """
    mcp.run()


if __name__ == "__main__":
    main()
