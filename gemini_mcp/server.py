"""MCP server implementation that exposes research and code review capabilities.

This module implements the MCP (Model Context Protocol) server using FastMCP
that exposes web_search and code_review tools with security enhancements and performance improvements.
"""

from mcp.server.fastmcp import FastMCP

from .core import (
    execute_gemini_command_async,
    get_gemini_bin,
    read_file_safely,
    validate_file_path,
)

# Define supported models for validation
SUPPORTED_MODELS = {
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
}

# Resolve gemini binary path once at module level
GEMINI_BIN_PATH = get_gemini_bin()

mcp = FastMCP("Gemini Research")


@mcp.tool()
async def web_search(
    query: str, model: str | None = None, allowed_tools: str = "google_web_search"
) -> str:
    """Perform a web search using the Gemini CLI.

    Args:
        query: The search query to execute. Argument injection is prevented using -- separator.
        model: Optional default: None. The Gemini model to use for the search.
        Supported models are: ("gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
        "gemini-3-pro-preview", "gemini-3-flash-preview"). Model validation is enforced.

        allowed_tools: The tools allowed for the research (default: "google_web_search")
    """
    if not GEMINI_BIN_PATH:
        return "Error: The 'gemini' executable was not found in PATH."

    # Validate model if provided
    if model and model not in SUPPORTED_MODELS:
        return f"Error: Model '{model}' is not supported. Choose from: {', '.join(SUPPORTED_MODELS)}"

    args = []
    if model:
        args.extend(["-m", model])

    args.extend(["--allowed-tools", allowed_tools, "--", query])

    success, stdout, error_msg = await execute_gemini_command_async(args)
    if not success:
        return error_msg or "Unknown error occurred"
    return stdout


@mcp.tool()
async def code_review(
    file_path: str, query: str, allowed_tools: str = "codebase_investigator"
) -> str:
    """Analyze a local source code file using the Gemini CLI.

    Args:
        file_path: The path to the file to be processed. Path validation and file size limits are enforced.
        query: The instruction or question about the code (e.g., "Review for
            security issues").
        allowed_tools: The tools allowed for the code review (default:
            "codebase_investigator")
    """
    if not GEMINI_BIN_PATH:
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
    args = ["--allowed-tools", allowed_tools, "-p", query]

    success, stdout, error_msg = await execute_gemini_command_async(
        args, input=file_content
    )
    if not success:
        return error_msg or "Unknown error occurred"
    return stdout


def main() -> None:
    """
    Initializes and runs the FastMCP server.
    """
    mcp.run()


if __name__ == "__main__":
    main()
