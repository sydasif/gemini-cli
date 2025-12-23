"""MCP server implementation that exposes research capabilities.

This module implements the MCP (Model Context Protocol) server using FastMCP that exposes
web_search and model_info tools wrapping the research functionality.
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
        model: Optional model to use (e.g., "gemini-2.5-pro", "gemini-2.5-flash")
               If not specified, uses Gemini's default model

    Returns:
        str: The search results or an error message if execution fails

    """
    try:
        return research.perform_research(query, model=model)
    except Exception as e:
        error_str = str(e)
        return f"Error: {error_str}"


@mcp.tool()
def model_info() -> str:
    """Provide information about available Gemini models.

    This tool returns a list of available models that can be used with the web_search tool,
    including their capabilities and use cases.

    Returns:
        str: Information about available Gemini models

    """
    try:
        models_info = """
Available Gemini Models:

1. gemini-2.5-pro
   - Capability: Highest capability for complex tasks
   - Use case: Complex reasoning, detailed analysis, creative tasks

2. gemini-2.5-flash
   - Capability: Balanced speed and capability
   - Use case: General purpose tasks, good balance of speed and quality

3. gemini-2.5-flash-lite
   - Capability: Optimized for speed and efficiency
   - Use case: Simple tasks, high-volume requests, quick responses

4. gemini-3-pro-preview
   - Capability: Next-generation flagship model (preview)
   - Use case: Advanced capabilities for complex reasoning (preview)

5. gemini-3-flash-preview
   - Capability: Next-generation optimized model (preview)
   - Use case: Fast responses with enhanced capabilities (preview)

To use a specific model, provide it as the 'model' parameter to the web_search tool.
If no model is specified, Gemini will use its default model selection.
"""
        return models_info.strip()
    except Exception as e:
        error_str = str(e)
        return f"Error: {error_str}"


def main() -> None:
    """Run the MCP server.

    Initializes and runs the FastMCP server to expose the web_search and model_info tools.

    """
    mcp.run()


if __name__ == "__main__":
    main()
