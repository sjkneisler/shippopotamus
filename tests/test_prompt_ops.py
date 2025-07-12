"""
Tests for Shippopotamus PromptOps platform
"""

import os
import tempfile
from pathlib import Path
import pytest
import sys
sys.path.append('..')

from tools.prompt_registry import get_prompt, save_prompt, load_prompts, init_db
from tools.prompt_composer import compose_prompts, list_available, estimate_context


class TestPromptRegistry:
    """Test the core registry functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        init_db()
    
    def test_get_default_prompt(self):
        """Test loading default prompts"""
        # This will fail in test env without the actual prompt files
        # In real usage, these files exist in the package
        result = get_prompt("nonexistent")
        assert "error" in result
    
    def test_save_and_get_custom_prompt(self):
        """Test saving and retrieving custom prompts"""
        # Save a prompt
        save_result = save_prompt(
            name="test_prompt",
            content="This is a test prompt",
            tags=["test", "example"]
        )
        
        assert save_result["saved"] is True
        assert save_result["name"] == "test_prompt"
        
        # Retrieve it
        get_result = get_prompt("test_prompt")
        assert get_result["name"] == "test_prompt"
        assert get_result["content"] == "This is a test prompt"
        assert get_result["type"] == "custom"
        assert "test" in get_result["tags"]
    
    def test_save_file_reference(self):
        """Test saving file references"""
        # Create a test file
        test_file = Path("test.md")
        test_file.write_text("# Test content")
        
        # Save reference
        save_result = save_prompt(
            name="file_ref",
            file_path=str(test_file)
        )
        
        assert save_result["saved"] is True
        assert save_result["type"] == "file_reference"
        
        # Load it
        get_result = get_prompt("file_ref")
        assert get_result["content"] == "# Test content"
    
    def test_duplicate_name_error(self):
        """Test that duplicate names are rejected"""
        save_prompt(name="duplicate", content="First")
        
        result = save_prompt(name="duplicate", content="Second")
        assert "error" in result
        assert "already exists" in result["error"]


class TestPromptLoading:
    """Test batch loading functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        init_db()
        
        # Create some test prompts
        save_prompt(name="prompt1", content="Content 1")
        save_prompt(name="prompt2", content="Content 2")
        
        # Create test file
        Path("external.md").write_text("External content")
    
    def test_load_multiple_prompts(self):
        """Test loading multiple prompts"""
        result = load_prompts([
            "prompt1",
            "custom:prompt2",
            "file:external.md"
        ])
        
        assert result["total_prompts"] == 3
        assert len(result["loaded"]) == 3
        assert len(result["errors"]) == 0
        
        # Check each loaded prompt
        refs = [p["ref"] for p in result["loaded"]]
        assert "prompt1" in refs
        assert "custom:prompt2" in refs
        assert "file:external.md" in refs
    
    def test_load_with_errors(self):
        """Test loading with some failures"""
        result = load_prompts([
            "prompt1",
            "nonexistent",
            "file:missing.md"
        ])
        
        assert result["total_prompts"] == 1
        assert len(result["errors"]) == 2


class TestPromptComposition:
    """Test prompt composition features"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        init_db()
        
        # Create test prompts
        save_prompt(name="base", content="Base content\n\nShared paragraph")
        save_prompt(name="extension", content="Extension content\n\nShared paragraph")
    
    def test_compose_basic(self):
        """Test basic composition"""
        result = compose_prompts(["base", "extension"], deduplicate=False)
        
        assert "content" in result
        assert "Base content" in result["content"]
        assert "Extension content" in result["content"]
        assert result["content"].count("Shared paragraph") == 2
    
    def test_compose_with_dedup(self):
        """Test composition with deduplication"""
        result = compose_prompts(["base", "extension"], deduplicate=True)
        
        assert "content" in result
        assert result["content"].count("Shared paragraph") == 1
        assert len(result["metadata"]["removed_duplicates"]) > 0
    
    def test_compose_with_token_limit(self):
        """Test composition with token limit"""
        # Create a large prompt
        save_prompt(name="large", content="x" * 10000)
        
        result = compose_prompts(
            ["base", "extension", "large"],
            max_tokens=100  # Very small limit
        )
        
        assert result["tokens"] <= 100
        assert "trimmed" in result["metadata"]


class TestUtilities:
    """Test utility functions"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        init_db()
    
    def test_estimate_tokens_content(self):
        """Test token estimation for content"""
        result = estimate_context(content="Hello world!")
        
        assert "tokens" in result
        assert result["tokens"] > 0
        assert "estimated_context_percentage" in result
    
    def test_list_available(self):
        """Test listing available prompts"""
        # Save some custom prompts
        save_prompt(name="custom1", content="Test", tags=["tag1"])
        save_prompt(name="custom2", content="Test", tags=["tag2"])
        
        result = list_available()
        
        assert "defaults" in result
        assert "custom" in result
        assert len(result["custom"]) == 2
        
        # Test filtering by tags
        filtered = list_available(tags=["tag1"])
        assert len(filtered["custom"]) == 1
        assert filtered["custom"][0]["name"] == "custom1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])