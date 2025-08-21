"""
Configuration Module Tests

Tests for the configuration management system, validating secure
environment variable handling, validation logic, and error scenarios.
This demonstrates professional configuration testing practices.
"""

import pytest
import os
from config.settings import AIConfig, AppConfig, load_configuration


class TestAIConfig:
    """Test cases for AI configuration management."""
    
    @pytest.mark.unit
    def test_ai_config_from_environment_success(self, mock_env_vars):
        """Test successful AI configuration loading from environment."""
        config = AIConfig.from_environment()
        
        assert config.api_key == 'sk-test1234567890abcdef1234567890abcdef123456'
        assert config.model == 'gpt-3.5-turbo'
        assert config.max_tokens == 1000
        assert config.temperature == 0.7
        assert config.timeout == 30
        assert config.max_retries == 3
        assert "marketing consultant" in config.system_prompt
    
    @pytest.mark.unit
    def test_ai_config_missing_api_key(self, monkeypatch):
        """Test configuration error when API key is missing."""
        # Remove API key from environment
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        
        with pytest.raises(ValueError) as exc_info:
            AIConfig.from_environment()
        
        assert "OPENAI_API_KEY environment variable is required" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_ai_config_invalid_api_key_format(self, monkeypatch):
        """Test configuration error for invalid API key format."""
        monkeypatch.setenv('OPENAI_API_KEY', 'invalid-key-format')
        
        with pytest.raises(ValueError) as exc_info:
            AIConfig.from_environment()
        
        assert "appears to be invalid" in str(exc_info.value)
        assert "start with 'sk-'" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_ai_config_custom_values(self, monkeypatch):
        """Test AI configuration with custom environment values."""
        monkeypatch.setenv('OPENAI_API_KEY', 'sk-custom1234567890abcdef1234567890abcdef123456')
        monkeypatch.setenv('AI_MODEL', 'gpt-4')
        monkeypatch.setenv('MAX_TOKENS', '2000')
        monkeypatch.setenv('TEMPERATURE', '0.9')
        monkeypatch.setenv('AI_TIMEOUT', '60')
        monkeypatch.setenv('AI_MAX_RETRIES', '5')
        monkeypatch.setenv('SYSTEM_PROMPT', 'Custom system prompt')
        
        config = AIConfig.from_environment()
        
        assert config.api_key == 'sk-custom1234567890abcdef1234567890abcdef123456'
        assert config.model == 'gpt-4'
        assert config.max_tokens == 2000
        assert config.temperature == 0.9
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.system_prompt == 'Custom system prompt'
    
    @pytest.mark.unit
    def test_ai_config_validation_errors(self, monkeypatch):
        """Test validation errors for invalid configuration values."""
        monkeypatch.setenv('OPENAI_API_KEY', 'sk-test1234567890abcdef1234567890abcdef123456')
        
        # Test invalid max_tokens
        monkeypatch.setenv('MAX_TOKENS', '0')
        with pytest.raises(ValueError) as exc_info:
            AIConfig.from_environment()
        assert "MAX_TOKENS must be between 1 and 4096" in str(exc_info.value)
        
        # Test invalid temperature
        monkeypatch.setenv('MAX_TOKENS', '1000')
        monkeypatch.setenv('TEMPERATURE', '3.0')
        with pytest.raises(ValueError) as exc_info:
            AIConfig.from_environment()
        assert "TEMPERATURE must be between 0.0 and 2.0" in str(exc_info.value)
        
        # Test invalid timeout
        monkeypatch.setenv('TEMPERATURE', '0.7')
        monkeypatch.setenv('AI_TIMEOUT', '0')
        with pytest.raises(ValueError) as exc_info:
            AIConfig.from_environment()
        assert "AI_TIMEOUT must be between 1 and 300" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_ai_config_invalid_numeric_values(self, monkeypatch):
        """Test handling of non-numeric values for numeric settings."""
        monkeypatch.setenv('OPENAI_API_KEY', 'sk-test1234567890abcdef1234567890abcdef123456')
        monkeypatch.setenv('MAX_TOKENS', 'not-a-number')
        
        with pytest.raises(ValueError) as exc_info:
            AIConfig.from_environment()
        
        assert "numeric environment variables contain valid numbers" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_ai_config_validate_method(self):
        """Test the validate method for AIConfig."""
        # Test valid configuration
        config = AIConfig(api_key='sk-test123')
        config.validate()  # Should not raise
        
        # Test invalid configurations
        invalid_configs = [
            AIConfig(api_key='', model='gpt-3.5-turbo'),  # Empty API key
            AIConfig(api_key='sk-test123', max_tokens=0),  # Invalid max_tokens
            AIConfig(api_key='sk-test123', temperature=3.0),  # Invalid temperature
            AIConfig(api_key='sk-test123', timeout=0),  # Invalid timeout
            AIConfig(api_key='sk-test123', max_retries=-1),  # Invalid max_retries
        ]
        
        for invalid_config in invalid_configs:
            with pytest.raises(ValueError):
                invalid_config.validate()


class TestAppConfig:
    """Test cases for application configuration management."""
    
    @pytest.mark.unit
    def test_app_config_from_environment_defaults(self, temp_dir, monkeypatch):
        """Test app configuration with default values."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        config = AppConfig.from_environment()
        
        assert config.conversation_file == 'conversations.json'
        assert config.max_history_context == 20
        assert config.auto_save is True
        assert config.log_level == 'INFO'
        assert config.backup_on_corruption is True
        assert config.data_directory == str(temp_dir)
    
    @pytest.mark.unit
    def test_app_config_custom_values(self, temp_dir, monkeypatch):
        """Test app configuration with custom environment values."""
        monkeypatch.setenv('CONVERSATION_FILE', 'custom_conversations.json')
        monkeypatch.setenv('MAX_HISTORY_CONTEXT', '50')
        monkeypatch.setenv('AUTO_SAVE', 'false')
        monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
        monkeypatch.setenv('BACKUP_ON_CORRUPTION', 'false')
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        config = AppConfig.from_environment()
        
        assert config.conversation_file == 'custom_conversations.json'
        assert config.max_history_context == 50
        assert config.auto_save is False
        assert config.log_level == 'DEBUG'
        assert config.backup_on_corruption is False
        assert config.data_directory == str(temp_dir)
    
    @pytest.mark.unit
    def test_app_config_boolean_parsing(self, monkeypatch):
        """Test boolean environment variable parsing."""
        test_cases = [
            ('true', True),
            ('True', True),
            ('1', True),
            ('yes', True),
            ('on', True),
            ('false', False),
            ('False', False),
            ('0', False),
            ('no', False),
            ('off', False),
            ('invalid', False),  # Default to False for invalid values
        ]
        
        for env_value, expected in test_cases:
            monkeypatch.setenv('AUTO_SAVE', env_value)
            config = AppConfig.from_environment()
            assert config.auto_save == expected, f"Failed for value: {env_value}"
    
    @pytest.mark.unit
    def test_app_config_invalid_numeric_values(self, monkeypatch):
        """Test handling of invalid numeric values."""
        monkeypatch.setenv('MAX_HISTORY_CONTEXT', 'not-a-number')
        
        with pytest.raises(ValueError) as exc_info:
            AppConfig.from_environment()
        
        assert "MAX_HISTORY_CONTEXT must be a valid integer" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_app_config_negative_history_context(self, monkeypatch):
        """Test validation of negative history context."""
        monkeypatch.setenv('MAX_HISTORY_CONTEXT', '-5')
        
        with pytest.raises(ValueError) as exc_info:
            AppConfig.from_environment()
        
        assert "MAX_HISTORY_CONTEXT cannot be negative" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_app_config_invalid_log_level(self, monkeypatch):
        """Test validation of invalid log levels."""
        monkeypatch.setenv('LOG_LEVEL', 'INVALID_LEVEL')
        
        with pytest.raises(ValueError) as exc_info:
            AppConfig.from_environment()
        
        assert "LOG_LEVEL must be one of" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_app_config_get_full_conversation_path(self, temp_dir):
        """Test getting full conversation file path."""
        config = AppConfig()
        config.data_directory = str(temp_dir)
        config.conversation_file = 'test_conversations.json'
        
        full_path = config.get_full_conversation_path()
        expected_path = str(temp_dir / 'test_conversations.json')
        
        assert full_path == expected_path
    
    @pytest.mark.unit
    def test_app_config_validate_method(self, temp_dir):
        """Test the validate method for AppConfig."""
        # Test valid configuration
        config = AppConfig()
        config.data_directory = str(temp_dir)
        config.validate()  # Should not raise
        
        # Test invalid configurations
        invalid_config = AppConfig()
        invalid_config.max_history_context = -1
        with pytest.raises(ValueError):
            invalid_config.validate()
        
        invalid_config = AppConfig()
        invalid_config.conversation_file = ''
        with pytest.raises(ValueError):
            invalid_config.validate()
    
    @pytest.mark.unit
    def test_app_config_data_directory_creation(self, temp_dir):
        """Test automatic creation of data directory."""
        new_dir = temp_dir / 'new_data_dir'
        assert not new_dir.exists()
        
        config = AppConfig()
        config.data_directory = str(new_dir)
        config.validate()
        
        assert new_dir.exists()


class TestConfigurationLoading:
    """Test cases for the main configuration loading function."""
    
    @pytest.mark.unit
    def test_load_configuration_success(self, mock_env_vars, temp_dir, monkeypatch):
        """Test successful loading of both configurations."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        ai_config, app_config = load_configuration()
        
        assert isinstance(ai_config, AIConfig)
        assert isinstance(app_config, AppConfig)
        assert ai_config.api_key == 'sk-test1234567890abcdef1234567890abcdef123456'
        assert app_config.auto_save is True
    
    @pytest.mark.unit
    def test_load_configuration_ai_error(self, monkeypatch):
        """Test configuration loading when AI config fails."""
        # Missing API key should cause AI config to fail
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        
        with pytest.raises(ValueError) as exc_info:
            load_configuration()
        
        assert "Configuration error" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_load_configuration_app_error(self, mock_env_vars, monkeypatch):
        """Test configuration loading when app config fails."""
        # Invalid log level should cause app config to fail
        monkeypatch.setenv('LOG_LEVEL', 'INVALID')
        
        with pytest.raises(ValueError) as exc_info:
            load_configuration()
        
        assert "Configuration error" in str(exc_info.value)


class TestConfigurationHelpers:
    """Test configuration helper functions."""
    
    @pytest.mark.unit
    def test_print_configuration_help(self, capsys):
        """Test the configuration help function."""
        from config.settings import print_configuration_help
        
        print_configuration_help()
        
        captured = capsys.readouterr()
        assert "AI Assistant Configuration Help" in captured.out
        assert "OPENAI_API_KEY" in captured.out
        assert "Required Environment Variables" in captured.out
        assert "Setup Examples" in captured.out


class TestEnvironmentVariableHandling:
    """Test edge cases in environment variable handling."""
    
    @pytest.mark.unit
    def test_missing_optional_variables(self, monkeypatch):
        """Test handling when optional environment variables are missing."""
        # Set only required variable
        monkeypatch.setenv('OPENAI_API_KEY', 'sk-test1234567890abcdef1234567890abcdef123456')
        
        # Clear all optional variables
        optional_vars = [
            'AI_MODEL', 'MAX_TOKENS', 'TEMPERATURE', 'AI_TIMEOUT', 
            'AI_MAX_RETRIES', 'SYSTEM_PROMPT', 'CONVERSATION_FILE',
            'MAX_HISTORY_CONTEXT', 'AUTO_SAVE', 'LOG_LEVEL'
        ]
        
        for var in optional_vars:
            monkeypatch.delenv(var, raising=False)
        
        # Should work with defaults
        ai_config = AIConfig.from_environment()
        app_config = AppConfig.from_environment()
        
        assert ai_config.model == 'gpt-3.5-turbo'  # Default value
        assert app_config.max_history_context == 20  # Default value
    
    @pytest.mark.unit
    def test_whitespace_in_environment_variables(self, monkeypatch):
        """Test handling of whitespace in environment variables."""
        monkeypatch.setenv('OPENAI_API_KEY', '  sk-test1234567890abcdef1234567890abcdef123456  ')
        monkeypatch.setenv('AI_MODEL', '  gpt-4  ')
        
        config = AIConfig.from_environment()
        
        # Should handle whitespace correctly
        assert config.api_key == '  sk-test1234567890abcdef1234567890abcdef123456  '
        assert config.model == '  gpt-4  '
    
    @pytest.mark.unit
    def test_case_sensitivity(self, monkeypatch):
        """Test case sensitivity in environment variable values."""
        monkeypatch.setenv('OPENAI_API_KEY', 'sk-test1234567890abcdef1234567890abcdef123456')
        monkeypatch.setenv('AUTO_SAVE', 'TRUE')  # Uppercase
        monkeypatch.setenv('LOG_LEVEL', 'debug')  # Lowercase
        
        ai_config = AIConfig.from_environment()
        app_config = AppConfig.from_environment()
        
        assert app_config.auto_save is True  # Should handle uppercase
        assert app_config.log_level == 'DEBUG'  # Should convert to uppercase


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration with other components."""
    
    def test_configuration_with_ai_client(self, mock_env_vars, mock_openai):
        """Test that configuration works properly with AI client."""
        ai_config = AIConfig.from_environment()
        
        # Should be able to create AI client with config
        from core.ai_client import AIClient
        client = AIClient(ai_config)
        
        assert client.config == ai_config
        assert client.call_count == 0
    
    def test_configuration_with_conversation_manager(self, mock_env_vars, temp_dir, monkeypatch):
        """Test that configuration works properly with conversation manager."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        app_config = AppConfig.from_environment()
        
        # Should be able to create conversation manager with config
        from conversation.manager import ConversationManager
        manager = ConversationManager(app_config)
        
        assert manager.config == app_config
        assert manager.file_path.parent == temp_dir