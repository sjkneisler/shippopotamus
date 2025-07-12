<!-- id:index emoji:🗺️ -->
## Purpose  
Single, always‑loaded guide that tells an agent **where to look next** and how to prove what it read.

---

### How to discover more guidance  
*Run a recursive file search (e.g. `rg "id:" --files`) and load any file whose header matches the emoji(s) you need.*

---

### Echo‑emoji rule  
When you load a prompt‑ops file, **echo its emoji(s) in order** at the start of your reply.  
Example reply prefix: `🗺️🧭⚖️`.

---

### Prompt Management Tools
| Function | Description |
|----------|-------------|
| `get_prompt(name)` | Load from registry or library |
| `save_prompt(...)` | Save custom prompts |
| `load_prompts([...])` | Batch load multiple sources |
| `compose_prompts(...)` | Combine with deduplication |
| `list_available()` | Discover all prompts |
| `estimate_context(...)` | Plan token usage |

(*File size target ≤ 2 KB—keep brief!*)