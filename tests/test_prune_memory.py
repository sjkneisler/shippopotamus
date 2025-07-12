"""
Smoke tests for the prune_memory tool
"""

import os
import tempfile
from pathlib import Path
import pytest
from tools.prune_memory import prune_memory


def test_prune_memory_empty_file():
    """Test pruning an empty or non-existent file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        result = prune_memory(count=5)
        
        assert result["status"] == "success"
        assert result["pruned"] == 0
        assert result["remaining"] == 0
        assert result["archived_to"] is None


def test_prune_memory_basic():
    """Test basic pruning functionality"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create memory file with content
        memory_dir = Path("memory-bank")
        memory_dir.mkdir()
        memory_file = memory_dir / "progress.md"
        
        lines = ["Line 1\n", "Line 2\n", "Line 3\n", "Line 4\n", "Line 5\n"]
        memory_file.write_text("".join(lines))
        
        # Prune 2 lines
        result = prune_memory(count=2, archive=False)
        
        assert result["status"] == "success"
        assert result["pruned"] == 2
        assert result["remaining"] == 3
        assert result["archived_to"] is None
        
        # Check remaining content
        remaining = memory_file.read_text()
        assert remaining == "Line 3\nLine 4\nLine 5\n"


def test_prune_memory_with_archive():
    """Test pruning with archiving"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create memory file with content
        memory_dir = Path("memory-bank")
        memory_dir.mkdir()
        memory_file = memory_dir / "progress.md"
        
        lines = ["Task 1\n", "Task 2\n", "Task 3\n"]
        memory_file.write_text("".join(lines))
        
        # Prune with archive
        result = prune_memory(count=1, archive=True)
        
        assert result["status"] == "success"
        assert result["pruned"] == 1
        assert result["remaining"] == 2
        assert result["archived_to"] is not None
        
        # Check archive was created
        archive_path = Path(result["archived_to"])
        assert archive_path.exists()
        archive_content = archive_path.read_text()
        assert "Task 1\n" in archive_content