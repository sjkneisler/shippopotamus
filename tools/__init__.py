"""
Shippopotamus Day-0 Tools Registration

This module registers all Day-0 tools with FastMCP for use in agentic workflows.
"""

from fastmcp import FastMCP

# Import all tool modules to register their tools
from . import prune_memory
from . import progress_queue
from . import tool_dedup_guard

# Create a single MCP instance for all tools
mcp = FastMCP()

# The tools are already registered via @mcp.tool decorators in their modules
# This file ensures they're all loaded when the tools package is imported

__all__ = [
    "prune_memory",
    "progress_queue", 
    "tool_dedup_guard",
    "mcp"
]