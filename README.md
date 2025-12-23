# Gemini CLI MCP Server

This project provides an MCP (Model Context Protocol) server that exposes research capabilities through the Gemini CLI as a web search tool for AI models. The architecture separates the core research functionality from the MCP server interface.

## Setup

1. Make sure you have `uv` installed
2. Install the tool globally:
   ```bash
   uv tool install git+https://github.com/YOUR_USERNAME/gemini-cli.git
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

## Connecting to Claude

To add this tool to Claude Code:
```bash
claude mcp add gemini-research -- gemini-mcp
```

## Requirements

- Python 3.11+
- `uv` package manager
- Gemini CLI tool installed and configured with a valid API key