# 🚢🦛 Shippo — Research Folder

This folder holds **long-form reference material**: white-paper digests, deep-dive experiments, competitive analyses, etc.

Unlike implementation plans (which are short-lived), research docs:

* Are **informational** – not actionable tasks.  
* May remain valuable for months.  
* Should **NOT** be loaded into every LLM context; they are “pull, not push.”

## Structure

```

research/
├─ README.md                # this file
├─ 2025-07-Agentic-Best-Practices.md   # example long-form research
└─ work/                    # scratch plans about research usage
└─ 2025-07-Research-Integration.md

```

### File naming

`YYYY-MM-Slug.md` keeps research chronologically ordered and easy to reference.

### Lifespan & pruning

* **Reference docs** (top-level `.md` files) live until manually archived or superseded.  
* **Plans / RFCs** go in `research/work/` and include a front-matter header with `status`, `remove_when`, and (optionally) a `checklist`.  
  Shippo’s prune tool deletes them automatically when their `remove_when` evaluates to **true**.

### Quick-link pattern

When you create a new research doc, add a one-line description (e.g. in backlog or design-rationale) so others know it exists:

```

* 2025-07-Agentic-Best-Practices → deep survey of multi-agent & PromptOps techniques

```
```

---

### 2  `research/work/2025-07-Research-Integration.md`
