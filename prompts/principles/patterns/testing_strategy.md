<!-- id:testing_strategy emoji:🧪 -->

# Test-Driven Development Strategy

Build reliable software by writing tests first and thinking about edge cases early.

## TDD Cycle

### 1. Red 🔴 - Write a Failing Test
```python
def test_user_can_login():
    user = User(email="test@example.com", password="secure123")
    token = login(user.email, user.password)
    assert token is not None
    assert len(token) > 20
```

### 2. Green 🟢 - Make It Pass (Minimal Code)
```python
def login(email: str, password: str) -> str:
    # Just enough to pass the test
    return "a" * 21
```

### 3. Refactor 🔧 - Improve the Code
```python
def login(email: str, password: str) -> str:
    user = User.find_by_email(email)
    if user and user.check_password(password):
        return generate_token(user)
    raise AuthenticationError("Invalid credentials")
```

## Test Categories

### Unit Tests
Test individual functions/methods in isolation:
```python
def test_calculate_tax():
    assert calculate_tax(100, 0.1) == 10
    assert calculate_tax(0, 0.1) == 0
    with pytest.raises(ValueError):
        calculate_tax(-100, 0.1)
```

### Integration Tests
Test how components work together:
```python
def test_order_processing():
    # Test database, payment gateway, and email service
    order = create_order(items=[...])
    process_payment(order)
    
    assert order.status == "completed"
    assert payment_gateway.was_charged(order.total)
    assert email_service.sent_confirmation(order.user.email)
```

### End-to-End Tests
Test complete user workflows:
```python
def test_user_purchase_flow():
    browser.get("/products")
    browser.click("Add to Cart")
    browser.click("Checkout")
    browser.fill("credit_card", "4242424242424242")
    browser.click("Purchase")
    
    assert "Thank you for your order" in browser.page_source
```

## What to Test

### Always Test
- **Happy path**: Normal, expected behavior
- **Edge cases**: Boundaries, empty inputs, nulls
- **Error cases**: Invalid inputs, exceptions
- **Business logic**: Core functionality
- **Security**: Authentication, authorization

### Consider Testing
- **Performance**: If critical to application
- **UI interactions**: For complex interfaces
- **External integrations**: With mocks/stubs

### Don't Test
- **Framework code**: Trust the framework
- **Simple getters/setters**: Unless they have logic
- **Third-party libraries**: They have their own tests

## Test Quality Indicators

### Good Tests Are:
- **Fast**: Run in milliseconds
- **Isolated**: Don't depend on other tests
- **Repeatable**: Same result every time
- **Self-validating**: Pass or fail clearly
- **Timely**: Written with or before code

### Test Smells 🚩
```python
# Bad: Testing implementation details
def test_uses_specific_algorithm():
    assert instance._internal_method_called == True

# Good: Testing behavior
def test_sorts_correctly():
    assert sort([3, 1, 2]) == [1, 2, 3]
```

## Mocking Best Practices

```python
# Mock external dependencies
@patch('requests.get')
def test_fetch_user_data(mock_get):
    mock_get.return_value.json.return_value = {"id": 1, "name": "Test"}
    
    user_data = fetch_user_data(1)
    
    assert user_data["name"] == "Test"
    mock_get.assert_called_once_with("https://api.example.com/users/1")
```

## Test Organization

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_validators.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
├── e2e/
│   └── test_user_flows.py
└── fixtures/
    └── test_data.py
```

## Coverage Guidelines

- **Aim for 80%+** code coverage
- **100% coverage** for critical paths
- **Don't chase 100%** everywhere - diminishing returns
- **Cover edge cases** not just lines

## Testing Pyramid

```
        /\
       /e2e\      <- Few, slow, expensive
      /------\
     /  integ \   <- Some, moderate
    /----------\
   /    unit    \ <- Many, fast, cheap
  /--------------\
```

## Remember

> "Legacy code is code without tests." - Michael Feathers

Testing isn't about catching bugs - it's about designing better software!