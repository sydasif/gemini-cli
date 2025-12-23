# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This project implements an MCP (Model Context Protocol) server that exposes research capabilities through the Gemini CLI as a web search tool for AI models. The architecture separates the core research functionality from the MCP server interface.

## Architecture

### Core Components

1. **gemini_mcp/research.py**: Contains the core research functionality that acts as a wrapper around the Gemini CLI. It provides:
   - `perform_research()` function that executes Gemini CLI commands with web search capabilities
   - Input sanitization and safety measures
   - Error handling and reporting

2. **gemini_mcp/server.py**: Implements the MCP server using FastMCP that exposes:
   - A `web_search` tool that wraps the research functionality
   - Proper MCP protocol compliance
   - Error handling for the MCP interface

### Key Dependencies

- `mcp>=1.25.0`: Model Context Protocol implementation
- `uv`: Project management and dependency resolution
- Python 3.11+ runtime

## Development Commands

### Setup & Dependencies

```bash
# Install the tool globally using uv
uv tool install --editable .

# Add new dependencies
uv add package_name

# Add development dependencies
uv add --dev package_name
```

### Running the Server

```bash
# Run the MCP server directly
gemini-mcp
```

### Testing

```bash
# Run tests (if pytest is available)
uv run pytest

# Run a single test file
uv run pytest test_file.py
```

## Using the MCP Tools

The server exposes a `web_search` tool that can be called through the MCP interface:

```python
# Example usage through MCP client
result = await client.call_tool("web_search", arguments={"query": "your search query"})
```

## Development Guidelines

- The `research.py` module should maintain both library and CLI compatibility
- Input sanitization is critical for the `perform_research` function to prevent injection attacks
- The MCP server should properly handle errors and return meaningful error messages
- All MCP tools must have proper docstrings with Args documentation