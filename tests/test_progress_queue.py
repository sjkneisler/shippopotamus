"""
Smoke tests for the progress_queue tool
"""

import os
import tempfile
from pathlib import Path
import pytest
from tools.progress_queue import progress_push, progress_pop, progress_list, progress_complete


def test_progress_queue_basic():
    """Test basic queue operations"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Push items
        result1 = progress_push("Task 1")
        assert result1["id"] == 1
        assert result1["position"] == 0
        assert result1["queue_size"] == 1
        
        result2 = progress_push("Task 2", importance=1, tags=["urgent"])
        assert result2["id"] == 2
        assert result2["position"] == 1
        assert result2["queue_size"] == 2
        
        # List items
        list_result = progress_list()
        assert list_result["total"] == 2
        assert list_result["sticky_count"] == 1
        assert len(list_result["items"]) == 2
        
        # Pop non-sticky item
        pop_result = progress_pop()
        assert pop_result["content"] == "Task 1"
        assert pop_result["importance"] == 0
        
        # Try to pop sticky item (should fail)
        pop_result2 = progress_pop()
        assert pop_result2.get("error") == "empty"


def test_progress_complete():
    """Test completing specific items"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Push items
        result1 = progress_push("Task A")
        result2 = progress_push("Task B", importance=2)
        
        # Complete first task
        complete_result = progress_complete(result1["id"])
        assert complete_result["status"] == "success"
        assert "completed_at" in complete_result
        
        # Try to complete already completed task
        complete_again = progress_complete(result1["id"])
        assert complete_again.get("error") == "already_completed"
        
        # Try to complete non-existent task
        complete_invalid = progress_complete(999)
        assert complete_invalid.get("error") == "not_found"


def test_progress_list_filters():
    """Test list filters"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Push items with different tags
        progress_push("Backend task", tags=["backend", "api"])
        progress_push("Frontend task", tags=["frontend", "ui"])
        progress_push("Database task", tags=["backend", "db"])
        
        # Complete one task
        progress_complete(2)
        
        # List all incomplete
        list_all = progress_list()
        assert list_all["total"] == 2
        
        # List with completed
        list_with_completed = progress_list(include_completed=True)
        assert list_with_completed["total"] == 3
        
        # List by tag
        list_backend = progress_list(tag_filter="backend")
        assert list_backend["total"] == 2