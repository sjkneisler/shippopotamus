# 🚢🦛 **Shippopotamus** (or **Shippo** or **🚢🦛** for short)

**Structured PromptOps:** lean prompt management, minimal tooling, and clear workflows for sustainable agentic coding.

---

## Why Shippo?

* **PromptOps mindset** – treat prompts, docs, and tools as first-class operational assets.  
* **Tiny always-loaded index** – one file (`prompts/00_INDEX.md`) keeps context costs low.  
* **Opinionated axioms** – shared, project-agnostic principles for consistency.  
* **Day-0 tool set** – three lightweight MCP tools (prune, progress queue, dedup + safe-write) that solve real pain without over-engineering.

---

## Quick start

1. `git clone <this-repo>`  
2. Copy **`prompts/`** and **`tools/`** into any codebase you want the agent to work on.  
3. Point your coding LLM at `prompts/00_INDEX.md`.  
4. Watch it echo the emojis, call only needed tools, and ship clean code.

---

## Directory guide

| Path | Purpose |
|------|---------|
| `prompts/00_INDEX.md` | Always-loaded index, tool list, emoji-echo rule. |
| `prompts/axioms/` | Core, Quality, and Pattern docs (global principles). |
| `prompts/meta/` | Design rationale, backlog, implementation plan. |
| `tools/` | Day-0 MCP wrappers (`prune_memory`, `progress_queue`, `tool_dedup_guard`). |

---

## Roadmap highlights

* RAG-on-tools registry for smart tool retrieval  
* Phase-switch mini-tool (PLAN / IMPLEMENT / QA)  
* Split-brain executor for low-latency local calls  
* Weekly CI prune & archive job

(See `prompts/meta/backlog.md` for details.)

---

## Contributing

Pull requests and prompt ideas welcome—keep them lean, documented, and in line with Shippo’s axioms. Open an issue if you’re unsure.

---

## License

MIT ― see `LICENSE`.
