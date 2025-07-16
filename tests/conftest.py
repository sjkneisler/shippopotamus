"""
Pytest configuration and shared fixtures for Shippopotamus tests
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for tests"""
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    
    yield temp_dir
    
    # Cleanup
    os.chdir(original_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def initialized_db(temp_workspace):
    """Create an initialized database in temp workspace"""
    from tools.prompt_registry import init_db
    init_db()
    return temp_workspace


@pytest.fixture
def sample_prompts(initialized_db):
    """Create sample prompts for testing"""
    from tools.prompt_registry import save_prompt
    
    prompts = {
        "test_principle": {
            "content": "principle: This is a test principle for unit testing",
            "tags": ["principle", "test"]
        },
        "test_workflow": {
            "content": "workflow: This is a test workflow with steps",
            "tags": ["workflow", "test"]
        },
        "test_pattern": {
            "content": "pattern: A reusable pattern for testing",
            "tags": ["pattern", "test"]
        }
    }
    
    for name, data in prompts.items():
        save_prompt(name=name, **data)
    
    return prompts


@pytest.fixture
def mock_embeddings_model(monkeypatch):
    """Mock the embeddings model to avoid dependencies"""
    class MockModel:
        def encode(self, text, convert_to_numpy=True):
            # Return consistent fake embeddings
            import hashlib
            import numpy as np
            
            # Generate deterministic embedding from text
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            
            # Convert to floats between -1 and 1
            embedding = []
            for i in range(0, len(hash_bytes), 4):
                chunk = hash_bytes[i:i+4]
                value = int.from_bytes(chunk, 'big') / (2**32)
                embedding.append(value * 2 - 1)
            
            # Pad to correct dimension (384)
            while len(embedding) < 384:
                embedding.append(0.0)
            
            return np.array(embedding[:384])
    
    # Monkey patch the model loading
    def mock_init_model(self):
        self.model = MockModel()
    
    from tools import embeddings_manager
    monkeypatch.setattr(embeddings_manager.EmbeddingsManager, '_init_model', mock_init_model)
    
    return MockModel()


@pytest.fixture
def prompt_files(temp_workspace):
    """Create temporary prompt files for testing"""
    files = {}
    
    # Create test prompt files
    prompts_dir = Path(temp_workspace) / "test_prompts"
    prompts_dir.mkdir()
    
    test_files = {
        "axiom.md": "<!-- id:test_axiom emoji:🧭 -->\n# Test Axiom\nCore principle content",
        "pattern.md": "<!-- id:test_pattern emoji:🔧 -->\n# Test Pattern\nPattern content",
        "workflow.md": "<!-- id:test_workflow emoji:📋 -->\n# Test Workflow\nWorkflow steps"
    }
    
    for filename, content in test_files.items():
        file_path = prompts_dir / filename
        file_path.write_text(content)
        files[filename] = str(file_path)
    
    return files


@pytest.fixture
def mock_default_prompts(monkeypatch):
    """Mock the default prompts mapping"""
    mock_prompts = {
        "test_default_1": "prompts/test1.md",
        "test_default_2": "prompts/test2.md",
    }
    
    # Create the files
    for name, path in mock_prompts.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(f"# {name}\nDefault content for {name}")
    
    # Patch the default prompts dictionary
    import tools.prompt_registry
    monkeypatch.setattr(tools.prompt_registry, 'default_prompts', mock_prompts)
    
    return mock_prompts


# Markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests for individual functions")
    config.addinivalue_line("markers", "integration: Integration tests for tool interactions")
    config.addinivalue_line("markers", "mcp: Tests specific to MCP tool registration")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
    config.addinivalue_line("markers", "requires_model: Tests that require ML models")