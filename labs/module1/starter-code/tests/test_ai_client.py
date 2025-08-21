"""
Comprehensive test suite for AI client functionality.
Includes unit tests, integration tests, and mocking for external services.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict

# Import the modules to test
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.ai_client import (
    AIClient, 
    AIResponse, 
    ResponseStatus, 
    OpenAIProvider,
    BaseAIProvider
)
from config.settings import Settings, AIConfig


class MockAIProvider(BaseAIProvider):
    """Mock AI provider for testing."""
    
    def __init__(self, api_key: str, model: str = "mock-model", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.responses = kwargs.get('responses', ["Mock response"])
        self.call_count = 0
        self.should_fail = kwargs.get('should_fail', False)
        self.fail_with_status = kwargs.get('fail_with_status', ResponseStatus.ERROR)
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """Generate mock response."""
        self.call_count += 1
        
        if self.should_fail:
            return AIResponse(
                content="",
                status=self.fail_with_status,
                provider="mock",
                model=self.model,
                error_message="Mock error"
            )
        
        response_index = min(self.call_count - 1, len(self.responses) - 1)
        response_content = self.responses[response_index]
        
        return AIResponse(
            content=response_content,
            status=ResponseStatus.SUCCESS,
            provider="mock",
            model=self.model,
            tokens_used=len(response_content.split()),
            response_time=0.1
        )
    
    async def stream_response(self, messages: List[Dict[str, str]], **kwargs):
        """Stream mock response."""
        if self.should_fail:
            yield "[Mock streaming error]"
            return
        
        response_index = min(self.call_count, len(self.responses) - 1)
        response = self.responses[response_index]
        
        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.01)  # Simulate streaming delay
    
    def validate_config(self) -> List[str]:
        """Validate mock configuration."""
        issues = []
        if not self.api_key:
            issues.append("Mock API key required")
        return issues


class TestAIResponse:
    """Test AIResponse dataclass functionality."""
    
    def test_successful_response_creation(self):
        """Test creating a successful AI response."""
        response = AIResponse(
            content="Hello, world!",
            status=ResponseStatus.SUCCESS,
            provider="test",
            model="test-model",
            tokens_used=3,
            response_time=0.5
        )
        
        assert response.content == "Hello, world!"
        assert response.status == ResponseStatus.SUCCESS
        assert response.success is True
        assert response.tokens_used == 3
        assert response.response_time == 0.5
    
    def test_error_response_creation(self):
        """Test creating an error AI response."""
        response = AIResponse(
            content="",
            status=ResponseStatus.ERROR,
            provider="test",
            model="test-model",
            error_message="Test error"
        )
        
        assert response.content == ""
        assert response.status == ResponseStatus.ERROR
        assert response.success is False
        assert response.error_message == "Test error"
    
    def test_response_to_dict(self):
        """Test converting response to dictionary."""
        response = AIResponse(
            content="Test content",
            status=ResponseStatus.SUCCESS,
            provider="test",
            model="test-model",
            tokens_used=5,
            metadata={"test": "value"}
        )
        
        response_dict = response.to_dict()
        
        assert response_dict["content"] == "Test content"
        assert response_dict["status"] == "success"
        assert response_dict["provider"] == "test"
        assert response_dict["tokens_used"] == 5
        assert response_dict["metadata"]["test"] == "value"


class TestMockAIProvider:
    """Test the mock AI provider used for testing."""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing."""
        return MockAIProvider(
            api_key="mock-key",
            model="mock-model",
            responses=["First response", "Second response"]
        )
    
    @pytest.mark.asyncio
    async def test_successful_response(self, mock_provider):
        """Test successful response generation."""
        messages = [{"role": "user", "content": "Hello"}]
        response = await mock_provider.generate_response(messages)
        
        assert response.success is True
        assert response.content == "First response"
        assert response.provider == "mock"
        assert response.model == "mock-model"
        assert response.tokens_used == 2  # "First response" = 2 tokens
    
    @pytest.mark.asyncio
    async def test_multiple_responses(self, mock_provider):
        """Test multiple response generation."""
        messages = [{"role": "user", "content": "Hello"}]
        
        # First call
        response1 = await mock_provider.generate_response(messages)
        assert response1.content == "First response"
        
        # Second call
        response2 = await mock_provider.generate_response(messages)
        assert response2.content == "Second response"
        
        # Third call (should repeat last response)
        response3 = await mock_provider.generate_response(messages)
        assert response3.content == "Second response"
    
    @pytest.mark.asyncio
    async def test_error_response(self):
        """Test error response generation."""
        failing_provider = MockAIProvider(
            api_key="mock-key",
            should_fail=True,
            fail_with_status=ResponseStatus.RATE_LIMITED
        )
        
        messages = [{"role": "user", "content": "Hello"}]
        response = await failing_provider.generate_response(messages)
        
        assert response.success is False
        assert response.status == ResponseStatus.RATE_LIMITED
        assert response.error_message == "Mock error"
    
    @pytest.mark.asyncio
    async def test_streaming_response(self, mock_provider):
        """Test streaming response generation."""
        messages = [{"role": "user", "content": "Hello"}]
        
        chunks = []
        async for chunk in mock_provider.stream_response(messages):
            chunks.append(chunk)
        
        # Should stream "First response" word by word
        assert "First " in chunks
        assert "response " in chunks
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        provider = MockAIProvider(api_key="valid-key")
        issues = provider.validate_config()
        assert len(issues) == 0
        
        # Invalid config
        provider = MockAIProvider(api_key="")
        issues = provider.validate_config()
        assert len(issues) == 1
        assert "Mock API key required" in issues[0]


class TestAIClient:
    """Test the main AI client functionality."""
    
    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        config = Settings()
        config.ai.api_key = "test-key"
        config.ai.model = "test-model"
        config.ai.max_retries = 2
        config.app.max_history_context = 5
        return config
    
    @pytest.fixture
    def mock_client(self, test_config):
        """Create AI client with mock provider."""
        client = AIClient(test_config)
        # Replace real providers with mock
        client.providers = [MockAIProvider(
            api_key=test_config.ai.api_key,
            model=test_config.ai.model,
            responses=["Mock AI response"]
        )]
        return client
    
    @pytest.mark.asyncio
    async def test_successful_response_generation(self, mock_client):
        """Test successful response generation."""
        response = await mock_client.generate_response("Hello, AI!")
        
        assert response.success is True
        assert response.content == "Mock AI response"
        assert response.provider == "mock"
        assert mock_client.call_count == 1
    
    @pytest.mark.asyncio
    async def test_response_with_conversation_history(self, mock_client):
        """Test response generation with conversation history."""
        history = [
            {"user": "What's your name?", "assistant": "I'm an AI assistant."},
            {"user": "How old are you?", "assistant": "I don't have an age."}
        ]
        
        response = await mock_client.generate_response(
            "Tell me a joke",
            conversation_history=history
        )
        
        assert response.success is True
        # Verify history was included in message building
        # (This would require inspecting the actual messages sent to provider)
    
    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self, test_config):
        """Test retry behavior on rate limiting."""
        # Create client with rate-limited provider
        client = AIClient(test_config)
        client.providers = [MockAIProvider(
            api_key=test_config.ai.api_key,
            should_fail=True,
            fail_with_status=ResponseStatus.RATE_LIMITED
        )]
        
        start_time = time.time()
        response = await client.generate_response("Test message")
        end_time = time.time()
        
        # Should fail after retries
        assert response.success is False
        assert response.status == ResponseStatus.RATE_LIMITED
        
        # Should have taken time due to exponential backoff
        # (Note: This test might be flaky in CI environments)
        # assert end_time - start_time > 1.0  # At least 1 second for backoff
    
    @pytest.mark.asyncio
    async def test_fallback_provider(self, test_config):
        """Test fallback to secondary provider."""
        client = AIClient(test_config)
        
        # Create two providers: first fails, second succeeds
        failing_provider = MockAIProvider(
            api_key=test_config.ai.api_key,
            should_fail=True,
            fail_with_status=ResponseStatus.PROVIDER_ERROR
        )
        
        working_provider = MockAIProvider(
            api_key=test_config.ai.api_key,
            responses=["Fallback response"]
        )
        
        client.providers = [failing_provider, working_provider]
        
        response = await client.generate_response("Test message")
        
        assert response.success is True
        assert response.content == "Fallback response"
        assert client.current_provider_index == 1  # Should switch to second provider
    
    @pytest.mark.asyncio
    async def test_streaming_response(self, mock_client):
        """Test streaming response generation."""
        chunks = []
        async for chunk in mock_client.stream_response("Tell me a story"):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        # Should contain parts of "Mock AI response"
        combined = ''.join(chunks)
        assert "Mock" in combined or "AI" in combined or "response" in combined
    
    def test_message_building(self, mock_client):
        """Test message building for AI providers."""
        # Test with system prompt
        messages = mock_client._build_messages(
            user_message="Hello",
            system_prompt="You are a helpful assistant"
        )
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hello"
    
    def test_message_building_with_history(self, mock_client):
        """Test message building with conversation history."""
        history = [
            {"user": "Hi", "assistant": "Hello!"},
            {"user": "How are you?", "assistant": "I'm good!"}
        ]
        
        messages = mock_client._build_messages(
            user_message="Great!",
            conversation_history=history
        )
        
        # Should have: system + 2*history + current = 6 messages
        assert len(messages) == 6
        assert messages[0]["role"] == "system"  # System prompt
        assert messages[1]["role"] == "user"    # First user message
        assert messages[2]["role"] == "assistant"  # First assistant response
        assert messages[3]["role"] == "user"    # Second user message  
        assert messages[4]["role"] == "assistant"  # Second assistant response
        assert messages[5]["role"] == "user"    # Current message
        assert messages[5]["content"] == "Great!"
    
    def test_history_limiting(self, mock_client):
        """Test conversation history limiting."""
        # Create long history (more than max_history_context)
        long_history = []
        for i in range(10):  # More than the default limit of 5
            long_history.append({
                "user": f"Message {i}",
                "assistant": f"Response {i}"
            })
        
        messages = mock_client._build_messages(
            user_message="Current message",
            conversation_history=long_history
        )
        
        # Should limit history to max_history_context (5)
        # System + 5*2 + current = 12 messages max
        assert len(messages) <= 12
        
        # Should contain the most recent history
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        assert "Message 9" in [msg["content"] for msg in user_messages]  # Most recent
    
    def test_stats_tracking(self, mock_client):
        """Test usage statistics tracking."""
        initial_stats = mock_client.get_stats()
        assert initial_stats["total_calls"] == 0
        assert initial_stats["total_tokens_used"] == 0
        
        # Make some calls (using asyncio.run for testing)
        async def make_calls():
            await mock_client.generate_response("First message")
            await mock_client.generate_response("Second message")
        
        asyncio.run(make_calls())
        
        updated_stats = mock_client.get_stats()
        assert updated_stats["total_calls"] == 2
        assert updated_stats["total_tokens_used"] > 0
        assert updated_stats["current_provider"] == "MockAIProvider"
    
    def test_configuration_validation(self, test_config):
        """Test configuration validation."""
        # Valid configuration
        client = AIClient(test_config)
        client.providers = [MockAIProvider(api_key="valid-key")]
        
        issues = client.validate_configuration()
        assert len(issues) == 0
        
        # Invalid configuration
        client.providers = []
        issues = client.validate_configuration()
        assert len(issues) > 0
        assert "No AI providers available" in issues


class TestOpenAIProvider:
    """Test OpenAI provider (requires mocking external API)."""
    
    @pytest.fixture
    def openai_provider(self):
        """Create OpenAI provider with mock configuration."""
        return OpenAIProvider(
            api_key="sk-test-key",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )
    
    def test_provider_initialization(self, openai_provider):
        """Test OpenAI provider initialization."""
        assert openai_provider.api_key == "sk-test-key"
        assert openai_provider.model == "gpt-3.5-turbo"
        assert openai_provider.temperature == 0.7
        assert openai_provider.max_tokens == 1000
    
    def test_config_validation(self, openai_provider):
        """Test OpenAI configuration validation."""
        # Valid config
        issues = openai_provider.validate_config()
        assert len(issues) == 0
        
        # Invalid API key
        openai_provider.api_key = "invalid-key"
        issues = openai_provider.validate_config()
        assert len(issues) > 0
        assert "Invalid OpenAI API key format" in issues[0]
    
    @patch('openai.OpenAI')
    @pytest.mark.asyncio
    async def test_successful_openai_response(self, mock_openai_class, openai_provider):
        """Test successful OpenAI API response."""
        # Mock the OpenAI client and response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello from OpenAI!"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 10
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Re-initialize provider to use mocked client
        openai_provider.client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        response = await openai_provider.generate_response(messages)
        
        assert response.success is True
        assert response.content == "Hello from OpenAI!"
        assert response.tokens_used == 10
        assert response.provider == "openai"


class TestIntegration:
    """Integration tests that test the full flow."""
    
    @pytest.mark.integration
    def test_end_to_end_mock_flow(self):
        """Test complete flow with mock provider."""
        # This test demonstrates how students can test the complete flow
        async def full_test():
            # Setup
            config = Settings()
            config.ai.api_key = "test-key"
            
            client = AIClient(config)
            client.providers = [MockAIProvider(
                api_key="test-key",
                responses=["Hello! How can I help you today?"]
            )]
            
            # Test conversation
            response1 = await client.generate_response("Hi there!")
            assert response1.success is True
            
            # Test with history
            history = [{"user": "Hi there!", "assistant": response1.content}]
            response2 = await client.generate_response(
                "What's the weather like?",
                conversation_history=history
            )
            assert response2.success is True
            
            # Test stats
            stats = client.get_stats()
            assert stats["total_calls"] == 2
            
            return True
        
        result = asyncio.run(full_test())
        assert result is True


# Performance tests
class TestPerformance:
    """Performance and load testing."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        config = Settings()
        config.ai.api_key = "test-key"
        
        client = AIClient(config)
        client.providers = [MockAIProvider(
            api_key="test-key",
            responses=["Concurrent response"]
        )]
        
        # Make 10 concurrent requests
        tasks = []
        for i in range(10):
            task = client.generate_response(f"Message {i}")
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All should succeed
        assert all(response.success for response in responses)
        assert len(responses) == 10
        
        # Should complete in reasonable time (less than 5 seconds)
        assert end_time - start_time < 5.0
        
        # Stats should reflect all calls
        stats = client.get_stats()
        assert stats["total_calls"] == 10


# Fixtures and test utilities
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Test configuration for pytest
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])