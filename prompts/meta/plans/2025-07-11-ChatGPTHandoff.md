<!--
title: Shippo Loader MCP
description: One-call tool that bundles prompts, echoes 🚢🦛, and accepts parent-repo docs.
status: in-progress                     # in-progress | review | done
checklist:
  - prompt_loader.py exists and passes smoke tests
  - 00_INDEX header emoji updated to 🚢🦛
  - prompt_rules.yaml created with 'always' rules
  - prune tool extended for remove_when logic
  - sample repo dog-food run shows first reply prefix 🚢🦛🧭⚖️
  - lessons summarised into design-rationale.md
checklist_complete: false
remove_when: checklist_complete==true
-->

# 🚢🦛 Shippo PromptOps Bootstrap & Self-Loader Plan

This temporary plan captures **everything discussed after naming “Shippopotamus / Shippo.”**  
When every checklist item in the header is true, set `checklist_complete: true` and let the prune tool delete this file.

---

## 0 Overview

* Convert Shippo into a **PromptOps MCP** that feeds prompts to agents via one tool call.  
* Swap index emoji to 🚢🦛 so echo confirms loader success.  
* Provide parent-repo override (`extra_docs_dir`) while Shippo lives as a **git submodule**.  
* Mark all temporary docs (like this one) with a lifespan header so they self-prune.  
* Keep the Day-0 scope minimal: loader + three existing tools (prune, progress, dedup).

---

## 1 File/Folder Additions

| Path | Purpose |
|------|---------|
| `tools/prompt_loader.py` | MCP that selects & concatenates prompts. |
| `prompt_rules.yaml` | Declarative selection rules (Day-0: “always” only). |
| `prompts/meta/work/` | Ephemeral plans & RFCs (this file lives here). |

---

## 2 prompt_loader.py – Day-0 behaviour

```python
def load(task: str, extra_docs_dir: str | None = None) -> dict:
    """
    1. Always include files where rule["always"] == true.
    2. If extra_docs_dir given, append every .md file (non-recursive).
    3. Concatenate: INDEX -> axioms -> extra.
    4. Build echo string from header emojis (always starts with 🚢🦛).
    5. Return {"prompts": big_string, "echo": echo}
    """
````

*No embeddings, no conditionals yet.*

---

## 3 Lifespan Header Conventions

```md
<!--
title: One-line descriptor
status: in-progress | review | done
remove_when: boolean rule
checklist:   # optional explicit list
  - ...
checklist_complete: false
-->
```

*Prune tool*: delete file if `eval(remove_when)` is `True`.
*Checklist*: helps LLM verify completeness before deletion.

---

## 4 Tasks

| # | Task                                                                              | Outcome                                                                                                                                                |
| - | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | Implement `tools/prompt_loader.py` (spec §2)                                      | One tool call returns all prompts.                                                                                                                     |
| 2 | Add `prompt_rules.yaml` with:                                                     | <br>`- path: prompts/00_INDEX.md, always: true`<br>`- path: prompts/axioms/CORE.md, always: true`<br>`- path: prompts/axioms/QUALITY.md, always: true` |
| 3 | Update **🚢🦛** emoji in `prompts/00_INDEX.md`.                                   | Echo starts with ship-hippo tag.                                                                                                                       |
| 4 | Extend `prune_memory.py` to evaluate `remove_when`.                               | Temp docs self-delete.                                                                                                                                 |
| 5 | Dog-food in sample repo via Cursor + Claude Code.                                 | First reply prefix `🚢🦛🧭⚖️`; tool calls succeed.                                                                                                     |
| 6 | Mark checklist\_complete → true and summarise lessons into `design-rationale.md`. | File eligible for pruning.                                                                                                                             |

---

## 5 Parent-Repo Hand-Shake

Parent repo usage:

```bash
git submodule add https://github.com/you/shippopotamus shippo
```

Agent call example:

```json
{
  "name": "prompt_loader.load",
  "arguments": {
    "task": "Refactor React component for TypeScript",
    "extra_docs_dir": "shippo_local"
  }
}
```

---

## 6 Future (Backlog)

* Vector-similarity conditional rules.
* Phase-switch tool (`set_phase`).
* Tool registry audit (`check_tools`).
* Split-brain executor.
* Weekly CI job: prune + archive.
* Cost ledger JSON.

---

*(Remember to tick checklist items and set `checklist_complete: true` when done.)*


### Addendum – Why include a **description** field in the front-matter?

A short, human-readable description:

1. **Clarifies intent** – Someone (or Shippo itself) can skim the plan without opening the whole file.
2. **Improves prune accuracy** – The prune tool can surface descriptions in logs or CI messages when deciding whether to delete or archive a finished plan.
3. **Prevents orphan work** – If a checklist is incomplete but status accidentally flips to `done`, the descriptive line often reveals the mismatch (“Wait, the loader isn’t smoke-tested yet!”).
