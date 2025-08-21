"""
AI Client Module Tests

Tests for the AI service integration module, validating API interactions,
error handling, retry logic, and response management. This demonstrates
professional testing of external service integrations.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from core.ai_client import AIClient, AIResponse, ErrorType, ConversationMessage


class TestAIResponse:
    """Test cases for AIResponse data structure."""
    
    @pytest.mark.unit
    def test_ai_response_creation(self):
        """Test creating AIResponse objects."""
        response = AIResponse(
            content="Test response",
            success=True,
            tokens_used=25,
            model_used="gpt-3.5-turbo",
            response_time=1.5
        )
        
        assert response.content == "Test response"
        assert response.success is True
        assert response.error_type is None
        assert response.error_message is None
        assert response.tokens_used == 25
        assert response.model_used == "gpt-3.5-turbo"
        assert response.response_time == 1.5
        assert response.attempt_count == 1
    
    @pytest.mark.unit
    def test_ai_response_error(self):
        """Test creating error AIResponse objects."""
        response = AIResponse(
            content="",
            success=False,
            error_type=ErrorType.RATE_LIMIT,
            error_message="Rate limit exceeded",
            attempt_count=3
        )
        
        assert response.content == ""
        assert response.success is False
        assert response.error_type == ErrorType.RATE_LIMIT
        assert response.error_message == "Rate limit exceeded"
        assert response.tokens_used == 0
        assert response.attempt_count == 3
    
    @pytest.mark.unit
    def test_ai_response_to_dict(self):
        """Test converting AIResponse to dictionary."""
        response = AIResponse(
            content="Test",
            success=True,
            error_type=ErrorType.API_ERROR,
            tokens_used=10
        )
        
        result = response.to_dict()
        
        assert isinstance(result, dict)
        assert result['content'] == "Test"
        assert result['success'] is True
        assert result['error_type'] == ErrorType.API_ERROR.value
        assert result['tokens_used'] == 10


class TestConversationMessage:
    """Test cases for ConversationMessage data structure."""
    
    @pytest.mark.unit
    def test_conversation_message_creation(self):
        """Test creating ConversationMessage objects."""
        message = ConversationMessage(
            role="user",
            content="Hello AI",
            timestamp="2023-10-01T10:00:00"
        )
        
        assert message.role == "user"
        assert message.content == "Hello AI"
        assert message.timestamp == "2023-10-01T10:00:00"
    
    @pytest.mark.unit
    def test_conversation_message_to_openai_format(self):
        """Test converting to OpenAI API format."""
        message = ConversationMessage(
            role="assistant",
            content="Hello user",
            timestamp="2023-10-01T10:01:00"
        )
        
        result = message.to_openai_format()
        
        assert result == {
            "role": "assistant",
            "content": "Hello user"
        }
        # Timestamp should not be included in OpenAI format


class TestAIClient:
    """Test cases for AIClient functionality."""
    
    @pytest.mark.unit
    def test_ai_client_initialization(self, ai_config, mock_openai):
        """Test AI client initialization."""
        client = AIClient(ai_config)
        
        assert client.config == ai_config
        assert client.total_requests == 0
        assert client.successful_requests == 0
        assert client.failed_requests == 0
        assert client.total_tokens_used == 0
        assert client.total_response_time == 0.0
    
    @pytest.mark.unit
    def test_successful_response_generation(self, ai_client, mock_openai):
        """Test successful AI response generation."""
        user_message = "Hello, how are you?"
        
        response = ai_client.generate_response(user_message)
        
        assert response.success is True
        assert response.content == "Test response from AI"
        assert response.error_type is None
        assert response.error_message is None
        assert response.tokens_used == 30
        assert response.model_used == ai_client.config.model
        assert response.response_time > 0
        assert response.attempt_count == 1
    
    @pytest.mark.unit
    def test_response_with_conversation_history(self, ai_client, mock_openai, sample_conversations):
        """Test response generation with conversation history."""
        user_message = "Continue our conversation"
        
        response = ai_client.generate_response(
            user_message, 
            conversation_history=sample_conversations
        )
        
        assert response.success is True
        # Verify that the API was called with proper message structure
        mock_openai.ChatCompletion.create.assert_called_once()
        call_args = mock_openai.ChatCompletion.create.call_args[1]
        messages = call_args['messages']
        
        # Should include system message, history, and current message
        assert len(messages) >= 4  # At least system + some history + user message
        assert messages[0]['role'] == 'system'
        assert messages[-1]['role'] == 'user'
        assert messages[-1]['content'] == user_message
    
    @pytest.mark.unit
    def test_custom_system_prompt(self, ai_client, mock_openai):
        """Test response generation with custom system prompt."""
        user_message = "Test message"
        custom_prompt = "You are a specialized assistant."
        
        response = ai_client.generate_response(
            user_message,
            custom_system_prompt=custom_prompt
        )
        
        assert response.success is True
        
        # Verify custom system prompt was used
        call_args = mock_openai.ChatCompletion.create.call_args[1]
        messages = call_args['messages']
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == custom_prompt
    
    @pytest.mark.unit
    def test_build_messages_basic(self, ai_client):
        """Test message building without history."""
        user_message = "Hello"
        
        messages = ai_client._build_messages(user_message)
        
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == ai_client.config.system_prompt
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == user_message
    
    @pytest.mark.unit
    def test_build_messages_with_history(self, ai_client, sample_conversations):
        """Test message building with conversation history."""
        user_message = "Current message"
        
        messages = ai_client._build_messages(user_message, sample_conversations)
        
        # Should include system message + history pairs + current message
        assert len(messages) >= 4
        assert messages[0]['role'] == 'system'
        assert messages[-1]['role'] == 'user'
        assert messages[-1]['content'] == user_message
        
        # Check that history is properly formatted
        for i in range(1, len(messages) - 1, 2):
            if i + 1 < len(messages) - 1:  # Ensure we have pairs
                assert messages[i]['role'] == 'user'
                assert messages[i + 1]['role'] == 'assistant'


class TestAIClientErrorHandling:
    """Test cases for AI client error handling and retry logic."""
    
    @pytest.mark.unit
    def test_rate_limit_error_with_retry(self, ai_client, mock_openai, error_scenarios):
        """Test rate limit error handling with successful retry."""
        # Configure mock to fail once, then succeed
        mock_openai.ChatCompletion.create.side_effect = [
            mock_openai.error.RateLimitError("Rate limit exceeded"),
            Mock(choices=[Mock(message=Mock(content="Success after retry"))], 
                 usage=Mock(total_tokens=25))
        ]
        
        with patch('time.sleep'):  # Speed up test by mocking sleep
            response = ai_client.generate_response("Test message")
        
        assert response.success is True
        assert response.content == "Success after retry"
        assert response.attempt_count == 2
        assert mock_openai.ChatCompletion.create.call_count == 2
    
    @pytest.mark.unit
    def test_rate_limit_error_max_retries(self, ai_client, mock_openai):
        """Test rate limit error when max retries exceeded."""
        # Configure mock to always fail with rate limit
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.RateLimitError("Rate limit")
        
        with patch('time.sleep'):  # Speed up test
            response = ai_client.generate_response("Test message")
        
        assert response.success is False
        assert response.error_type == ErrorType.RATE_LIMIT
        assert "Rate limit exceeded" in response.error_message
        assert response.attempt_count == ai_client.config.max_retries + 1
    
    @pytest.mark.unit
    def test_api_error_handling(self, ai_client, mock_openai):
        """Test general API error handling."""
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.APIError("Service unavailable")
        
        with patch('time.sleep'):
            response = ai_client.generate_response("Test message")
        
        assert response.success is False
        assert response.error_type == ErrorType.API_ERROR
        assert "temporarily unavailable" in response.error_message
    
    @pytest.mark.unit
    def test_invalid_request_error(self, ai_client, mock_openai):
        """Test invalid request error handling."""
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.InvalidRequestError("Invalid params")
        
        response = ai_client.generate_response("Test message")
        
        assert response.success is False
        assert response.error_type == ErrorType.INVALID_REQUEST
        assert "Invalid request" in response.error_message
        # Should not retry for invalid request
        assert mock_openai.ChatCompletion.create.call_count == 1
    
    @pytest.mark.unit
    def test_authentication_error(self, ai_client, mock_openai):
        """Test authentication error handling."""
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.AuthenticationError("Invalid API key")
        
        response = ai_client.generate_response("Test message")
        
        assert response.success is False
        assert response.error_type == ErrorType.AUTHENTICATION
        assert "Authentication failed" in response.error_message
        # Should not retry for auth error
        assert mock_openai.ChatCompletion.create.call_count == 1
    
    @pytest.mark.unit
    def test_permission_error(self, ai_client, mock_openai):
        """Test permission/quota error handling."""
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.PermissionError("Quota exceeded")
        
        response = ai_client.generate_response("Test message")
        
        assert response.success is False
        assert response.error_type == ErrorType.QUOTA_EXCEEDED
        assert "quota exceeded" in response.error_message
    
    @pytest.mark.unit
    def test_unexpected_error(self, ai_client, mock_openai):
        """Test handling of unexpected errors."""
        mock_openai.ChatCompletion.create.side_effect = Exception("Unexpected error")
        
        response = ai_client.generate_response("Test message")
        
        assert response.success is False
        assert response.error_type == ErrorType.UNKNOWN
        assert "unexpected error" in response.error_message
    
    @pytest.mark.unit
    def test_exponential_backoff(self, ai_client, mock_openai):
        """Test exponential backoff timing."""
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.RateLimitError("Rate limit")
        
        with patch('time.sleep') as mock_sleep:
            ai_client.generate_response("Test message")
        
        # Verify exponential backoff: should sleep for 1, 2, 4 seconds (or capped at 60)
        sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
        expected_pattern = [min(2**i, 60) for i in range(ai_client.config.max_retries)]
        assert sleep_calls == expected_pattern


class TestAIClientStatistics:
    """Test cases for AI client statistics tracking."""
    
    @pytest.mark.unit
    def test_statistics_initial_state(self, ai_client):
        """Test initial statistics state."""
        stats = ai_client.get_statistics()
        
        assert stats['total_requests'] == 0
        assert stats['successful_requests'] == 0
        assert stats['failed_requests'] == 0
        assert stats['success_rate_percent'] == 0.0
        assert stats['total_tokens_used'] == 0
        assert stats['average_response_time_seconds'] == 0.0
        assert stats['model_used'] == ai_client.config.model
        assert stats['max_retries_configured'] == ai_client.config.max_retries
    
    @pytest.mark.unit
    def test_statistics_after_successful_request(self, ai_client, mock_openai):
        """Test statistics after successful requests."""
        # Make successful request
        ai_client.generate_response("Test message 1")
        ai_client.generate_response("Test message 2")
        
        stats = ai_client.get_statistics()
        
        assert stats['total_requests'] == 2
        assert stats['successful_requests'] == 2
        assert stats['failed_requests'] == 0
        assert stats['success_rate_percent'] == 100.0
        assert stats['total_tokens_used'] == 60  # 30 tokens per request
        assert stats['average_response_time_seconds'] > 0
    
    @pytest.mark.unit
    def test_statistics_after_failed_request(self, ai_client, mock_openai):
        """Test statistics after failed requests."""
        # Make one successful and one failed request
        ai_client.generate_response("Success")
        
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.APIError("Failed")
        with patch('time.sleep'):
            ai_client.generate_response("Failure")
        
        stats = ai_client.get_statistics()
        
        assert stats['total_requests'] == 2
        assert stats['successful_requests'] == 1
        assert stats['failed_requests'] == 1
        assert stats['success_rate_percent'] == 50.0
        assert stats['total_tokens_used'] == 30  # Only successful request counted
    
    @pytest.mark.unit
    def test_reset_statistics(self, ai_client, mock_openai):
        """Test resetting statistics."""
        # Make some requests
        ai_client.generate_response("Test")
        
        # Reset statistics
        ai_client.reset_statistics()
        
        stats = ai_client.get_statistics()
        assert stats['total_requests'] == 0
        assert stats['successful_requests'] == 0
        assert stats['failed_requests'] == 0
        assert stats['total_tokens_used'] == 0


class TestAIClientHealthCheck:
    """Test cases for AI client health check functionality."""
    
    @pytest.mark.unit
    def test_health_check_success(self, ai_client, mock_openai):
        """Test successful health check."""
        result = ai_client.health_check()
        
        assert result is True
        mock_openai.ChatCompletion.create.assert_called_once()
    
    @pytest.mark.unit
    def test_health_check_failure(self, ai_client, mock_openai):
        """Test failed health check."""
        mock_openai.ChatCompletion.create.side_effect = Exception("Service down")
        
        result = ai_client.health_check()
        
        assert result is False
    
    @pytest.mark.unit
    def test_health_check_api_error(self, ai_client, mock_openai):
        """Test health check with API error."""
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.APIError("API error")
        
        with patch('time.sleep'):
            result = ai_client.health_check()
        
        assert result is False


@pytest.mark.integration
class TestAIClientIntegration:
    """Integration tests for AI client with other components."""
    
    def test_ai_client_with_conversation_manager(self, ai_client, conversation_manager, mock_openai):
        """Test AI client integration with conversation manager."""
        # Generate response
        response = ai_client.generate_response("Hello")
        
        # Add to conversation manager
        conversation_manager.add_exchange(
            user_message="Hello",
            ai_response=response.content,
            tokens_used=response.tokens_used,
            model_used=response.model_used,
            response_time=response.response_time
        )
        
        # Verify integration
        stats = conversation_manager.get_statistics()
        assert stats['total_exchanges'] == 1
        assert stats['total_tokens_used'] == response.tokens_used
    
    def test_ai_client_with_configuration_changes(self, mock_openai, mock_env_vars, monkeypatch):
        """Test AI client behavior with different configurations."""
        # Test with different model
        monkeypatch.setenv('AI_MODEL', 'gpt-4')
        monkeypatch.setenv('MAX_TOKENS', '2000')
        monkeypatch.setenv('TEMPERATURE', '0.9')
        
        from config.settings import AIConfig
        config = AIConfig.from_environment()
        client = AIClient(config)
        
        assert client.config.model == 'gpt-4'
        assert client.config.max_tokens == 2000
        assert client.config.temperature == 0.9
        
        # Verify API is called with correct parameters
        client.generate_response("Test")
        
        call_args = mock_openai.ChatCompletion.create.call_args[1]
        assert call_args['model'] == 'gpt-4'
        assert call_args['max_tokens'] == 2000
        assert call_args['temperature'] == 0.9


@pytest.mark.slow
class TestAIClientPerformance:
    """Performance tests for AI client (marked as slow)."""
    
    def test_multiple_concurrent_requests(self, ai_client, mock_openai):
        """Test handling of multiple requests."""
        import threading
        import time
        
        results = []
        
        def make_request(i):
            response = ai_client.generate_response(f"Message {i}")
            results.append(response)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        assert len(results) == 10
        assert all(result.success for result in results)
        
        # Verify statistics
        stats = ai_client.get_statistics()
        assert stats['total_requests'] == 10
        assert stats['successful_requests'] == 10
    
    def test_large_conversation_history(self, ai_client, mock_openai, large_conversation_history):
        """Test handling of large conversation histories."""
        response = ai_client.generate_response(
            "Current message",
            conversation_history=large_conversation_history
        )
        
        assert response.success is True
        
        # Verify that history was truncated appropriately
        call_args = mock_openai.ChatCompletion.create.call_args[1]
        messages = call_args['messages']
        
        # Should not include all 100 conversations (would be too many tokens)
        assert len(messages) < 200  # Much less than 100 * 2 + 2