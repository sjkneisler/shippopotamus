# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

🚢🦛 **Shippopotamus** is a PromptOps framework for structured prompt management and lean tooling for agentic coding. This is NOT a traditional programming project - it's a meta-framework for managing LLM interactions.

## Key Development Principles

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
Day-0 tools use FastMCP for registration. Each tool must:
1. Include header docstring with `id:` and `tag:`
2. Be registered in `tools/__init__.py`
3. Use SQLite databases in `tmp/` directory
4. Follow the dedup guard pattern before any tool invocation

## Architecture

### Directory Structure
- `prompts/` - Prompt management system
  - `00_INDEX.md` - Always-loaded index (must stay ≤2KB)
  - `axioms/` - Core principles (CORE.md, QUALITY.md, PATTERNS.md)
  - `meta/` - Design docs and backlog
- `tools/` - MCP tool implementations
  - `prune_memory.py` - Memory pruning
  - `progress_queue.py` - FIFO queue with importance levels
  - `tool_dedup_guard.py` - Prevent duplicate calls

### Database Files
- `tmp/progress.db` - Progress queue storage
- `tmp/dedup.db` - Tool deduplication hashes
- `memory-bank/progress.md` - Memory bank for pruning

## Critical Rules

1. **Tool Deduplication**: Always call `tool_dedup_guard` before any tool invocation
2. **Safe Write**: Never use `write_file` without `read_file` in the same turn
3. **File Size**: Keep `00_INDEX.md` under 2KB
4. **Temp Files**: All temporary artifacts go under `tmp/`

## Testing Approach

Use pytest for unit tests focusing on:
- Basic tool functionality (smoke tests)
- Database creation and operations
- Deduplication logic
- File size constraints

## Future Features (Backlog)

- RAG-on-tools registry for smart tool retrieval
- Phase-switch mini-tool (PLAN/IMPLEMENT/QA)
- Split-brain executor for low-latency calls
- Weekly CI prune & archive job
- Cost telemetry in `tmp/tool_stats.json`