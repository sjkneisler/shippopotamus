# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

🚢🦛 **Shippopotamus** is a prompt management platform that helps AI applications manage, compose, and optimize their prompts. It provides MCP tools that external teams can use to professionalize their prompt engineering workflows.

## Key Development Principles

### Principles vs Workflows
- **Principles**: Define HOW to work (axioms, patterns, methodologies)
- **Workflows**: Define WHAT to do (specific task prompts)
- Bootstrap loads principles; workflows are loaded on-demand for tasks

### Ask → Plan → Act Methodology
Always clarify requirements before implementing. When working on this codebase:
1. Understand the existing prompt structure
2. Plan changes that align with the axioms
3. Implement with minimal tooling

### Echo-Emoji Contract
When loading any prompt file, **echo its emoji(s) in order** at the start of your reply. For example, if loading CORE.md (🧭) and QUALITY.md (⚖️), start with: `🧭⚖️`

### Context Economy
- Default load only `prompts/00_INDEX.md` (≤2KB)
- Load other files on-demand using `rg "id:" --files` to discover available prompts
- Each prompt file has header: `<!-- id:name emoji:symbol -->`

## Development Commands

### Python Environment (Planned)
```bash
# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Run tests
pytest

# Specific test file
pytest tests/test_tools.py
```

### Tool Development
Our MCP tools use FastMCP for registration. Each tool provides:
1. Prompt loading and saving capabilities
2. Intelligent composition and deduplication
3. Token estimation and context budgeting
4. Support for both curated defaults and custom prompts

## Architecture

### Directory Structure
- `prompts/` - Prompt management system
  - `00_INDEX.md` - Always-loaded index (must stay ≤2KB)
  - `principles/` - How to work (methodologies and patterns)
    - `axioms/` - Core principles (CORE.md, QUALITY.md, PATTERNS.md)
    - `patterns/` - Best practices (safe_coding.md, documentation.md, etc.)
  - `workflows/` - What to do (task-oriented prompts)
    - `documentation/` - Documentation workflows
    - `testing/` - Testing workflows
    - `refactoring/` - Refactoring workflows
  - `meta/` - Design docs and backlog
- `tools/` - MCP tool implementations
  - `prompt_registry.py` - Core registry for default and custom prompts
  - `prompt_composer.py` - Intelligent prompt composition tools

### Database Files
- `tmp/prompt_registry.db` - SQLite database for custom prompts and usage tracking

## Critical Rules

1. **Consumer Focus**: All tools must provide value to external users, not just internal use
2. **Dual Registry**: Support both our curated prompts and user's custom prompts
3. **File References**: Allow users to reference files in their own repositories
4. **Context Awareness**: Help users manage token budgets effectively

## Testing Approach

Use pytest for unit tests focusing on:
- Registry functionality (save, load, search)
- Prompt composition and deduplication
- File reference resolution
- Token estimation accuracy
- Error handling for missing prompts

## Future Features (Backlog)

- Prompt versioning and history
- Team collaboration features
- Prompt performance analytics
- Import/export capabilities
- Integration with more LLM platforms