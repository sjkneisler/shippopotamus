**Shippopotamus** (or **Shippo** or **🚢🦛** for short) — portable prompt & tool scaffolding for agentic coding.

* **One tiny index** (`00_INDEX.md`) always in context.  
* **Hierarchical axioms** under `prompts/axioms/` (🧭 core, ⚖️ quality, 🪢 patterns).  
* **Day‑0 tools only:** prune memory, FIFO progress log, dedup + safe‑write guard.  
* Future niceties (RAG‑tool registry, cost telemetry, etc.) live in `prompts/meta/backlog.md`.

Copy `prompts/` and `tools/` into any repo, point your LLM agent at `00_INDEX.md`, and start shipping.
