"""
Configuration management for Personal AI Assistant.
Handles loading from environment variables, config files, and defaults.
"""

import os
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


@dataclass
class AIConfig:
    """AI service configuration."""
    provider: str = AIProvider.OPENAI.value
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30
    max_retries: int = 3
    system_prompt: str = "You are a helpful AI assistant for productivity and collaboration."
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        if self.max_tokens < 1:
            raise ValueError("Max tokens must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")


@dataclass
class AppConfig:
    """Application-level configuration."""
    data_dir: str = "~/.ai-assistant"
    conversation_file: str = "conversations.json"
    user_profiles_file: str = "profiles.json"
    analytics_file: str = "analytics.json"
    log_level: str = "INFO"
    log_file: str = "assistant.log"
    auto_save: bool = True
    max_history_context: int = 20
    backup_interval_hours: int = 24
    
    def __post_init__(self):
        """Expand paths and create directories."""
        self.data_dir = str(Path(self.data_dir).expanduser())
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class WebConfig:
    """Web interface configuration."""
    host: str = "127.0.0.1"
    port: int = 7860
    share: bool = False
    debug: bool = False
    auth: Optional[tuple] = None
    theme: str = "soft"
    title: str = "Personal AI Assistant"
    favicon_path: Optional[str] = None
    custom_css: Optional[str] = None
    
    def __post_init__(self):
        """Validate web configuration."""
        if not 1024 <= self.port <= 65535:
            raise ValueError("Port must be between 1024 and 65535")


@dataclass
class CLIConfig:
    """CLI interface configuration."""
    default_output_format: str = "text"
    color_output: bool = True
    verbose: bool = False
    prompt_style: str = "default"
    history_size: int = 1000


@dataclass
class Settings:
    """Complete application settings."""
    ai: AIConfig = field(default_factory=AIConfig)
    app: AppConfig = field(default_factory=AppConfig)
    web: WebConfig = field(default_factory=WebConfig)
    cli: CLIConfig = field(default_factory=CLIConfig)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Settings':
        """Load settings from configuration file."""
        path = Path(config_path)
        if not path.exists():
            return cls()
        
        config = configparser.ConfigParser()
        config.read(path)
        
        settings_dict = {}
        
        # Parse each section
        for section_name in config.sections():
            section_dict = {}
            for key, value in config[section_name].items():
                section_dict[key] = _convert_config_value(value)
            settings_dict[section_name] = section_dict
        
        return cls(**settings_dict)
    
    @classmethod
    def from_environment(cls) -> 'Settings':
        """Load settings from environment variables."""
        # TODO: Implement environment variable loading
        # Students will implement this method
        pass
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Settings':
        """
        Load settings with proper precedence:
        1. Default values
        2. Configuration file
        3. Environment variables
        4. Command line arguments (handled separately)
        """
        # Start with defaults
        settings = cls()
        
        # Override with config file if provided
        if config_path:
            file_settings = cls.from_file(config_path)
            settings = _merge_settings(settings, file_settings)
        
        # Override with environment variables
        env_settings = cls.from_environment()
        if env_settings:
            settings = _merge_settings(settings, env_settings)
        
        return settings
    
    def save(self, config_path: str) -> bool:
        """Save settings to configuration file."""
        try:
            config = configparser.ConfigParser()
            
            # Convert dataclasses to config sections
            config.add_section('ai')
            for key, value in asdict(self.ai).items():
                config.set('ai', key, str(value))
            
            config.add_section('app')
            for key, value in asdict(self.app).items():
                config.set('app', key, str(value))
            
            config.add_section('web')
            for key, value in asdict(self.web).items():
                if value is not None:
                    config.set('web', key, str(value))
            
            config.add_section('cli')
            for key, value in asdict(self.cli).items():
                config.set('cli', key, str(value))
            
            # Write to file
            with open(config_path, 'w') as f:
                config.write(f)
            
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def validate(self) -> List[str]:
        """Validate all configuration settings."""
        issues = []
        
        # Validate AI configuration
        if not self.ai.api_key:
            issues.append("AI API key is required")
        
        if self.ai.provider not in [p.value for p in AIProvider]:
            issues.append(f"Unsupported AI provider: {self.ai.provider}")
        
        # Validate paths
        try:
            Path(self.app.data_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create data directory: {e}")
        
        return issues


def _convert_config_value(value: str) -> Any:
    """Convert string configuration value to appropriate Python type."""
    # Boolean values
    if value.lower() in ('true', 'yes', '1', 'on'):
        return True
    elif value.lower() in ('false', 'no', '0', 'off'):
        return False
    
    # None values
    if value.lower() in ('none', 'null', ''):
        return None
    
    # Numeric values
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass
    
    # String value (default)
    return value


def _merge_settings(base: Settings, override: Settings) -> Settings:
    """Merge two settings objects, with override taking precedence."""
    # TODO: Implement deep merge of settings
    # Students will implement this method
    return override


# Environment variable mappings for student implementation
ENV_MAPPINGS = {
    'AI_ASSISTANT_API_KEY': ('ai', 'api_key'),
    'AI_ASSISTANT_PROVIDER': ('ai', 'provider'),
    'AI_ASSISTANT_MODEL': ('ai', 'model'),
    'AI_ASSISTANT_TEMPERATURE': ('ai', 'temperature'),
    'AI_ASSISTANT_MAX_TOKENS': ('ai', 'max_tokens'),
    'AI_ASSISTANT_SYSTEM_PROMPT': ('ai', 'system_prompt'),
    'AI_ASSISTANT_DATA_DIR': ('app', 'data_dir'),
    'AI_ASSISTANT_LOG_LEVEL': ('app', 'log_level'),
    'AI_ASSISTANT_AUTO_SAVE': ('app', 'auto_save'),
    'AI_ASSISTANT_WEB_HOST': ('web', 'host'),
    'AI_ASSISTANT_WEB_PORT': ('web', 'port'),
    'AI_ASSISTANT_WEB_SHARE': ('web', 'share'),
    'AI_ASSISTANT_CLI_VERBOSE': ('cli', 'verbose'),
    'AI_ASSISTANT_CLI_COLOR': ('cli', 'color_output'),
}


if __name__ == "__main__":
    # Test configuration loading
    settings = Settings.load()
    print("Configuration loaded successfully!")
    print(f"AI Provider: {settings.ai.provider}")
    print(f"Data Directory: {settings.app.data_dir}")
    
    # Validate configuration
    issues = settings.validate()
    if issues:
        print("Configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration is valid!")