"""
Pytest Configuration and Fixtures

This module provides shared pytest fixtures and configuration for testing
the AI Assistant application. It demonstrates professional testing setup
with proper isolation, mocking, and test data management.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, List
import sys

# Add solution_examples to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "solution_examples"))

# Import modules to test
from config.settings import AIConfig, AppConfig
from core.ai_client import AIClient, AIResponse, ErrorType
from conversation.manager import ConversationManager, ConversationExchange


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test files.
    Automatically cleaned up after test completion.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Setup mock environment variables for testing.
    """
    test_env = {
        'OPENAI_API_KEY': 'sk-test1234567890abcdef1234567890abcdef123456',
        'AI_MODEL': 'gpt-3.5-turbo',
        'MAX_TOKENS': '1000',
        'TEMPERATURE': '0.7',
        'CONVERSATION_FILE': 'test_conversations.json',
        'AUTO_SAVE': 'true',
        'LOG_LEVEL': 'DEBUG'
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    
    return test_env


@pytest.fixture
def ai_config(mock_env_vars):
    """
    Create a test AI configuration.
    """
    return AIConfig.from_environment()


@pytest.fixture
def app_config(mock_env_vars, temp_dir):
    """
    Create a test application configuration with temporary directory.
    """
    # Override data directory to use temp directory
    import os
    os.environ['DATA_DIRECTORY'] = str(temp_dir)
    
    return AppConfig.from_environment()


@pytest.fixture
def mock_openai_response():
    """
    Mock OpenAI API response object.
    """
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This is a test AI response."
    mock_response.usage.total_tokens = 25
    
    return mock_response


@pytest.fixture
def mock_ai_client(ai_config):
    """
    Create a mock AI client for testing without API calls.
    """
    client = Mock(spec=AIClient)
    client.config = ai_config
    client.call_count = 0
    
    # Mock successful response
    client.generate_response.return_value = AIResponse(
        content="This is a test AI response.",
        success=True,
        tokens_used=25,
        model_used="gpt-3.5-turbo",
        response_time=1.5,
        attempt_count=1
    )
    
    # Mock statistics
    client.get_statistics.return_value = {
        "total_requests": 5,
        "successful_requests": 4,
        "failed_requests": 1,
        "success_rate_percent": 80.0,
        "total_tokens_used": 125,
        "average_response_time_seconds": 1.2,
        "model_used": "gpt-3.5-turbo",
        "max_retries_configured": 3
    }
    
    client.health_check.return_value = True
    
    return client


@pytest.fixture
def sample_conversations():
    """
    Sample conversation data for testing.
    """
    return [
        {
            "timestamp": "2023-10-01T10:00:00",
            "user": "Hello, how are you?",
            "assistant": "I'm doing well, thank you! How can I help you today?",
            "tokens_used": 20,
            "model_used": "gpt-3.5-turbo",
            "response_time": 1.2
        },
        {
            "timestamp": "2023-10-01T10:01:00",
            "user": "What's the weather like?",
            "assistant": "I don't have access to real-time weather data, but I can help you find weather information from reliable sources.",
            "tokens_used": 35,
            "model_used": "gpt-3.5-turbo",
            "response_time": 1.8
        },
        {
            "timestamp": "2023-10-01T10:02:00",
            "user": "Thank you for your help!",
            "assistant": "You're welcome! Feel free to ask if you need anything else.",
            "tokens_used": 18,
            "model_used": "gpt-3.5-turbo",
            "response_time": 0.9
        }
    ]


@pytest.fixture
def conversation_file(temp_dir, sample_conversations):
    """
    Create a test conversation file with sample data.
    """
    conv_file = temp_dir / "test_conversations.json"
    with open(conv_file, 'w', encoding='utf-8') as f:
        json.dump(sample_conversations, f, indent=2)
    
    return conv_file


@pytest.fixture
def conversation_manager(app_config):
    """
    Create a conversation manager for testing.
    """
    return ConversationManager(app_config)


@pytest.fixture
def mock_openai(monkeypatch):
    """
    Mock the entire openai module to prevent actual API calls.
    """
    mock_openai_module = Mock()
    
    # Mock successful API response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response from AI"
    mock_response.usage.total_tokens = 30
    
    mock_openai_module.ChatCompletion.create.return_value = mock_response
    mock_openai_module.error = Mock()
    mock_openai_module.error.RateLimitError = Exception
    mock_openai_module.error.APIError = Exception
    mock_openai_module.error.InvalidRequestError = Exception
    mock_openai_module.error.AuthenticationError = Exception
    mock_openai_module.error.PermissionError = Exception
    
    monkeypatch.setattr('core.ai_client.openai', mock_openai_module)
    monkeypatch.setattr('openai', mock_openai_module)
    
    return mock_openai_module


@pytest.fixture
def ai_client(ai_config, mock_openai):
    """
    Create a real AI client with mocked OpenAI API.
    """
    return AIClient(ai_config)


@pytest.fixture
def corrupted_conversation_file(temp_dir):
    """
    Create a corrupted conversation file for testing error handling.
    """
    conv_file = temp_dir / "corrupted_conversations.json"
    with open(conv_file, 'w', encoding='utf-8') as f:
        f.write('{"invalid": json syntax')  # Intentionally corrupted JSON
    
    return conv_file


@pytest.fixture
def large_conversation_history():
    """
    Generate a large conversation history for performance testing.
    """
    conversations = []
    for i in range(100):
        conversations.append({
            "timestamp": f"2023-10-01T{i:02d}:00:00",
            "user": f"This is test message number {i}",
            "assistant": f"This is test response number {i}",
            "tokens_used": 20 + (i % 10),
            "model_used": "gpt-3.5-turbo",
            "response_time": 1.0 + (i % 5) * 0.1
        })
    
    return conversations


@pytest.fixture
def error_scenarios():
    """
    Define various error scenarios for testing error handling.
    """
    return {
        'rate_limit': {
            'exception_type': 'RateLimitError',
            'message': 'Rate limit exceeded',
            'expected_error_type': ErrorType.RATE_LIMIT
        },
        'api_error': {
            'exception_type': 'APIError',
            'message': 'API service unavailable',
            'expected_error_type': ErrorType.API_ERROR
        },
        'invalid_request': {
            'exception_type': 'InvalidRequestError',
            'message': 'Invalid request parameters',
            'expected_error_type': ErrorType.INVALID_REQUEST
        },
        'authentication': {
            'exception_type': 'AuthenticationError',
            'message': 'Invalid API key',
            'expected_error_type': ErrorType.AUTHENTICATION
        },
        'permission': {
            'exception_type': 'PermissionError',
            'message': 'Insufficient permissions',
            'expected_error_type': ErrorType.QUOTA_EXCEEDED
        }
    }


@pytest.fixture
def mock_file_operations(monkeypatch):
    """
    Mock file operations to test file handling without actual file I/O.
    """
    mock_open = Mock()
    mock_json = Mock()
    
    monkeypatch.setattr('builtins.open', mock_open)
    monkeypatch.setattr('json.dump', mock_json.dump)
    monkeypatch.setattr('json.load', mock_json.load)
    
    return {
        'open': mock_open,
        'json': mock_json
    }


# Pytest configuration
def pytest_configure(config):
    """
    Configure pytest with custom markers and settings.
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "mock: mark test as using mocks"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_runtest_setup(item):
    """
    Setup function run before each test.
    """
    # Ensure clean environment for each test
    if hasattr(item, 'function'):
        # Reset any global state if needed
        pass


def pytest_runtest_teardown(item):
    """
    Teardown function run after each test.
    """
    # Clean up any test artifacts
    if hasattr(item, 'function'):
        # Cleanup any global state if needed
        pass


# Helper functions for tests
class TestHelpers:
    """
    Helper functions for test assertions and setup.
    """
    
    @staticmethod
    def assert_conversation_exchange(exchange: ConversationExchange, 
                                   expected_user: str, 
                                   expected_assistant: str):
        """
        Helper to assert conversation exchange properties.
        """
        assert exchange.user == expected_user
        assert exchange.assistant == expected_assistant
        assert exchange.timestamp is not None
        assert isinstance(exchange.tokens_used, int)
        assert isinstance(exchange.response_time, float)
    
    @staticmethod
    def assert_ai_response_success(response: AIResponse, 
                                 expected_content: str = None):
        """
        Helper to assert successful AI response.
        """
        assert response.success is True
        assert response.error_message is None
        assert response.error_type is None
        assert response.content is not None
        assert response.tokens_used >= 0
        assert response.response_time >= 0.0
        
        if expected_content:
            assert response.content == expected_content
    
    @staticmethod
    def assert_ai_response_failure(response: AIResponse, 
                                 expected_error_type: ErrorType = None,
                                 expected_message_contains: str = None):
        """
        Helper to assert failed AI response.
        """
        assert response.success is False
        assert response.error_message is not None
        assert response.content == ""
        
        if expected_error_type:
            assert response.error_type == expected_error_type
        
        if expected_message_contains:
            assert expected_message_contains in response.error_message


# Make TestHelpers available to all tests
@pytest.fixture
def test_helpers():
    """
    Provide test helper functions.
    """
    return TestHelpers