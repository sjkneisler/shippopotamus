"""
Shippopotamus PromptOps Tools

Core tools for prompt management and context economy in agentic coding workflows.
"""

from fastmcp import FastMCP

# Import the prompt management tools
from . import prompt_loader
from . import prompt_registry

# Create a single MCP instance for all tools
mcp = FastMCP()

# The tools are already registered via @mcp.tool() decorators in their modules

__all__ = [
    "prompt_loader",
    "prompt_registry",
    "mcp"
]