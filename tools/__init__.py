"""
Shippopotamus PromptOps Platform

A prompt management platform for AI applications.
Provides tools to load, save, compose, and manage prompts efficiently.
"""

from fastmcp import FastMCP

# Import all tool modules
from . import prompt_registry
from . import prompt_composer

# Create a single MCP instance for all tools
mcp = FastMCP()

# Tools are registered via @mcp.tool() decorators in their modules

__all__ = [
    "prompt_registry",
    "prompt_composer",
    "mcp"
]

# Version info
__version__ = "0.1.0"