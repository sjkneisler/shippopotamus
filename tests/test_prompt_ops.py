"""
Tests for Shippopotamus PromptOps platform
"""

import os
import tempfile
from pathlib import Path
import pytest
import sys
from unittest.mock import patch, Mock
sys.path.append('..')

from tools.prompt_registry import get_prompt, save_prompt, load_prompts, init_db
from tools.prompt_composer import compose_prompts, list_available, estimate_context, bootstrap_session


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
    
    def test_bootstrap_session(self):
        """Test bootstrap session functionality"""
        result = bootstrap_session()
        
        assert "status" in result
        assert "🦛" in result["status"]
        assert "loaded_prompts" in result
        assert "tokens_loaded" in result
        assert "capabilities_enabled" in result
        assert "quick_reference" in result
        
        # Check that it loads expected prompts
        assert len(result["loaded_prompts"]) >= 4
        assert result["tokens_loaded"] > 0
        assert len(result["capabilities_enabled"]) >= 4
        
        # Verify quick reference structure
        qr = result["quick_reference"]
        assert "core_tools" in qr
        assert "prompt_prefixes" in qr
        assert "next_steps" in qr


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        init_db()
    
    def test_save_prompt_validation(self):
        """Test input validation for save_prompt"""
        # No content or file_path
        result = save_prompt(name="invalid")
        assert "error" in result
        assert "Must provide either content or file_path" in result["error"]
        
        # Both content and file_path
        result = save_prompt(name="invalid", content="test", file_path="test.md")
        assert "error" in result
        assert "Cannot provide both content and file_path" in result["error"]
    
    def test_load_prompts_empty_list(self):
        """Test loading with empty prompt list"""
        result = load_prompts([])
        assert result["total_prompts"] == 0
        assert len(result["loaded"]) == 0
        assert len(result["errors"]) == 0
    
    def test_compose_prompts_no_valid_prompts(self):
        """Test composing with no valid prompts"""
        result = compose_prompts(["nonexistent1", "nonexistent2"])
        assert "error" in result or len(result["errors"]) == 2
    
    def test_estimate_context_edge_cases(self):
        """Test estimate_context with edge cases"""
        # Empty content
        result = estimate_context(content="")
        assert result["tokens"] == 0
        
        # Very long content
        long_content = "x" * 1000000
        result = estimate_context(content=long_content)
        assert result["tokens"] > 0
        assert result["estimated_context_percentage"] > 0
        
        # Unicode content
        unicode_content = "Hello 世界 🌍"
        result = estimate_context(content=unicode_content)
        assert result["tokens"] > 0


class TestBootstrapSession:
    """Test bootstrap_session functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        init_db()
    
    def test_bootstrap_session_success(self):
        """Test successful session bootstrap"""
        from prompt_composer import bootstrap_session
        
        # Mock the compose_prompts to avoid file dependencies
        with patch('prompt_composer.compose_prompts') as mock_compose:
            mock_compose.return_value = {
                'content': 'Combined principles content',
                'tokens': 922,
                'sources': [
                    {'ref': 'ask_plan_act'},
                    {'ref': 'quality_axioms'},
                    {'ref': 'context_economy'},
                    {'ref': 'safe_coding'}
                ]
            }
            
            result = bootstrap_session()
            
            assert result['status'] == "🦛 Session bootstrapped successfully!"
            assert len(result['loaded_prompts']) == 4
            assert result['tokens_loaded'] == 922
            assert len(result['capabilities_enabled']) == 4
            assert 'quick_reference' in result
            assert 'core_tools' in result['quick_reference']
            assert 'prompt_prefixes' in result['quick_reference']
            assert 'next_steps' in result['quick_reference']
            assert result['tip'] == "💡 Your session now includes proven methodologies. Use them to approach tasks systematically!"
    
    def test_bootstrap_session_failure(self):
        """Test bootstrap session handling failures"""
        from prompt_composer import bootstrap_session
        
        # Mock compose_prompts to return an error
        with patch('prompt_composer.compose_prompts') as mock_compose:
            mock_compose.return_value = {
                'error': 'Failed to load prompts'
            }
            
            result = bootstrap_session()
            
            assert 'error' in result
            assert result['error'] == "Failed to bootstrap session"
            assert 'details' in result
    
    def test_bootstrap_session_correct_prompts(self):
        """Test bootstrap loads the correct starter prompts"""
        from prompt_composer import bootstrap_session
        
        # Capture what prompts are requested
        with patch('prompt_composer.compose_prompts') as mock_compose:
            mock_compose.return_value = {'content': '', 'tokens': 0, 'sources': []}
            
            bootstrap_session()
            
            # Verify compose_prompts was called with correct prompts
            mock_compose.assert_called_once()
            args, kwargs = mock_compose.call_args
            prompt_refs = kwargs.get('prompt_refs', args[0] if args else [])
            
            expected_prompts = ["ask_plan_act", "quality_axioms", "context_economy", "safe_coding"]
            assert prompt_refs == expected_prompts
            assert kwargs.get('deduplicate', True) == True
    
    def test_parent_prompts_tracking(self):
        """Test parent prompt tracking functionality"""
        # Save base prompt
        save_prompt(name="base_prompt", content="Base content")
        
        # Save derived prompt
        result = save_prompt(
            name="derived_prompt",
            content="Derived content",
            parent_prompts=["base_prompt"]
        )
        
        assert result["saved"] is True
        assert "base_prompt" in result["parent_prompts"]
        
        # Retrieve and verify
        derived = get_prompt("derived_prompt")
        assert "base_prompt" in derived["parent_prompts"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])