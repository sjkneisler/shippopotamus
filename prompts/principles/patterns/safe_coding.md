<!-- id:safe_coding emoji:🛡️ type:principle -->

# Safe Coding Practices

When writing or modifying code, always follow these safety principles:

## Core Safety Rules

1. **Read Before Write**: Never use write_file without read_file in the same turn
2. **Verify Paths**: Always verify parent directories exist before creating new files
3. **Check Dependencies**: Ensure all imports and dependencies are available
4. **Test Changes**: Run tests after modifications to ensure nothing breaks

## Security Principles

- Never expose secrets, API keys, or credentials in code or logs
- Always validate user input before processing
- Use secure defaults for all configurations
- Follow the principle of least privilege

## Error Handling

- Always include proper error handling
- Provide meaningful error messages
- Log errors appropriately (without exposing sensitive data)
- Fail gracefully with helpful recovery suggestions

## Code Quality

- Write clear, self-documenting code
- Follow existing code conventions in the project
- Add appropriate comments for complex logic
- Keep functions focused and single-purpose