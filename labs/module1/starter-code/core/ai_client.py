"""
AI client for managing interactions with various AI providers.
Provides unified interface with error handling, retries, and fallbacks.
"""

import time
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncGenerator, Union
from dataclasses import dataclass
from enum import Enum
import json

# Students will need to install these packages
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None


class ResponseStatus(Enum):
    """Response status indicators."""
    SUCCESS = "success"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"


@dataclass
class AIResponse:
    """Structured AI response with metadata."""
    content: str
    status: ResponseStatus
    provider: str
    model: str
    tokens_used: int = 0
    response_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def success(self) -> bool:
        """Check if response was successful."""
        return self.status == ResponseStatus.SUCCESS
    
    def to_dict(self) -> Dict:
        """Convert response to dictionary for serialization."""
        return {
            'content': self.content,
            'status': self.status.value,
            'provider': self.provider,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'response_time': self.response_time,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate_response(self, 
                               messages: List[Dict[str, str]], 
                               **kwargs) -> AIResponse:
        """Generate response from AI provider."""
        pass
    
    @abstractmethod
    async def stream_response(self, 
                             messages: List[Dict[str, str]], 
                             **kwargs) -> AsyncGenerator[str, None]:
        """Stream response from AI provider."""
        pass
    
    @abstractmethod
    def validate_config(self) -> List[str]:
        """Validate provider configuration."""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(api_key, model, **kwargs)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 1000)
        self.timeout = kwargs.get('timeout', 30)
    
    async def generate_response(self, 
                               messages: List[Dict[str, str]], 
                               **kwargs) -> AIResponse:
        """Generate response from OpenAI."""
        start_time = time.time()
        
        try:
            # Override default parameters with any provided kwargs
            params = {
                'model': self.model,
                'messages': messages,
                'temperature': kwargs.get('temperature', self.temperature),
                'max_tokens': kwargs.get('max_tokens', self.max_tokens),
                'timeout': kwargs.get('timeout', self.timeout)
            }
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                **params
            )
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=response.choices[0].message.content,
                status=ResponseStatus.SUCCESS,
                provider="openai",
                model=self.model,
                tokens_used=response.usage.total_tokens,
                response_time=response_time,
                metadata={'finish_reason': response.choices[0].finish_reason}
            )
            
        except openai.RateLimitError as e:
            self.logger.warning(f"OpenAI rate limit exceeded: {e}")
            return AIResponse(
                content="",
                status=ResponseStatus.RATE_LIMITED,
                provider="openai",
                model=self.model,
                response_time=time.time() - start_time,
                error_message="Rate limit exceeded. Please try again later."
            )
        
        except openai.APITimeoutError as e:
            self.logger.error(f"OpenAI timeout: {e}")
            return AIResponse(
                content="",
                status=ResponseStatus.TIMEOUT,
                provider="openai",
                model=self.model,
                response_time=time.time() - start_time,
                error_message="Request timed out. Please try again."
            )
        
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return AIResponse(
                content="",
                status=ResponseStatus.PROVIDER_ERROR,
                provider="openai",
                model=self.model,
                response_time=time.time() - start_time,
                error_message=f"AI service error: {str(e)}"
            )
    
    async def stream_response(self, 
                             messages: List[Dict[str, str]], 
                             **kwargs) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI."""
        try:
            params = {
                'model': self.model,
                'messages': messages,
                'temperature': kwargs.get('temperature', self.temperature),
                'max_tokens': kwargs.get('max_tokens', self.max_tokens),
                'stream': True
            }
            
            stream = await asyncio.to_thread(
                self.client.chat.completions.create,
                **params
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"OpenAI streaming error: {e}")
            yield f"[Streaming Error: {str(e)}]"
    
    def validate_config(self) -> List[str]:
        """Validate OpenAI configuration."""
        issues = []
        
        if not self.api_key or not self.api_key.startswith('sk-'):
            issues.append("Invalid OpenAI API key format")
        
        if self.model not in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']:
            issues.append(f"Unsupported OpenAI model: {self.model}")
        
        return issues


class AnthropicProvider(BaseAIProvider):
    """Anthropic (Claude) API provider implementation."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, model, **kwargs)
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not available. Install with: pip install anthropic")
        
        # TODO: Students implement Anthropic integration
        # This is a placeholder for students to complete
        pass
    
    async def generate_response(self, 
                               messages: List[Dict[str, str]], 
                               **kwargs) -> AIResponse:
        """Generate response from Anthropic."""
        # TODO: Students implement this method
        pass
    
    async def stream_response(self, 
                             messages: List[Dict[str, str]], 
                             **kwargs) -> AsyncGenerator[str, None]:
        """Stream response from Anthropic."""
        # TODO: Students implement this method
        pass
    
    def validate_config(self) -> List[str]:
        """Validate Anthropic configuration."""
        # TODO: Students implement this method
        return []


class AIClient:
    """
    High-level AI client with provider management, fallbacks, and retries.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.providers = []
        self.current_provider_index = 0
        self.call_count = 0
        self.total_tokens_used = 0
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers based on configuration."""
        provider_type = self.config.ai.provider.lower()
        
        if provider_type == "openai" and OPENAI_AVAILABLE:
            provider = OpenAIProvider(
                api_key=self.config.ai.api_key,
                model=self.config.ai.model,
                temperature=self.config.ai.temperature,
                max_tokens=self.config.ai.max_tokens,
                timeout=self.config.ai.timeout
            )
            self.providers.append(provider)
        
        # TODO: Students add other providers
        # elif provider_type == "anthropic" and ANTHROPIC_AVAILABLE:
        #     provider = AnthropicProvider(...)
        #     self.providers.append(provider)
        
        if not self.providers:
            raise ValueError(f"No available providers for type: {provider_type}")
    
    async def generate_response(self, 
                               user_message: str, 
                               conversation_history: Optional[List[Dict]] = None,
                               system_prompt: Optional[str] = None,
                               **kwargs) -> AIResponse:
        """
        Generate response with automatic retries and fallbacks.
        
        Args:
            user_message: The user's input message
            conversation_history: Previous conversation context
            system_prompt: Custom system prompt (overrides config)
            **kwargs: Additional parameters for AI providers
        
        Returns:
            AIResponse object with result and metadata
        """
        messages = self._build_messages(user_message, conversation_history, system_prompt)
        
        last_response = None
        max_retries = self.config.ai.max_retries
        
        for attempt in range(max_retries):
            try:
                # Try current provider
                provider = self.providers[self.current_provider_index]
                response = await provider.generate_response(messages, **kwargs)
                
                if response.success:
                    self.call_count += 1
                    self.total_tokens_used += response.tokens_used
                    return response
                
                # If rate limited, wait and retry
                if response.status == ResponseStatus.RATE_LIMITED:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.info(f"Rate limited, waiting {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                
                # For other errors, try fallback provider if available
                if len(self.providers) > 1:
                    self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
                    self.logger.info(f"Switching to fallback provider: {self.providers[self.current_provider_index].__class__.__name__}")
                
                last_response = response
                
            except Exception as e:
                self.logger.error(f"Unexpected error in attempt {attempt + 1}: {e}")
                last_response = AIResponse(
                    content="",
                    status=ResponseStatus.ERROR,
                    provider="unknown",
                    model="unknown",
                    error_message=f"Unexpected error: {str(e)}"
                )
        
        # All retries exhausted
        return last_response or AIResponse(
            content="",
            status=ResponseStatus.ERROR,
            provider="unknown",
            model="unknown",
            error_message="All retry attempts exhausted"
        )
    
    async def stream_response(self, 
                             user_message: str, 
                             conversation_history: Optional[List[Dict]] = None,
                             system_prompt: Optional[str] = None,
                             **kwargs) -> AsyncGenerator[str, None]:
        """Stream response with fallback handling."""
        messages = self._build_messages(user_message, conversation_history, system_prompt)
        
        try:
            provider = self.providers[self.current_provider_index]
            async for chunk in provider.stream_response(messages, **kwargs):
                yield chunk
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            yield f"[Streaming Error: {str(e)}]"
    
    def _build_messages(self, 
                       user_message: str, 
                       conversation_history: Optional[List[Dict]] = None,
                       system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """Build properly formatted message list for AI providers."""
        messages = []
        
        # Add system message
        system_content = system_prompt or self.config.ai.system_prompt
        if system_content:
            messages.append({"role": "system", "content": system_content})
        
        # Add conversation history
        if conversation_history:
            # Limit history to configured maximum
            max_history = self.config.app.max_history_context
            recent_history = conversation_history[-max_history:] if len(conversation_history) > max_history else conversation_history
            
            for exchange in recent_history:
                if "user" in exchange and "assistant" in exchange:
                    messages.append({"role": "user", "content": exchange["user"]})
                    messages.append({"role": "assistant", "content": exchange["assistant"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def get_stats(self) -> Dict[str, Union[int, float, str]]:
        """Get usage statistics."""
        current_provider = self.providers[self.current_provider_index] if self.providers else None
        
        return {
            "total_calls": self.call_count,
            "total_tokens_used": self.total_tokens_used,
            "current_provider": current_provider.__class__.__name__ if current_provider else "None",
            "current_model": current_provider.model if current_provider else "Unknown",
            "available_providers": len(self.providers)
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate AI client configuration."""
        issues = []
        
        if not self.providers:
            issues.append("No AI providers available")
        
        for provider in self.providers:
            provider_issues = provider.validate_config()
            issues.extend(provider_issues)
        
        return issues


# TODO: Students implement the following features:
# 1. Cost tracking and budgeting
# 2. Response caching to avoid duplicate API calls
# 3. Advanced prompt templates and chaining
# 4. Batch processing capabilities
# 5. Performance analytics and optimization


if __name__ == "__main__":
    # Example usage (students can run this to test)
    import asyncio
    from config.settings import Settings
    
    async def test_ai_client():
        # This requires proper API key configuration
        settings = Settings.load()
        
        if not settings.ai.api_key:
            print("Please set AI_ASSISTANT_API_KEY environment variable")
            return
        
        client = AIClient(settings)
        
        response = await client.generate_response("Hello, how are you?")
        print(f"Response: {response.content}")
        print(f"Status: {response.status}")
        print(f"Provider: {response.provider}")
        print(f"Tokens: {response.tokens_used}")
        
        stats = client.get_stats()
        print(f"Stats: {stats}")
    
    # Uncomment to test (requires API key)
    # asyncio.run(test_ai_client())