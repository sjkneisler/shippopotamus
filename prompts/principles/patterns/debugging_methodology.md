<!-- id:debugging_methodology emoji:🐛 -->

# Systematic Debugging Methodology

When encountering bugs or unexpected behavior, follow this systematic approach.

## 1. Reproduce First

Before attempting any fix:
- Confirm you can reproduce the issue consistently
- Document the exact steps to reproduce
- Note any intermittent behavior patterns
- Save error messages and stack traces

## 2. Isolate the Problem

Narrow down the scope:
- **Binary search**: Comment out half the code, test, repeat
- **Minimal reproduction**: Create the smallest code that exhibits the bug
- **Remove variables**: Eliminate external dependencies one by one
- **Check assumptions**: Verify your mental model matches reality

## 3. Gather Evidence

Collect data before hypothesizing:
```
- Add strategic logging/print statements
- Use debugger breakpoints
- Inspect variable states
- Check system resources (memory, CPU, disk)
- Review recent changes (git log/diff)
```

## 4. Form Hypotheses

Based on evidence, not guesses:
- List possible causes ranked by probability
- Consider edge cases and race conditions
- Think about what changed recently
- Question your assumptions

## 5. Test Systematically

One change at a time:
- Fix the most likely cause first
- Change only one thing per test
- Verify the fix actually works
- Ensure no regressions introduced

## 6. Document the Fix

For future reference:
- What was the root cause?
- Why did it happen?
- How was it fixed?
- How can it be prevented?

## Common Pitfalls to Avoid

❌ **Shotgun debugging**: Making random changes hoping something works
❌ **Assumption-driven**: "It must be X" without evidence
❌ **Fix symptoms**: Addressing effects not causes
❌ **Skip reproduction**: Fixing what you can't reproduce

## Remember

> "Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it." - Kernighan's Law