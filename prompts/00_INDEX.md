<!-- id:index emoji:🗺️ -->
## Purpose  
Single, always‑loaded guide that tells an agent **where to look next** and how to prove what it read.

---

### How to discover more guidance  
*Run a recursive file search (e.g. `rg "id:" --files`) and load any file whose header matches the emoji(s) you need.*

---

### Echo‑emoji rule  
When you load a prompt‑ops file, **echo its emoji(s) in order** at the start of your reply.  
Example reply prefix: `🗺️🧭⚖️`.

---

### Day‑0 tools  
| Tag | Function | Path |
|-----|----------|------|
| `<TOOL_PRUNE>` | Prune oldest lines in `memory-bank/progress.md`. | `tools/prune_memory.py` |
| `<TOOL_QUEUE>` | FIFO + sticky progress log. | `tools/progress_queue.py` |
| `<TOOL_DEDUP>` | Block duplicate tool calls & unsafe writes. | `tools/tool_dedup_guard.py` |

(*File size target ≤ 2 KB—keep brief!*)

