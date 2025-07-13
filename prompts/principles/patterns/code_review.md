<!-- id:code_review emoji:👀 -->

# Code Review Checklist

Systematic approach to reviewing code for quality, security, and maintainability.

## Functionality

- [ ] **Correctness**: Does the code do what it's supposed to do?
- [ ] **Edge cases**: Are boundary conditions handled?
- [ ] **Error handling**: Are errors caught and handled appropriately?
- [ ] **Performance**: Are there any obvious performance issues?

## Code Quality

- [ ] **Readability**: Is the code easy to understand?
- [ ] **Naming**: Are variables, functions, and classes named clearly?
- [ ] **Comments**: Are complex sections documented?
- [ ] **DRY**: Is there unnecessary duplication?
- [ ] **Single Responsibility**: Does each function/class do one thing well?

## Security

- [ ] **Input validation**: Are all inputs validated?
- [ ] **Authentication**: Are permissions checked appropriately?
- [ ] **Sensitive data**: Are secrets/credentials handled safely?
- [ ] **SQL injection**: Are database queries parameterized?
- [ ] **XSS**: Is user input escaped when displayed?

## Architecture

- [ ] **Design patterns**: Are appropriate patterns used?
- [ ] **Dependencies**: Are new dependencies justified?
- [ ] **Modularity**: Is the code properly organized?
- [ ] **Coupling**: Are components loosely coupled?
- [ ] **Future-proof**: Is the design extensible?

## Testing

- [ ] **Test coverage**: Are critical paths tested?
- [ ] **Test quality**: Do tests actually verify behavior?
- [ ] **Edge cases**: Are boundary conditions tested?
- [ ] **Mocking**: Are external dependencies properly mocked?

## Documentation

- [ ] **API docs**: Are public interfaces documented?
- [ ] **README**: Is setup/usage information current?
- [ ] **Changelog**: Are changes noted?
- [ ] **Examples**: Are usage examples provided?

## Best Practices

### When Reviewing

✅ **Be constructive**: Suggest improvements, don't just criticize
✅ **Ask questions**: "What do you think about..." encourages discussion
✅ **Praise good code**: Acknowledge well-written sections
✅ **Provide examples**: Show, don't just tell

### Red Flags 🚩

- Very long functions (>50 lines)
- Deeply nested code (>3 levels)
- Magic numbers without explanation
- Empty catch blocks
- Commented-out code
- TODO comments in production code
- Inconsistent formatting

## Review Priority

1. **Security issues** - Must fix immediately
2. **Bugs** - Fix before merge
3. **Performance** - Fix if significant
4. **Code style** - Fix if time permits
5. **Nitpicks** - Optional improvements

Remember: The goal is to improve code quality while maintaining team morale!