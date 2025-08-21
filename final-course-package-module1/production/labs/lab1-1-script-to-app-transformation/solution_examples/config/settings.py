"""
Configuration Management Module

This module demonstrates professional configuration management practices
for AI applications, including secure environment variable handling,
validation, and flexible defaults.

Key improvements over the original script:
- Environment variables instead of hardcoded values
- Comprehensive validation with helpful error messages
- Type hints for better code documentation
- Dataclasses for clean configuration objects
- Separation of AI and application settings
"""

import os
from dataclasses import dataclass
from typing import Optional, Union
import json


@dataclass
class AIConfig:
    """
    Configuration settings for AI service integration.
    
    This class encapsulates all AI-related configuration with secure
    environment variable loading and sensible defaults.
    
    Attributes:
        api_key: OpenAI API key (required from environment)
        model: AI model to use for completions
        max_tokens: Maximum tokens per response
        temperature: Response creativity (0.0-2.0)
        system_prompt: Default system message for AI context
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts for failed requests
    """
    api_key: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    system_prompt: str = "You are a helpful AI assistant for a marketing consultant."
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_environment(cls) -> 'AIConfig':
        """
        Create configuration from environment variables with validation.
        
        Environment Variables:
            OPENAI_API_KEY (required): Your OpenAI API key
            AI_MODEL (optional): Model name (default: gpt-3.5-turbo)
            MAX_TOKENS (optional): Max tokens per response (default: 1000)
            TEMPERATURE (optional): Response temperature (default: 0.7)
            SYSTEM_PROMPT (optional): Default system prompt
            AI_TIMEOUT (optional): Request timeout seconds (default: 30)
            AI_MAX_RETRIES (optional): Max retry attempts (default: 3)
            
        Returns:
            AIConfig: Configured instance
            
        Raises:
            ValueError: If required environment variables are missing or invalid
        """
        # Required configuration
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required.\\n"
                "Set it with: export OPENAI_API_KEY='your-key-here'\\n"
                "Or create a .env file with: OPENAI_API_KEY=your-key-here"
            )
        
        # Validate API key format (basic check)
        if not api_key.startswith('sk-'):
            raise ValueError(
                "OPENAI_API_KEY appears to be invalid. "
                "OpenAI API keys typically start with 'sk-'"
            )
        
        # Optional configuration with validation
        try:
            max_tokens = int(os.getenv('MAX_TOKENS', '1000'))
            if max_tokens < 1 or max_tokens > 4096:
                raise ValueError("MAX_TOKENS must be between 1 and 4096")
                
            temperature = float(os.getenv('TEMPERATURE', '0.7'))
            if temperature < 0.0 or temperature > 2.0:
                raise ValueError("TEMPERATURE must be between 0.0 and 2.0")
                
            timeout = int(os.getenv('AI_TIMEOUT', '30'))
            if timeout < 1 or timeout > 300:
                raise ValueError("AI_TIMEOUT must be between 1 and 300 seconds")
                
            max_retries = int(os.getenv('AI_MAX_RETRIES', '3'))
            if max_retries < 0 or max_retries > 10:
                raise ValueError("AI_MAX_RETRIES must be between 0 and 10")
                
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(
                    f"Configuration error: {e}. "
                    "Check that numeric environment variables contain valid numbers."
                )
            raise
        
        return cls(
            api_key=api_key,
            model=os.getenv('AI_MODEL', 'gpt-3.5-turbo'),
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=os.getenv(
                'SYSTEM_PROMPT', 
                "You are a helpful AI assistant for a marketing consultant."
            ),
            timeout=timeout,
            max_retries=max_retries
        )
    
    def validate(self) -> None:
        """
        Validate configuration values after creation.
        
        Raises:
            ValueError: If any configuration values are invalid
        """
        if not self.api_key:
            raise ValueError("API key cannot be empty")
            
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be positive")
            
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
            
        if self.timeout < 1:
            raise ValueError("timeout must be positive")
            
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")


@dataclass
class AppConfig:
    """
    Application-level configuration settings.
    
    This class manages application behavior, file paths, and
    operational settings separate from AI service configuration.
    
    Attributes:
        conversation_file: Path to conversation history file
        max_history_context: Maximum conversation exchanges to include in context
        auto_save: Whether to automatically save conversations
        log_level: Logging level for application messages
        backup_on_corruption: Whether to backup corrupted files before replacement
        data_directory: Directory for application data files
    """
    conversation_file: str = "conversations.json"
    max_history_context: int = 20
    auto_save: bool = True
    log_level: str = "INFO"
    backup_on_corruption: bool = True
    data_directory: str = "."
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        """
        Create app configuration from environment variables.
        
        Environment Variables:
            CONVERSATION_FILE (optional): Path to conversation file
            MAX_HISTORY_CONTEXT (optional): Max conversation context
            AUTO_SAVE (optional): Enable auto-save (true/false)
            LOG_LEVEL (optional): Logging level (DEBUG/INFO/WARNING/ERROR)
            BACKUP_ON_CORRUPTION (optional): Backup corrupted files (true/false)
            DATA_DIRECTORY (optional): Directory for app data
            
        Returns:
            AppConfig: Configured instance
            
        Raises:
            ValueError: If configuration values are invalid
        """
        try:
            max_history = int(os.getenv('MAX_HISTORY_CONTEXT', '20'))
            if max_history < 0:
                raise ValueError("MAX_HISTORY_CONTEXT cannot be negative")
                
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(
                    "MAX_HISTORY_CONTEXT must be a valid integer"
                )
            raise
        
        # Parse boolean environment variables
        auto_save = os.getenv('AUTO_SAVE', 'true').lower() in ('true', '1', 'yes', 'on')
        backup_on_corruption = os.getenv('BACKUP_ON_CORRUPTION', 'true').lower() in ('true', '1', 'yes', 'on')
        
        # Validate log level
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if log_level not in valid_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of: {', '.join(valid_levels)}"
            )
        
        return cls(
            conversation_file=os.getenv('CONVERSATION_FILE', 'conversations.json'),
            max_history_context=max_history,
            auto_save=auto_save,
            log_level=log_level,
            backup_on_corruption=backup_on_corruption,
            data_directory=os.getenv('DATA_DIRECTORY', '.')
        )
    
    def get_full_conversation_path(self) -> str:
        """
        Get the full path to the conversation file.
        
        Returns:
            str: Full path combining data_directory and conversation_file
        """
        return os.path.join(self.data_directory, self.conversation_file)
    
    def validate(self) -> None:
        """
        Validate configuration values after creation.
        
        Raises:
            ValueError: If any configuration values are invalid
        """
        if self.max_history_context < 0:
            raise ValueError("max_history_context cannot be negative")
            
        if not self.conversation_file:
            raise ValueError("conversation_file cannot be empty")
            
        # Validate data directory exists or can be created
        if not os.path.exists(self.data_directory):
            try:
                os.makedirs(self.data_directory, exist_ok=True)
            except OSError as e:
                raise ValueError(f"Cannot create data directory {self.data_directory}: {e}")


def load_configuration() -> tuple[AIConfig, AppConfig]:
    """
    Load and validate both AI and application configurations.
    
    This is a convenience function that loads both configuration
    objects and validates them, providing a single point of
    configuration loading for the application.
    
    Returns:
        tuple[AIConfig, AppConfig]: Both configuration objects
        
    Raises:
        ValueError: If any configuration is invalid
    """
    try:
        ai_config = AIConfig.from_environment()
        ai_config.validate()
        
        app_config = AppConfig.from_environment()
        app_config.validate()
        
        return ai_config, app_config
        
    except ValueError as e:
        # Re-raise with additional context
        raise ValueError(f"Configuration error: {e}")


def print_configuration_help():
    """
    Print helpful information about configuration setup.
    
    This function provides users with clear guidance on how to
    set up their environment variables for the application.
    """
    help_text = """
🔧 AI Assistant Configuration Help

Required Environment Variables:
  OPENAI_API_KEY=your-api-key-here    # Your OpenAI API key (required)

Optional AI Configuration:
  AI_MODEL=gpt-3.5-turbo              # AI model to use
  MAX_TOKENS=1000                     # Maximum response length
  TEMPERATURE=0.7                     # Response creativity (0.0-2.0)
  AI_TIMEOUT=30                       # Request timeout in seconds
  AI_MAX_RETRIES=3                    # Maximum retry attempts

Optional App Configuration:
  CONVERSATION_FILE=conversations.json  # Conversation history file
  MAX_HISTORY_CONTEXT=20               # Max conversation context
  AUTO_SAVE=true                       # Auto-save conversations
  LOG_LEVEL=INFO                       # Logging level
  DATA_DIRECTORY=.                     # Directory for app data

Setup Examples:

Windows (Command Prompt):
  set OPENAI_API_KEY=your-key-here
  set AI_MODEL=gpt-4

Windows (PowerShell):
  $env:OPENAI_API_KEY="your-key-here"
  $env:AI_MODEL="gpt-4"

macOS/Linux:
  export OPENAI_API_KEY=your-key-here
  export AI_MODEL=gpt-4

.env file (place in application directory):
  OPENAI_API_KEY=your-key-here
  AI_MODEL=gpt-4
  MAX_TOKENS=1500
  TEMPERATURE=0.8
"""
    print(help_text)


if __name__ == "__main__":
    # Configuration testing and help
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        print_configuration_help()
        sys.exit(0)
    
    try:
        ai_config, app_config = load_configuration()
        print("✓ Configuration loaded successfully!")
        print(f"  AI Model: {ai_config.model}")
        print(f"  Max Tokens: {ai_config.max_tokens}")
        print(f"  Temperature: {ai_config.temperature}")
        print(f"  Conversation File: {app_config.get_full_conversation_path()}")
        print(f"  Auto-save: {app_config.auto_save}")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\\nRun 'python settings.py help' for configuration guidance.")
        sys.exit(1)