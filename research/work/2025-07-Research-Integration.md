<!--
title: Integrate 2025-07 Agentic Best Practices Research
description: Plan for consuming latest research, updating prompts, and deciding what to action.
status: in-progress                           # in-progress | review | done
checklist:
  - Long-form research file placed in research/ and committed
  - Prompt team (or Shippo) has read the doc and extracted actionable items
  - Actionable items added to prompts/meta/backlog.md
  - Non-actionable insights noted in design-rationale.md
checklist_complete: false
remove_when: checklist_complete==true
-->

# Plan: Integrate Latest Agentic / PromptOps Research

## Objective
Ingest the long-form document **“2025-07-Agentic-Best-Practices.md”**, distil actionable improvements for Shippo, and record them in the appropriate permanent docs.

## Steps
1. **Read & Summarise**  
   - Human (or LLM) reads the research file and produces a concise summary of key takeaways.
2. **Identify Actionables**  
   - Anything that should change prompts, tools, or processes goes to `prompts/meta/backlog.md`.
   - High-confidence axioms may be promoted into `prompts/axioms/PATTERNS.md`.
3. **Record Non-actionable Insights**  
   - Broad philosophy or context stays in `prompts/meta/design-rationale.md` under a “Research Insights” header.
4. **Mark Checklist Complete**  
   - Once all bullets above are ticked, flip `checklist_complete: true` so the prune tool can delete this file.

## Notes
- **Do NOT** copy the full research doc into prompt context; reference it selectively.  
- Future deep-research docs should follow the same lifecycle:  
  1) drop in `research/` → 2) create a `work/` integration plan.