"""
id: prune_memory
tag: memory_management

Memory pruning tool that removes the oldest lines from memory-bank/progress.md
while optionally saving pruned content to an archive.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def prune_memory(
    count: int = 10,
    archive: bool = True,
    archive_path: Optional[str] = None
) -> dict:
    """
    Prune the oldest lines from memory-bank/progress.md
    
    Args:
        count: Number of lines to prune (default: 10)
        archive: Whether to save pruned lines to archive (default: True)
        archive_path: Custom archive path (default: memory-bank/archive/YYYY-MM-DD.md)
    
    Returns:
        dict: {"status": "success", "pruned": N, "remaining": M, "archived_to": path}
    """
    memory_file = Path("memory-bank/progress.md")
    
    # Create memory-bank directory if it doesn't exist
    memory_file.parent.mkdir(exist_ok=True)
    
    # Initialize file if it doesn't exist
    if not memory_file.exists():
        memory_file.write_text("")
        return {
            "status": "success",
            "pruned": 0,
            "remaining": 0,
            "archived_to": None
        }
    
    # Read all lines
    lines = memory_file.read_text().splitlines(keepends=True)
    
    # If no lines to prune, return early
    if not lines or count <= 0:
        return {
            "status": "success",
            "pruned": 0,
            "remaining": len(lines),
            "archived_to": None
        }
    
    # Split into pruned and remaining
    pruned_lines = lines[:min(count, len(lines))]
    remaining_lines = lines[min(count, len(lines)):]
    
    # Archive if requested
    archived_to = None
    if archive and pruned_lines:
        if archive_path:
            archive_file = Path(archive_path)
        else:
            archive_dir = Path("memory-bank/archive")
            archive_dir.mkdir(exist_ok=True)
            archive_file = archive_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        
        # Append to archive
        with open(archive_file, "a") as f:
            f.write(f"\n---\n# Pruned on {datetime.now().isoformat()}\n")
            f.writelines(pruned_lines)
        
        archived_to = str(archive_file)
    
    # Write remaining lines back
    memory_file.write_text("".join(remaining_lines))
    
    return {
        "status": "success",
        "pruned": len(pruned_lines),
        "remaining": len(remaining_lines),
        "archived_to": archived_to
    }