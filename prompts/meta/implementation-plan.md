Below is a **step‑by‑step, agent‑ready implementation plan** that stitches together every decision we’ve reached.
It is deliberately prescriptive (so an LLM agent can follow it) but *does not* include full code—only critical paths, interfaces, and acceptance checks.

---

## 0  Guiding constraints (baked into every step)

* **Ask → Plan → Act** loop; agent must confirm assumptions before writing code.
* Keep the *always‑loaded* file ≤ 2 KB; other files load on demand.
* Day‑0 scope = prompts + 3 tools (prune, progress, dedup + safe‑write).
* **Echo‑emoji / tool‑tag contract** is mandatory for validation.
* Hard‑code temp artefacts under `tmp/`.
* No cost telemetry, CI, or split‑brain until backlog is tackled.

---

## 1  Repo bootstrap  (≈ 15 min)

1. `mkdir PLACEHOLDER-promptops && cd $_`
2. `git init`
3. Create top‑level `.gitignore` with at least:

   ```
   tmp/
   *.db
   __pycache__/
   ```
4. Add MIT (or preferred) license.

**Checkpoint 1:** repo root contains only `.gitignore` and `LICENSE`.

---

## 2  Prompt layer skeleton  (≈ 25 min)

### 2.1 Directory tree

```
prompts/
├─ README.md
├─ 00_INDEX.md          (≤2 KB, emoji 🗺️)
├─ axioms/
│   ├─ CORE.md          (emoji 🧭)
│   ├─ QUALITY.md       (emoji ⚖️)
│   └─ PATTERNS.md      (emoji 🪢)
└─ meta/
    ├─ design‑rationale.md
    └─ backlog.md
```

### 2.2 Fill minimal content

* **README.md** – human‑oriented overview; note *PlaceHolder* name.
* **00\_INDEX.md**

  * Header: `<!-- id:index emoji:🗺️ -->`
  * Sections: *Purpose, How agents discover more docs (regex example), Echo‑emoji rule, Day‑0 tools list*.
* **CORE.md** – 10 axioms table (see previous message).
* **QUALITY.md** – headers “Testing”, “Cleanup”, “Safe‑write rule” with BAD/GOOD bullet pairs.
* **PATTERNS.md** – one‑sentence summaries of meta‑meta patterns.
* **design‑rationale.md** – explain constraints & future layers (CI, RAG‑tools).
* **backlog.md** – list backlog items (RAG‑registry, phase switch tool, split‑brain, cost ledger, CI prune job).

**Checkpoint 2:** total size of `00_INDEX.md` < 2 KB; each axiom file header includes `id:` and `emoji:` comments.

---

## 3  Tool layer (Day‑0)  (≈ 60 min)

### 3.1 Create structure

```
tools/
├─ __init__.py
├─ prune_memory.py
├─ progress_queue.py
└─ tool_dedup_guard.py
```

Each file begins with:

```python
"""
id: prune_memory
tag: TOOL_PRUNE
"""
```

### 3.2 Interface specs

| File                  | Public functions                                                                   | Critical logic to implement                                                                                                                                                                        |
| --------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prune_memory.py`     | `def prune(k: int = 20, strategy: str = "embeddings") -> str`                      | - Open `memory-bank/progress.md`.<br>- Delete oldest lines until ≤ k remain.<br>- Return summary string.                                                                                           |
| `progress_queue.py`   | `put(event: str, importance: int = 0) -> None`  <br>`get(k: int = 5) -> list[str]` | - SQLite DB under `tmp/progress.db`.<br>- `importance>0` rows never auto‑purged.<br>- `get` pops newest first.                                                                                     |
| `tool_dedup_guard.py` | `check(tool: str, args: dict) -> bool`                                             | - Hash `(tool, json.dumps(args, sort_keys=True))`.<br>- Store in `tmp/dedup.db`.<br>- Return **False** if hash exists.<br>- Extra rule: reject `write_file` if `read_file(path)` not in same turn. |

### 3.3 Register with FastMCP

Edit `tools/__init__.py`:

```python
from fastmcp import registry
import tools.prune_memory as pm
import tools.progress_queue as pq
import tools.tool_dedup_guard as dg

registry.register("prune_memory", pm.prune)
registry.register("progress_put", pq.put)
registry.register("progress_get", pq.get)
registry.register("tool_dedup_guard", dg.check)
```

### 3.4 Unit smoke tests

Create `tests/test_tools.py` with one call per function asserting type/ basic behaviour; run `pytest`.

**Checkpoint 3:** `pytest` passes; DB files appear in `tmp/` after test run.

---

## 4  Documentation updates  (≈ 10 min)

* Append Day‑0 tool tags to `00_INDEX.md` under **Available tools**.
* In `QUALITY.md`, add bullet *“Always call `tool_dedup_guard` before any tool invocation.”*

**Checkpoint 4:** `00_INDEX.md` lists `TOOL_PRUNE`, `TOOL_QUEUE`, `TOOL_DEDUP`.

---

## 5  Validation / dog‑food session  (1 working session)

1. Open a real project repo in Cursor (or VS Code + Claude Code).
2. Copy `prompts/` and `tools/` directories into project root.
3. Instruct agent: *“Refactor X; follow PLACEHOLDER prompt‑ops guidance.”*
4. Verify:

   * Reply begins with `🗺️🧭` (and others if loaded).
   * Agent calls at most one Day‑0 tool; echoes `<TOOL_…>` tag.
   * No `write_file` occurs without a preceding `read_file`.

Log any friction into `meta/backlog.md`.

---

## 6  Post‑Day‑0 backlog (no work now)

* **RAG‑on‑tools registry + embedding lookup**
* **Phase‑switch mini‑tool** (`set_phase`)
* **Split‑brain executor (local small model)**
* **Cost telemetry ledger in `tmp/tool_stats.json`**
* **Weekly CI job** – prune stale tools & memory, archive old progress
* **Mermaid architecture diagram in `meta/`**

---

## 7  Human checkpoints

| Milestone            | Human action                                              |
| -------------------- | --------------------------------------------------------- |
| After Checkpoint 2   | Skim `00_INDEX.md`; ensure wording is project‑agnostic.   |
| After Checkpoint 3   | Review SQLite paths & verify no secrets written.          |
| Dog‑food session end | Decide whether pain justifies promoting any backlog item. |

---

### DONE

This plan is lean enough for an LLM agent to execute but leaves heavy lifting (complex MCPs, CI, RAG registry) for later, exactly in line with our “best part is no part” maxim.
