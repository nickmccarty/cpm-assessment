# Testing Framework for Lab 1.1

## Overview

This testing framework validates your refactored application to ensure it maintains functionality while improving code organization.

## Test Structure

```
tests/
├── README.md                # This file
├── conftest.py             # pytest configuration and fixtures
├── test_config.py          # Configuration module tests
├── test_ai_client.py       # AI client tests with mocks
├── test_conversation.py    # Conversation manager tests
└── test_integration.py     # Full application integration tests
```

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-mock python-dotenv
```

### Basic Test Execution
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=refactored_app
```

## Test Categories

### 1. Unit Tests (`test_config.py`, `test_ai_client.py`, `test_conversation.py`)
Test individual modules in isolation:
- Configuration loading and validation
- AI client error handling (with mocked API calls)
- Conversation manager functionality

### 2. Integration Tests (`test_integration.py`)
Test how modules work together:
- Full application workflow
- Error propagation between modules
- End-to-end functionality validation

## Key Testing Concepts

### Mocking API Calls
Since we're testing with external APIs, we use mocks to simulate:
- Successful API responses
- Rate limiting errors
- Network connection failures
- Invalid API key scenarios

### Fixtures
Common test data and setup code is shared through fixtures:
- Mock conversation data
- Test configuration settings
- Temporary file handling

### Environment Isolation
Tests use temporary environments to avoid:
- Interfering with your actual API keys
- Creating permanent test files
- Affecting your development environment

## Success Criteria

Your refactored application should pass all tests, demonstrating:

✅ **Configuration Management**
- Loads environment variables correctly
- Validates required settings
- Handles missing configuration gracefully

✅ **AI Client Robustness**
- Handles successful API responses
- Manages rate limiting and errors
- Provides user-friendly error messages

✅ **Conversation Management**
- Tracks conversation history accurately
- Trims history when reaching limits
- Saves and loads session data

✅ **Integration Stability**
- All modules work together correctly
- Error handling propagates appropriately
- Application maintains state consistency

## Test-Driven Development Tips

1. **Run tests frequently** as you refactor Sarah's script
2. **Fix failing tests immediately** before adding new features
3. **Add new tests** when you discover edge cases
4. **Use test output** to understand what your code is doing wrong

## Common Test Failures and Solutions

### `ImportError: No module named 'config'`
- Ensure you have `__init__.py` files in each package directory
- Check your Python path and package structure

### `ValueError: OPENAI_API_KEY environment variable is required`
- Tests should use mocked configuration, not real API keys
- Check that test fixtures override environment variables

### `AssertionError: Expected X but got Y`
- Review the specific test that failed
- Compare expected behavior with your implementation
- Use print statements or debugger to understand the difference

## Next Steps

After all tests pass:
1. Review test coverage to ensure you're testing all important code paths
2. Add additional tests for edge cases you discovered
3. Use the testing patterns in future lab assignments
4. Consider this testing approach for your portfolio projects

The testing framework ensures your refactoring maintains Sarah's original functionality while dramatically improving code quality and maintainability.