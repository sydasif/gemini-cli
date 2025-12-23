from mcp.server.fastmcp import FastMCP
from . import research  # Relative import is crucial here

mcp = FastMCP("Gemini Research")

@mcp.tool()
def web_search(query: str) -> str:
    """
    Performs a web search using the Gemini CLI.
    """
    try:
        return research.perform_research(query)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()