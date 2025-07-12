<!-- id:documentation emoji:📝 -->

# Documentation Best Practices

Clear documentation is as important as clean code. Follow these principles.

## Documentation Levels

### 1. Code Comments
```python
# WHY, not WHAT
# Bad: Increment x by 1
x += 1

# Good: Compensate for zero-based index when displaying to user
x += 1
```

### 2. Function/Method Documentation
```python
def calculate_discount(price: float, user: User) -> float:
    """
    Calculate personalized discount based on user loyalty status.
    
    Args:
        price: Original price in dollars
        user: User object with loyalty information
        
    Returns:
        Discounted price in dollars
        
    Raises:
        ValueError: If price is negative
        
    Example:
        >>> calculate_discount(100.0, premium_user)
        85.0
    """
```

### 3. Module/Class Documentation
```python
"""
Payment Processing Module

This module handles all payment-related operations including:
- Credit card processing
- Refund management
- Transaction logging

Usage:
    from payments import process_payment
    result = process_payment(card, amount)
"""
```

### 4. API Documentation
```yaml
POST /api/v1/users
Description: Create a new user account
Auth: Required (Bearer token)

Request Body:
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "standard"
}

Response 201:
{
  "id": "usr_123",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}

Response 400:
{
  "error": "Invalid email format"
}
```

## README Structure

```markdown
# Project Name

Brief description of what this project does and why it exists.

## Features

- Key feature 1
- Key feature 2
- Key feature 3

## Installation

\`\`\`bash
pip install your-package
\`\`\`

## Quick Start

\`\`\`python
from your_package import main_function
result = main_function()
\`\`\`

## Documentation

- [API Reference](docs/api.md)
- [User Guide](docs/guide.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT - see LICENSE file
```

## Writing Style Guidelines

### Be Clear and Concise
- Use simple language
- Avoid jargon without explanation
- Get to the point quickly
- Use examples liberally

### Structure for Scannability
- Use headers and subheaders
- Keep paragraphs short
- Use bullet points
- Include code examples

### Keep It Current
- Update docs with code changes
- Remove outdated information
- Version your documentation
- Date significant updates

## Documentation Anti-patterns

❌ **Auto-generated noise**: Don't document getters/setters
❌ **Outdated examples**: Test your code samples
❌ **Wall of text**: Break up long sections
❌ **Missing context**: Explain the "why"
❌ **Assumption overload**: Define your terms

## Tools and Formats

- **Markdown**: For README, guides
- **Docstrings**: For code documentation
- **OpenAPI/Swagger**: For REST APIs
- **JSDoc/TypeDoc**: For JavaScript/TypeScript
- **Sphinx/MkDocs**: For documentation sites

## Remember

> "Documentation is a love letter that you write to your future self." - Damian Conway

Good documentation:
- Reduces support burden
- Accelerates onboarding
- Prevents misuse
- Builds trust