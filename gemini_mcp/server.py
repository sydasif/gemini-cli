"""MCP server implementation that exposes research capabilities.

This module implements the MCP (Model Context Protocol) server using FastMCP that exposes
a web_search tool wrapping the research functionality.
"""

from mcp.server.fastmcp import FastMCP

from . import research  # Relative import is crucial here

mcp = FastMCP("Gemini Research")


@mcp.tool()
def web_search(query: str, model: str = None) -> str:
    """Performs a web search using the Gemini CLI.

    This tool wraps the research functionality to provide web search capabilities
    through the MCP interface.

    Args:
        query: The search query to execute
        model: Optional model to use (e.g., "gemini-2.5-pro", "gemini-2.5-flash")
               If not specified, uses default model with automatic fallback

    Returns:
        str: The search results or an error message if execution fails
    """
    try:
        return research.perform_research(query, model=model)
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    """Main entry point for the MCP server.

    Initializes and runs the FastMCP server to expose the web_search tool.
    """
    mcp.run()


if __name__ == "__main__":
    main()
