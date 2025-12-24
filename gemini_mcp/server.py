"""MCP server implementation that exposes research capabilities.

This module implements the MCP (Model Context Protocol) server using FastMCP that exposes
web_search tool wrapping the research functionality.
"""

from mcp.server.fastmcp import FastMCP

from . import research  # Relative import is crucial here

mcp = FastMCP("Gemini Research")


@mcp.tool()
def web_search(query: str, model: str | None = None) -> str:
    """Perform a web search using the Gemini CLI.

    This tool wraps the research functionality to provide web search capabilities
    through the MCP interface.

    Args:
        query: The search query to execute
        model: Available model to use (
        "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
        "gemini-3-pro-preview", "gemini-3-flash-preview",
    )

    Returns:
        str: The search results or an error message if execution fails
    """
    try:
        if not query or not query.strip():
            return "Error: Query cannot be empty"

        # Limit query length for security
        if len(query) > 1000:
            return "Error: Query too long (max 1000 characters)"

        return research.perform_research(query, model=model)
    except FileNotFoundError as e:
        return f"Error: {str(e)}. Please ensure the 'gemini' CLI is installed and in PATH."
    except ValueError as e:
        return f"Error: Invalid input - {str(e)}"
    except RuntimeError as e:
        return f"Error: Gemini CLI execution failed - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error occurred - {str(e)}"




def main() -> None:
    """
    Initializes and runs the FastMCP server to expose the web_search tool.
    """
    mcp.run()


if __name__ == "__main__":
    main()
