"""
Tests for the prompt_registry tool
"""

import os
import tempfile
from pathlib import Path
import pytest
from tools.prompt_registry import (
    register_prompt_load, get_session_report, estimate_context_usage,
    new_session, get_all_sessions_summary, _reset_registry
)


def test_register_prompt_load():
    """Test registering prompt loads"""
    # Reset registry for test isolation
    _reset_registry()
    # Start fresh
    new_session()
    
    # Register a load
    result = register_prompt_load(
        prompt_id="CORE",
        emoji="🧭",
        tokens=500,
        source_path="prompts/axioms/CORE.md",
        echo_confirmed=True
    )
    
    assert result["registered"] is True
    assert result["load_number"] == 1
    assert result["session_total_tokens"] == 500
    assert result["echo_contract"] == "fulfilled"
    
    # Register another load
    result2 = register_prompt_load(
        prompt_id="QUALITY",
        emoji="⚖️",
        tokens=300,
        source_path="prompts/axioms/QUALITY.md",
        echo_confirmed=False
    )
    
    assert result2["load_number"] == 2
    assert result2["session_total_tokens"] == 800
    assert result2["echo_contract"] == "pending"


def test_get_session_report():
    """Test session reporting"""
    # Reset registry for test isolation
    _reset_registry()
    # Start fresh session
    new_session()
    
    # Register multiple loads
    register_prompt_load("CORE", "🧭", 500, "prompts/CORE.md", True)
    register_prompt_load("CORE", "🧭", 500, "prompts/CORE.md", True)  # Duplicate
    register_prompt_load("QUALITY", "⚖️", 300, "prompts/QUALITY.md", False)
    
    # Get report
    report = get_session_report()
    
    assert report["total_loads"] == 3
    assert report["unique_prompts"] == 2
    assert report["total_tokens"] == 1300
    assert report["average_tokens_per_load"] == 433  # 1300 // 3
    assert "66.7%" in report["echo_contract_compliance"]  # 2/3 confirmed
    
    # Check most loaded
    assert len(report["most_loaded_prompts"]) >= 1
    assert report["most_loaded_prompts"][0]["id"] == "CORE"
    assert report["most_loaded_prompts"][0]["loads"] == 2
    
    # Check categorization
    assert "axioms" in report["prompts_by_category"]
    assert "CORE" in report["prompts_by_category"]["axioms"]


def test_estimate_context_usage():
    """Test context usage estimation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create test prompts
        prompts_dir = Path("prompts/axioms")
        prompts_dir.mkdir(parents=True)
        
        # Create some prompts with known sizes
        prompts_data = [
            ("CORE", "🧭", "x" * 2000),  # ~500 tokens
            ("QUALITY", "⚖️", "y" * 1200),  # ~300 tokens
            ("PATTERNS", "🪢", "z" * 4000)  # ~1000 tokens
        ]
        
        for name, emoji, content in prompts_data:
            full_content = f"<!-- id:{name} emoji:{emoji} -->\n{content}"
            (prompts_dir / f"{name}.md").write_text(full_content)
        
        # Estimate usage
        result = estimate_context_usage(["CORE", "QUALITY", "NONEXISTENT"])
        
        assert result["requested_prompts"] == 3
        assert result["found_prompts"] == 2
        assert "NONEXISTENT" in result["missing_prompts"]
        assert result["total_estimated_tokens"] > 0
        assert len(result["estimates"]) == 2
        
        # Test large context warning
        result_large = estimate_context_usage(["CORE", "QUALITY", "PATTERNS"] * 10)
        assert len(result_large["recommendations"]) > 0


def test_multiple_sessions():
    """Test multiple session management"""
    # Reset registry for test isolation
    _reset_registry()
    # First session
    new_session()
    register_prompt_load("CORE", "🧭", 500, "prompts/CORE.md", True)
    
    # Second session
    result = new_session()
    assert result["previous_sessions"] == 1
    
    register_prompt_load("QUALITY", "⚖️", 300, "prompts/QUALITY.md", True)
    
    # Get all sessions summary
    summary = get_all_sessions_summary()
    
    assert summary["total_sessions"] == 2
    assert summary["total_tokens_all_time"] == 800
    assert summary["total_loads_all_time"] == 2
    assert len(summary["sessions"]) == 2
    
    # Check current session marking
    current_marked = sum(1 for s in summary["sessions"] if s["is_current"])
    assert current_marked == 1