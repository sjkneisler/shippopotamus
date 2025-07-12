"""
Tests for the prompt_loader tool
"""

import os
import tempfile
from pathlib import Path
import pytest
from tools.prompt_loader import (
    load_prompt, load_index, list_prompts, 
    get_load_stats, validate_prompts, parse_prompt_header, _reset_cache
)


def test_parse_prompt_header():
    """Test header parsing functionality"""
    content = "<!-- id:TEST emoji:🧪 -->\n# Test Prompt"
    prompt_id, emoji = parse_prompt_header(content)
    assert prompt_id == "TEST"
    assert emoji == "🧪"
    
    # Test missing header
    content_no_header = "# Just a regular markdown file"
    prompt_id, emoji = parse_prompt_header(content_no_header)
    assert prompt_id is None
    assert emoji is None


def test_load_index():
    """Test loading the prompt index"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create prompts directory and index
        prompts_dir = Path("prompts")
        prompts_dir.mkdir()
        
        index_content = """<!-- id:INDEX emoji:🗺️ -->
# Prompt Index

This is the main index for all prompts.
"""
        index_file = prompts_dir / "00_INDEX.md"
        index_file.write_text(index_content)
        
        # Test loading
        result = load_index()
        
        assert "content" in result
        assert result["emoji"] == "🗺️"
        assert result["within_limit"] is True
        assert result["echo_required"] is True
        assert result["size_kb"] < 1.0


def test_load_prompt_with_cache():
    """Test loading prompts with caching"""
    _reset_cache()  # Reset cache for test isolation
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create test prompt
        prompts_dir = Path("prompts/axioms")
        prompts_dir.mkdir(parents=True)
        
        core_content = """<!-- id:CORE emoji:🧭 -->
# Core Axioms

These are the core principles of Shippopotamus.
"""
        core_file = prompts_dir / "CORE.md"
        core_file.write_text(core_content)
        
        # First load
        result1 = load_prompt("CORE")
        
        assert result1["id"] == "CORE"
        assert result1["emoji"] == "🧭"
        assert result1["echo_required"] is True
        assert result1["from_cache"] is False
        assert "tokens" in result1
        
        # Second load (should be cached)
        result2 = load_prompt("CORE")
        assert result2["from_cache"] is True
        
        # Force reload
        result3 = load_prompt("CORE", force_reload=True)
        assert result3["from_cache"] is False


def test_list_prompts_with_categories():
    """Test listing prompts with category filtering"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create prompts in different categories
        Path("prompts/axioms").mkdir(parents=True)
        Path("prompts/meta").mkdir(parents=True)
        
        # Create axiom prompts
        for name, emoji in [("CORE", "🧭"), ("QUALITY", "⚖️")]:
            content = f"<!-- id:{name} emoji:{emoji} -->\n# {name}"
            (Path("prompts/axioms") / f"{name}.md").write_text(content)
        
        # Create meta prompt
        meta_content = "<!-- id:backlog emoji:📋 -->\n# Backlog"
        (Path("prompts/meta") / "backlog.md").write_text(meta_content)
        
        # List all
        all_prompts = list_prompts()
        assert all_prompts["total"] == 3
        assert "axioms" in all_prompts["categories"]
        assert all_prompts["categories"]["axioms"]["count"] == 2
        
        # List by category
        axioms_only = list_prompts(category="axioms")
        assert axioms_only["total"] == 2
        
        meta_only = list_prompts(category="meta")
        assert meta_only["total"] == 1


def test_validate_prompts():
    """Test prompt validation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        prompts_dir = Path("prompts")
        prompts_dir.mkdir()
        
        # Create valid prompt
        valid_content = "<!-- id:VALID emoji:✅ -->\n# Valid Prompt"
        (prompts_dir / "valid.md").write_text(valid_content)
        
        # Create prompt missing emoji
        no_emoji = "<!-- id:NOEMOJI -->\n# Missing Emoji"
        (prompts_dir / "no_emoji.md").write_text(no_emoji)
        
        # Create prompt missing ID
        no_id = "<!-- emoji:❌ -->\n# Missing ID"
        (prompts_dir / "no_id.md").write_text(no_id)
        
        # Create oversized prompt (simulate with small limit)
        large_content = "<!-- id:LARGE emoji:📦 -->\n" + "x" * 15000
        (prompts_dir / "large.md").write_text(large_content)
        
        # Validate
        result = validate_prompts()
        
        assert result["valid"] is False
        assert len(result["issues"]) >= 3
        assert result["stats"]["total_files"] == 4
        assert result["stats"]["valid_headers"] == 2
        assert result["stats"]["missing_emoji"] == 1
        assert result["stats"]["missing_id"] == 1
        assert result["stats"]["oversized_files"] == 1


def test_get_load_stats():
    """Test getting load statistics"""
    _reset_cache()  # Reset cache for test isolation
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create a test prompt
        prompts_dir = Path("prompts")
        prompts_dir.mkdir()
        
        test_content = "<!-- id:TEST emoji:📊 -->\n# Test"
        (prompts_dir / "test.md").write_text(test_content)
        
        # Initial stats (empty)
        stats = get_load_stats()
        assert stats["total_loaded"] == 0
        assert stats["total_tokens"] == 0
        
        # Load a prompt
        load_prompt("TEST")
        
        # Check stats
        stats = get_load_stats()
        assert stats["total_loaded"] == 1
        assert stats["total_tokens"] > 0
        assert len(stats["loaded_prompts"]) == 1
        assert stats["loaded_prompts"][0]["id"] == "TEST"
        assert stats["loaded_prompts"][0]["emoji"] == "📊"