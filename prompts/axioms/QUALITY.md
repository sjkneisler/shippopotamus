<!-- id:quality emoji:⚖️ -->

## Testing & Validation
*GOOD* ✔  Write or update tests, run them, then commit.  
*BAD* ✖  Add code paths without any automated check.

## Cleanup
*GOOD* ✔  Call `<TOOL_PRUNE>` and delete `tmp/` artefacts in the final step.  
*BAD* ✖  Leave temp files or obsolete tests in place.

## Safe‑write rule
> **Never overwrite a file you haven’t read in the same turn.**  
Guard is enforced by `<TOOL_DEDUP>`; bypass requires a human TODO.
