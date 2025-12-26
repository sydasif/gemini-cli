"""Pytest configuration for the Gemini MCP server tests."""

import pytest


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "asyncio: mark test as asyncio test")


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample file for testing."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Sample file content for testing")
    return file_path
