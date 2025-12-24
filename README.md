# Gemini CLI MCP Server

This project provides an MCP (Model Context Protocol) server that exposes research capabilities through the Gemini CLI as a web search tool for AI models. The architecture separates the core research functionality from the MCP server interface.

## Setup

1. Make sure you have `uv` installed
2. Install the tool globally:

   ```bash
   uv tool install git+https://github.com/sydasif/gemini-cli.git
   ```

   Or for local development:

   ```bash
   uv tool install --editable .
   ```

## Usage

To run the MCP server directly:

```bash
gemini-mcp
```

## Available Tools

### web_search

Performs web searches using the Gemini CLI with automatic model selection.

**Parameters:**

- `query` (required): The search query to execute
- `model` (optional): Specific model to use (e.g., "gemini-2.5-pro", "gemini-2.5-flash")
  If not specified, Gemini will use its default model selection

**Example:**

```python
# Using default model
result = await client.call_tool("web_search", arguments={"query": "latest AI research"})

# Using specific model
result = await client.call_tool("web_search", arguments={
    "query": "latest AI research",
    "model": "gemini-2.5-pro"
})
```

## Architecture

### Core Components

**gemini_mcp/server.py**: Implements the complete MCP server functionality that includes:
- The `web_search` tool that provides research and web search capabilities
- Direct integration with the Gemini CLI for executing research queries
- Input sanitization and safety measures to prevent injection attacks
- Proper MCP protocol compliance
- Comprehensive error handling for both the MCP interface and Gemini CLI execution

### Key Dependencies

- `mcp>=1.25.0`: Model Context Protocol implementation
- `uv`: Project management and dependency resolution
- Python 3.11+ runtime

## Connecting to Claude

To add this tool to Claude Code:

```bash
claude mcp add gemini-research -- gemini-mcp
```

## Requirements

- Python 3.11+
- `uv` package manager
- Gemini CLI tool installed and configured with a valid API key

## Development and Updates

To update the tool after making local changes:

```bash
# For local development (if installed with --editable)
uv tool install --editable --force .

# Or uninstall and reinstall
uv tool uninstall gemini-mcp
uv tool install --editable .
```

To update from the GitHub repository after changes have been pushed:

```bash
uv tool install --upgrade git+https://github.com/sydasif/gemini-cli.git
```

## Features

- **Automatic Model Selection**: Uses Gemini's default model when no specific model is provided
- **Model Flexibility**: Allows specifying different Gemini models (gemini-2.5-pro, gemini-2.5-flash, etc.) for different use cases
- **Web Search Capabilities**: Executes web searches with research functionality
- **Error Handling**: Robust error handling and reporting
