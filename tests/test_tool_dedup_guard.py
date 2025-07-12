"""
Smoke tests for the tool_dedup_guard tool
"""

import os
import tempfile
import time
from pathlib import Path
import pytest
from tools.tool_dedup_guard import tool_dedup_guard, register_file_read, clear_dedup_log


def test_dedup_guard_basic():
    """Test basic deduplication"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # First call should be safe
        result1 = tool_dedup_guard("test_tool", {"param1": "value1"})
        assert result1["safe"] is True
        assert result1["reason"] == "No duplicate detected"
        
        # Immediate duplicate should be blocked
        result2 = tool_dedup_guard("test_tool", {"param1": "value1"})
        assert result2["safe"] is False
        assert "Duplicate call detected" in result2["reason"]
        
        # Different params should be safe
        result3 = tool_dedup_guard("test_tool", {"param1": "value2"})
        assert result3["safe"] is True
        
        # Different tool same params should be safe
        result4 = tool_dedup_guard("other_tool", {"param1": "value1"})
        assert result4["safe"] is True


def test_dedup_guard_ttl():
    """Test TTL expiration"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # First call
        result1 = tool_dedup_guard("test_tool", {"data": "test"}, ttl_seconds=1)
        assert result1["safe"] is True
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should be safe again
        result2 = tool_dedup_guard("test_tool", {"data": "test"}, ttl_seconds=1)
        assert result2["safe"] is True


def test_safe_write_rule():
    """Test safe-write rule enforcement"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Try to write without reading first
        result1 = tool_dedup_guard("write_file", {"file_path": "/test/file.txt", "content": "data"})
        assert result1["safe"] is False
        assert "Safe-write rule violation" in result1["reason"]
        
        # Register file read
        register_result = register_file_read("/test/file.txt")
        assert register_result["status"] == "success"
        
        # Now write should be safe
        result2 = tool_dedup_guard("write_file", {"file_path": "/test/file.txt", "content": "data"})
        assert result2["safe"] is True


def test_clear_dedup_log():
    """Test clearing old entries"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Add some entries
        tool_dedup_guard("tool1", {"data": "1"})
        tool_dedup_guard("tool2", {"data": "2"})
        tool_dedup_guard("tool3", {"data": "3"})
        
        # Clear immediately (nothing should be deleted with default 1 hour)
        result = clear_dedup_log()
        assert result["deleted"] == 0
        assert result["remaining"] == 3
        
        # Clear with 0 seconds threshold (delete all)
        result2 = clear_dedup_log(older_than_seconds=0)
        assert result2["deleted"] == 3
        assert result2["remaining"] == 0