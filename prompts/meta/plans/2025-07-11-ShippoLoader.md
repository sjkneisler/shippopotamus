<!--
title: Shippo Loader & PromptOps Extensions
status: in-progress               # in-progress | review | done
remove_when: status=="done"       # Shippo prune tool/CI auto-deletes on completion
-->


# 🚢🦛 Shippo Loader & PromptOps Extensions

Single-tool prompt delivery, emoji swap, submodule hand-shake, and parent-repo overrides.

---

## 0 High-Level Goals

* **Replace multi-file reads** with one `prompt_loader.load` MCP call.  
* **Echo clarity** – loader guarantees first reply begins with `🚢🦛`.  
* **Parent repo co-existence** – allow an `extra_docs_dir` for project-local prompts.  
* **Stale-doc hygiene** – all temp plans live under `prompts/meta/work/` with auto-prune headers.

---

## 1 Task List (Day-0 scope)

| # | Task | Owner | Notes |
|---|------|-------|-------|
| 1 | Create `tools/prompt_loader.py` MCP (basic version). | dev | Args: `task`, `extra_docs_dir`. Returns concatenated prompts + `echo`. |
| 2 | Add `prompt_rules.yaml` with “always” rules for `00_INDEX`, CORE, QUALITY. | dev | Format: `{ path: prompts/axioms/CORE.md, always: true }` |
| 3 | Switch 00_INDEX header emoji from 🗺️ → 🚢🦛. | dev | Update examples & docs. |
| 4 | Update `tools/__init__.py` to register `prompt_loader.load`. | dev | |
| 5 | Amend `implementation-plan.md` (umbrella) to instruct agents to call `prompt_loader.load`. | dev | |
| 6 | Smoke test in sample repo via Cursor + Claude Code. | tester | Confirm first reply prefix = `🚢🦛🧭⚖️` etc. |
| 7 | If pass, flip this file’s `status` → `done`. | reviewer | Triggers prune. |

---

## 2 Prompt Loader – Minimal Spec

```python
def load(task: str, extra_docs_dir: str | None = None) -> dict:
    """
    Returns:
      {
        "prompts": "<big markdown string>",
        "echo": "🚢🦛..."       # emojis for index + loaded axioms
      }
    """
````

**Selection logic Day-0**

1. Always include files marked `always: true` in `prompt_rules.yaml`.
2. If `extra_docs_dir` given, read every `.md` in that dir (flat, no recurse).
3. Concatenate docs in this order: INDEX → axioms → extra.
4. Build `echo` from collected headers.

*No embedding or conditional rules yet.*

---

## 3 Prune Tool Extension

Update `prune_memory.py` to also scan `prompts/meta/work/` and delete any file whose front-matter evaluates `remove_when` to `True`.

Pseudocode:

```python
for file in Path("prompts/meta/work").glob("*.md"):
    fm = read_front_matter(file)
    if fm.get("remove_when") and eval(fm["remove_when"], {}, {"status": fm.get("status")}):
        file.unlink()
```

---

## 4 Submodule Hand-Shake

* Parent repo adds Shippo:
  `git submodule add https://github.com/... shippo`
* Parent can create `shippo_local/` and pass `extra_docs_dir="shippo_local"` to loader.
* Document this in root README of parent repo (not here).

---

## 5 Backlog (defer)

* Vector-similarity prompt retrieval.
* Phase-switch mini-tool.
* Tool-registry audit (`check_tools`).
* Split-brain executor (local small model).
* Cost ledger & weekly CI prune job.

---

**End of Plan – status: in-progress**
