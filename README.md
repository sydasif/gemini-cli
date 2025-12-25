# Gemini CLI MCP Server

A Model Context Protocol (MCP) server that exposes research and code review capabilities through the Gemini CLI.

## Overview

This MCP server acts as a bridge between MCP clients and the Gemini CLI, providing web search and code review functionality. It implements the MCP (Model Context Protocol) specification using FastMCP framework.

## Features

- **Web Search Tool**: Performs web searches using the Gemini CLI with configurable models and allowed tools
- **Code Review Tool**: Analyzes source code files using the Gemini CLI with security validation
- **Secure File Access**: Implements path validation to prevent directory traversal attacks
- **Command Execution**: Safely executes Gemini CLI commands with proper error handling

## Prerequisites

- Python 3.11+
- Gemini CLI installed and available in PATH (or specify via GEMINI_BIN environment variable)

## Installation

```bash
# Clone the repository
git clone <repository-url>

# Navigate to project directory
cd gemini-mcp

# Install dependencies using uv
uv sync

# Or install in development mode
uv sync --dev
```

## Usage

### Running the Server

```bash
# Run the server directly
uv run python -m gemini_mcp.server

# Or use the installed command (after installation)
gemini-mcp
```

### Environment Variables

- `GEMINI_BIN`: Specify the path to the Gemini CLI executable (optional, defaults to searching in PATH)

## Tools

### web_search

Performs a web search using the Gemini CLI.

```python
web_search(
    query: str,                    # The search query to execute
    model: str | None = None,      # Available model to use (e.g., "gemini-1.5-pro", "gemini-1.5-flash")
    allowed_tools: str = "google_web_search"  # The tools allowed for the research (default: "google_web_search")
)
```

### code_review

Analyzes a local source code file using the Gemini CLI.

```python
code_review(
    file_path: str,                # The path to the file to be processed
    query: str,                    # The instruction or question about the code (e.g., "Review for security issues")
    allowed_tools: str = "codebase_investigator"  # The tools allowed for the code review (default: "codebase_investigator")
)
```

## Security Considerations

- File paths are validated to prevent directory traversal attacks
- Input is sanitized before command execution
- The server requires the `gemini` executable to be available in PATH or specified via GEMINI_BIN environment variable
- Error messages are designed to not expose sensitive system information

## Development

### Adding Dependencies

```bash
# Add runtime dependencies
uv add package_name

# Add development dependencies
uv add --dev pytest ruff
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=gemini_mcp
```

### Linting & Formatting

```bash
# Lint code
uv run ruff check .

# Auto-fix lint issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

## Architecture

### Core Components

- `gemini_mcp/server.py`: Main MCP server implementation with FastMCP framework
- `gemini_mcp/core.py`: Core functionality including secure file handling and command execution
- `pyproject.toml`: Project configuration using uv for dependency management

## License

[Add license information here]
