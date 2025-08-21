"""
AI Service Integration Module

This module demonstrates professional AI API integration with comprehensive
error handling, retry logic, and response management. It encapsulates all
AI service communication and provides a clean interface for the application.

Key improvements over the original script:
- Structured response objects with metadata
- Exponential backoff retry logic
- Comprehensive error handling for all API scenarios
- Request/response logging for debugging
- Token usage tracking
- Timeout and rate limit management
"""

import openai
import time
import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json


# Configure module logger
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Enumeration of possible AI service error types."""
    RATE_LIMIT = "rate_limit"
    API_ERROR = "api_error"
    INVALID_REQUEST = "invalid_request"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNKNOWN = "unknown"


@dataclass
class AIResponse:
    """
    Structured response from AI service with comprehensive metadata.
    
    This class encapsulates all information about an AI service response,
    including success/failure status, content, usage statistics, and
    error details when applicable.
    
    Attributes:
        content: The AI-generated response text
        success: Whether the request was successful
        error_type: Type of error if request failed
        error_message: Human-readable error description
        tokens_used: Total tokens consumed by the request
        model_used: AI model that generated the response
        response_time: Time taken to generate response in seconds
        attempt_count: Number of attempts made (for retry scenarios)
    """
    content: str
    success: bool
    error_type: Optional[ErrorType] = None
    error_message: Optional[str] = None
    tokens_used: int = 0
    model_used: str = ""
    response_time: float = 0.0
    attempt_count: int = 1
    
    def to_dict(self) -> Dict:
        """Convert response to dictionary for logging/serialization."""
        return {
            "content": self.content,
            "success": self.success,
            "error_type": self.error_type.value if self.error_type else None,
            "error_message": self.error_message,
            "tokens_used": self.tokens_used,
            "model_used": self.model_used,
            "response_time": self.response_time,
            "attempt_count": self.attempt_count
        }


@dataclass
class ConversationMessage:
    """
    Structured conversation message for API requests.
    
    Attributes:
        role: Message role (system, user, assistant)
        content: Message content
        timestamp: When the message was created (for context ordering)
    """
    role: str
    content: str
    timestamp: Optional[str] = None
    
    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI API message format."""
        return {
            "role": self.role,
            "content": self.content
        }


class AIClient:
    """
    Professional AI service client with robust error handling.
    
    This class provides a clean, reliable interface to AI services with
    comprehensive error handling, retry logic, and usage tracking.
    Features include:
    - Exponential backoff for rate limits
    - Detailed error categorization
    - Request/response logging
    - Token usage tracking
    - Conversation context management
    """
    
    def __init__(self, config):
        """
        Initialize AI client with configuration.
        
        Args:
            config: AIConfig object with API key and settings
        """
        self.config = config
        self._setup_openai()
        self._reset_statistics()
        
        logger.info(f"AI Client initialized with model: {config.model}")
    
    def _setup_openai(self) -> None:
        """Configure OpenAI client with API key and settings."""
        openai.api_key = self.config.api_key
        
        # Log configuration (without exposing the API key)
        logger.debug(f"OpenAI configured: model={self.config.model}, "
                    f"max_tokens={self.config.max_tokens}, "
                    f"temperature={self.config.temperature}")
    
    def _reset_statistics(self) -> None:
        """Reset usage statistics."""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_tokens_used = 0
        self.total_response_time = 0.0
    
    def generate_response(self, 
                         user_message: str, 
                         conversation_history: Optional[List[Dict]] = None,
                         custom_system_prompt: Optional[str] = None) -> AIResponse:
        """
        Generate AI response with comprehensive error handling.
        
        This method handles the complete request lifecycle including:
        - Message formatting and context building
        - API request with retry logic
        - Error handling and categorization
        - Response validation and metadata collection
        
        Args:
            user_message: The user's input message
            conversation_history: Previous conversation context
            custom_system_prompt: Override default system prompt
            
        Returns:
            AIResponse: Structured response with content and metadata
        """
        start_time = time.time()
        self.total_requests += 1
        
        try:
            messages = self._build_messages(
                user_message, 
                conversation_history, 
                custom_system_prompt
            )
            
            logger.debug(f"Generating response for message: {user_message[:50]}...")
            
            response = self._make_request_with_retry(messages)
            
            if response.success:
                self.successful_requests += 1
                self.total_tokens_used += response.tokens_used
                logger.info(f"Response generated successfully in {response.response_time:.2f}s")
            else:
                self.failed_requests += 1
                logger.warning(f"Response generation failed: {response.error_message}")
            
            response.response_time = time.time() - start_time
            self.total_response_time += response.response_time
            
            return response
            
        except Exception as e:
            self.failed_requests += 1
            error_response = AIResponse(
                content="",
                success=False,
                error_type=ErrorType.UNKNOWN,
                error_message=f"Unexpected error: {str(e)}",
                response_time=time.time() - start_time
            )
            
            logger.error(f"Unexpected error in generate_response: {e}", exc_info=True)
            return error_response
    
    def _make_request_with_retry(self, messages: List[Dict]) -> AIResponse:
        """
        Make API request with exponential backoff retry logic.
        
        Args:
            messages: Formatted messages for the API request
            
        Returns:
            AIResponse: Response with success/failure details
        """
        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(f"API request attempt {attempt + 1}")
                
                response = openai.ChatCompletion.create(
                    model=self.config.model,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    timeout=self.config.timeout
                )
                
                # Successful response
                return AIResponse(
                    content=response.choices[0].message.content,
                    success=True,
                    tokens_used=response.usage.total_tokens,
                    model_used=self.config.model,
                    attempt_count=attempt + 1
                )
                
            except openai.error.RateLimitError as e:
                error_response = self._handle_rate_limit_error(e, attempt)
                if not error_response.success:
                    return error_response
                # Continue retry loop if we should retry
                
            except openai.error.APIError as e:
                return self._handle_api_error(e, attempt)
                
            except openai.error.InvalidRequestError as e:
                return self._handle_invalid_request_error(e)
                
            except openai.error.AuthenticationError as e:
                return self._handle_authentication_error(e)
                
            except openai.error.PermissionError as e:
                return self._handle_permission_error(e)
                
            except Exception as e:
                return self._handle_unexpected_error(e, attempt)
        
        # Max retries exceeded
        return AIResponse(
            content="",
            success=False,
            error_type=ErrorType.UNKNOWN,
            error_message="Maximum retry attempts exceeded",
            attempt_count=self.config.max_retries + 1
        )
    
    def _handle_rate_limit_error(self, error, attempt: int) -> AIResponse:
        """Handle rate limit errors with exponential backoff."""
        if attempt < self.config.max_retries:
            wait_time = min(2 ** attempt, 60)  # Cap at 60 seconds
            logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
            
            # Return success=True to indicate we should continue retrying
            return AIResponse(content="", success=True)
        else:
            return AIResponse(
                content="",
                success=False,
                error_type=ErrorType.RATE_LIMIT,
                error_message="Rate limit exceeded. Please try again in a few minutes.",
                attempt_count=attempt + 1
            )
    
    def _handle_api_error(self, error, attempt: int) -> AIResponse:
        """Handle general API errors."""
        logger.error(f"OpenAI API error on attempt {attempt + 1}: {error}")
        
        if attempt < self.config.max_retries:
            wait_time = 2 ** attempt
            logger.info(f"Retrying after {wait_time} seconds...")
            time.sleep(wait_time)
            
            # Return success=True to indicate we should continue retrying
            return AIResponse(content="", success=True)
        else:
            return AIResponse(
                content="",
                success=False,
                error_type=ErrorType.API_ERROR,
                error_message="AI service is temporarily unavailable. Please try again later.",
                attempt_count=attempt + 1
            )
    
    def _handle_invalid_request_error(self, error) -> AIResponse:
        """Handle invalid request errors (no retry)."""
        logger.error(f"Invalid request: {error}")
        return AIResponse(
            content="",
            success=False,
            error_type=ErrorType.INVALID_REQUEST,
            error_message="Invalid request. Please check your input and try again."
        )
    
    def _handle_authentication_error(self, error) -> AIResponse:
        """Handle authentication errors (no retry)."""
        logger.error(f"Authentication error: {error}")
        return AIResponse(
            content="",
            success=False,
            error_type=ErrorType.AUTHENTICATION,
            error_message="Authentication failed. Please check your API key."
        )
    
    def _handle_permission_error(self, error) -> AIResponse:
        """Handle permission/quota errors (no retry)."""
        logger.error(f"Permission/quota error: {error}")
        return AIResponse(
            content="",
            success=False,
            error_type=ErrorType.QUOTA_EXCEEDED,
            error_message="API quota exceeded. Please check your billing and usage limits."
        )
    
    def _handle_unexpected_error(self, error, attempt: int) -> AIResponse:
        """Handle unexpected errors."""
        logger.error(f"Unexpected error on attempt {attempt + 1}: {error}")
        
        return AIResponse(
            content="",
            success=False,
            error_type=ErrorType.UNKNOWN,
            error_message="An unexpected error occurred. Please try again.",
            attempt_count=attempt + 1
        )
    
    def _build_messages(self, 
                       user_message: str, 
                       history: Optional[List[Dict]] = None,
                       custom_system_prompt: Optional[str] = None) -> List[Dict]:
        """
        Build properly formatted message list for OpenAI API.
        
        Args:
            user_message: Current user message
            history: Previous conversation exchanges
            custom_system_prompt: Override for system prompt
            
        Returns:
            List[Dict]: Formatted messages ready for API request
        """
        messages = []
        
        # Add system message
        system_prompt = custom_system_prompt or self.config.system_prompt
        messages.append({
            "role": "system", 
            "content": system_prompt
        })
        
        # Add conversation history if provided
        if history:
            # Limit history to prevent token overflow
            recent_history = history[-self.config.max_tokens // 100:]  # Rough estimation
            
            for exchange in recent_history:
                if isinstance(exchange, dict):
                    # Handle different history formats
                    if "user" in exchange and "assistant" in exchange:
                        messages.append({"role": "user", "content": exchange["user"]})
                        messages.append({"role": "assistant", "content": exchange["assistant"]})
                    elif "role" in exchange and "content" in exchange:
                        messages.append({"role": exchange["role"], "content": exchange["content"]})
        
        # Add current user message
        messages.append({
            "role": "user", 
            "content": user_message
        })
        
        logger.debug(f"Built {len(messages)} messages for API request")
        return messages
    
    def get_statistics(self) -> Dict[str, Union[int, float, str]]:
        """
        Get comprehensive usage statistics.
        
        Returns:
            Dict: Statistics about API usage and performance
        """
        avg_response_time = (
            self.total_response_time / self.total_requests 
            if self.total_requests > 0 else 0.0
        )
        
        success_rate = (
            (self.successful_requests / self.total_requests * 100) 
            if self.total_requests > 0 else 0.0
        )
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate_percent": round(success_rate, 2),
            "total_tokens_used": self.total_tokens_used,
            "average_response_time_seconds": round(avg_response_time, 2),
            "model_used": self.config.model,
            "max_retries_configured": self.config.max_retries
        }
    
    def reset_statistics(self) -> None:
        """Reset all usage statistics."""
        self._reset_statistics()
        logger.info("Usage statistics reset")
    
    def health_check(self) -> bool:
        """
        Perform a simple health check to verify AI service connectivity.
        
        Returns:
            bool: True if service is accessible, False otherwise
        """
        try:
            response = self.generate_response(
                "Hello", 
                conversation_history=None
            )
            return response.success
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


if __name__ == "__main__":
    # Example usage and testing
    import sys
    import os
    
    # Add parent directory to path to import config
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from config.settings import AIConfig
        
        # Test configuration
        os.environ['OPENAI_API_KEY'] = 'test-key-demo'  # For testing only
        ai_config = AIConfig.from_environment()
        
        # Initialize client
        client = AIClient(ai_config)
        
        print("✓ AI Client initialized successfully")
        print(f"  Model: {ai_config.model}")
        print(f"  Max Tokens: {ai_config.max_tokens}")
        print(f"  Temperature: {ai_config.temperature}")
        
        # Display statistics
        stats = client.get_statistics()
        print("\\nInitial Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except ImportError:
        print("❌ Could not import configuration module")
    except Exception as e:
        print(f"❌ Error testing AI client: {e}")