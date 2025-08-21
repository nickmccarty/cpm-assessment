"""
Conversation Manager Tests

Tests for the conversation management system, validating data persistence,
file operations, search functionality, and export capabilities.
This demonstrates professional testing of data management components.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, mock_open
from conversation.manager import (
    ConversationManager, 
    ConversationExchange, 
    ConversationFormat
)


class TestConversationExchange:
    """Test cases for ConversationExchange data structure."""
    
    @pytest.mark.unit
    def test_conversation_exchange_creation(self):
        """Test creating ConversationExchange objects."""
        timestamp = datetime.now().isoformat()
        exchange = ConversationExchange(
            timestamp=timestamp,
            user="Hello AI",
            assistant="Hello user",
            tokens_used=25,
            model_used="gpt-3.5-turbo",
            response_time=1.5,
            metadata={"test": "value"}
        )
        
        assert exchange.timestamp == timestamp
        assert exchange.user == "Hello AI"
        assert exchange.assistant == "Hello user"
        assert exchange.tokens_used == 25
        assert exchange.model_used == "gpt-3.5-turbo"
        assert exchange.response_time == 1.5
        assert exchange.metadata == {"test": "value"}
    
    @pytest.mark.unit
    def test_conversation_exchange_from_dict(self):
        """Test creating ConversationExchange from dictionary."""
        data = {
            "timestamp": "2023-10-01T10:00:00",
            "user": "Test user message",
            "assistant": "Test AI response",
            "tokens_used": 30,
            "model_used": "gpt-4",
            "response_time": 2.0
        }
        
        exchange = ConversationExchange.from_dict(data)
        
        assert exchange.timestamp == "2023-10-01T10:00:00"
        assert exchange.user == "Test user message"
        assert exchange.assistant == "Test AI response"
        assert exchange.tokens_used == 30
        assert exchange.model_used == "gpt-4"
        assert exchange.response_time == 2.0
    
    @pytest.mark.unit
    def test_conversation_exchange_to_dict(self):
        """Test converting ConversationExchange to dictionary."""
        exchange = ConversationExchange(
            timestamp="2023-10-01T10:00:00",
            user="Test message",
            assistant="Test response"
        )
        
        result = exchange.to_dict()
        
        assert isinstance(result, dict)
        assert result['timestamp'] == "2023-10-01T10:00:00"
        assert result['user'] == "Test message"
        assert result['assistant'] == "Test response"
        assert result['tokens_used'] == 0  # Default value
    
    @pytest.mark.unit
    def test_conversation_exchange_to_openai_format(self):
        """Test converting to OpenAI API format."""
        exchange = ConversationExchange(
            timestamp="2023-10-01T10:00:00",
            user="User message",
            assistant="AI response"
        )
        
        result = exchange.to_openai_format()
        
        expected = [
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "AI response"}
        ]
        assert result == expected


class TestConversationManager:
    """Test cases for ConversationManager functionality."""
    
    @pytest.mark.unit
    def test_conversation_manager_initialization(self, app_config, temp_dir):
        """Test conversation manager initialization."""
        manager = ConversationManager(app_config)
        
        assert manager.config == app_config
        assert manager.file_path.name == app_config.conversation_file
        assert isinstance(manager._conversations, list)
        assert len(manager._conversations) == 0
    
    @pytest.mark.unit
    def test_conversation_manager_with_existing_file(self, app_config, conversation_file):
        """Test loading existing conversation file."""
        app_config.conversation_file = conversation_file.name
        app_config.data_directory = str(conversation_file.parent)
        
        manager = ConversationManager(app_config)
        
        assert len(manager._conversations) == 3  # From sample_conversations fixture
        assert manager._conversations[0].user == "Hello, how are you?"
    
    @pytest.mark.unit
    def test_add_exchange(self, conversation_manager):
        """Test adding conversation exchanges."""
        manager = conversation_manager
        initial_count = len(manager._conversations)
        
        manager.add_exchange(
            user_message="Test user message",
            ai_response="Test AI response",
            tokens_used=25,
            model_used="gpt-3.5-turbo",
            response_time=1.2
        )
        
        assert len(manager._conversations) == initial_count + 1
        
        last_exchange = manager._conversations[-1]
        assert last_exchange.user == "Test user message"
        assert last_exchange.assistant == "Test AI response"
        assert last_exchange.tokens_used == 25
        assert last_exchange.model_used == "gpt-3.5-turbo"
        assert last_exchange.response_time == 1.2
        assert last_exchange.timestamp is not None
    
    @pytest.mark.unit
    def test_add_exchange_with_empty_content(self, conversation_manager):
        """Test adding exchange with empty content."""
        manager = conversation_manager
        initial_count = len(manager._conversations)
        
        # Should not add exchanges with empty content
        manager.add_exchange("", "Test response")
        manager.add_exchange("Test message", "")
        manager.add_exchange("   ", "Test response")  # Whitespace only
        
        assert len(manager._conversations) == initial_count
    
    @pytest.mark.unit
    def test_get_recent_context(self, conversation_manager, sample_conversations):
        """Test getting recent conversation context."""
        manager = conversation_manager
        
        # Add sample conversations
        for conv in sample_conversations:
            manager.add_exchange(
                conv['user'], 
                conv['assistant'],
                conv['tokens_used'],
                conv['model_used'],
                conv['response_time']
            )
        
        # Test getting all context
        context = manager.get_recent_context()
        assert len(context) <= manager.config.max_history_context
        
        # Test limiting context
        limited_context = manager.get_recent_context(max_exchanges=2)
        assert len(limited_context) == 2
        
        # Verify format
        for exchange in context:
            assert 'user' in exchange
            assert 'assistant' in exchange
            assert 'timestamp' in exchange
    
    @pytest.mark.unit
    def test_get_openai_context(self, conversation_manager, sample_conversations):
        """Test getting context in OpenAI format."""
        manager = conversation_manager
        
        # Add sample conversations
        for conv in sample_conversations:
            manager.add_exchange(conv['user'], conv['assistant'])
        
        context = manager.get_openai_context(max_exchanges=2)
        
        # Should return messages in OpenAI format
        assert len(context) == 4  # 2 exchanges = 4 messages (user + assistant pairs)
        
        for i in range(0, len(context), 2):
            assert context[i]['role'] == 'user'
            assert context[i + 1]['role'] == 'assistant'
    
    @pytest.mark.unit
    def test_clear_history(self, conversation_manager, sample_conversations):
        """Test clearing conversation history."""
        manager = conversation_manager
        
        # Add some conversations
        for conv in sample_conversations:
            manager.add_exchange(conv['user'], conv['assistant'])
        
        assert len(manager._conversations) > 0
        
        result = manager.clear_history(create_backup=False)
        
        assert result is True
        assert len(manager._conversations) == 0
    
    @pytest.mark.unit
    def test_search_conversations(self, conversation_manager, sample_conversations):
        """Test searching conversations."""
        manager = conversation_manager
        
        # Add sample conversations
        for conv in sample_conversations:
            manager.add_exchange(conv['user'], conv['assistant'])
        
        # Search in user messages
        results = manager.search_conversations("hello", search_assistant=False)
        assert len(results) == 1
        assert "Hello, how are you?" in results[0].user
        
        # Search in assistant messages
        results = manager.search_conversations("weather", search_user=False)
        assert len(results) == 1
        assert "weather" in results[0].assistant
        
        # Case insensitive search
        results = manager.search_conversations("HELLO", case_sensitive=False)
        assert len(results) == 1
        
        # Case sensitive search
        results = manager.search_conversations("HELLO", case_sensitive=True)
        assert len(results) == 0
    
    @pytest.mark.unit
    def test_filter_by_date(self, conversation_manager):
        """Test filtering conversations by date."""
        manager = conversation_manager
        
        # Add conversations with different timestamps
        base_time = datetime(2023, 10, 1, 10, 0, 0)
        for i in range(5):
            timestamp = (base_time + timedelta(hours=i)).isoformat()
            exchange = ConversationExchange(
                timestamp=timestamp,
                user=f"Message {i}",
                assistant=f"Response {i}"
            )
            manager._conversations.append(exchange)
        
        # Filter by date range
        start_date = datetime(2023, 10, 1, 11, 0, 0)
        end_date = datetime(2023, 10, 1, 13, 0, 0)
        
        results = manager.filter_by_date(start_date, end_date)
        
        assert len(results) == 3  # Hours 11, 12, 13
        assert all("Message" in result.user for result in results)


class TestConversationManagerFileOperations:
    """Test cases for file operations and error handling."""
    
    @pytest.mark.unit
    def test_load_nonexistent_file(self, app_config, temp_dir):
        """Test loading when conversation file doesn't exist."""
        app_config.data_directory = str(temp_dir)
        app_config.conversation_file = "nonexistent.json"
        
        manager = ConversationManager(app_config)
        
        assert len(manager._conversations) == 0
    
    @pytest.mark.unit
    def test_load_corrupted_file(self, app_config, corrupted_conversation_file):
        """Test handling of corrupted conversation files."""
        app_config.conversation_file = corrupted_conversation_file.name
        app_config.data_directory = str(corrupted_conversation_file.parent)
        
        manager = ConversationManager(app_config)
        
        # Should handle corruption gracefully
        assert len(manager._conversations) == 0
        
        # Should create backup if backup_on_corruption is enabled
        if app_config.backup_on_corruption:
            backup_files = list(corrupted_conversation_file.parent.glob("*.backup"))
            assert len(backup_files) > 0
    
    @pytest.mark.unit
    def test_load_invalid_format_file(self, app_config, temp_dir):
        """Test handling of invalid format conversation files."""
        # Create file with wrong format (dict instead of list)
        invalid_file = temp_dir / "invalid_format.json"
        with open(invalid_file, 'w') as f:
            json.dump({"invalid": "format"}, f)
        
        app_config.conversation_file = invalid_file.name
        app_config.data_directory = str(temp_dir)
        
        manager = ConversationManager(app_config)
        
        assert len(manager._conversations) == 0
    
    @pytest.mark.unit
    def test_save_conversations_auto_save_enabled(self, temp_dir):
        """Test automatic saving when auto_save is enabled."""
        from config.settings import AppConfig
        
        app_config = AppConfig()
        app_config.data_directory = str(temp_dir)
        app_config.conversation_file = "test_auto_save.json"
        app_config.auto_save = True
        
        manager = ConversationManager(app_config)
        
        # Add exchange (should trigger auto-save)
        manager.add_exchange("Test message", "Test response")
        
        # Check that file was created
        conversation_file = temp_dir / "test_auto_save.json"
        assert conversation_file.exists()
        
        # Verify content
        with open(conversation_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]['user'] == "Test message"
    
    @pytest.mark.unit
    def test_save_conversations_auto_save_disabled(self, temp_dir):
        """Test no automatic saving when auto_save is disabled."""
        from config.settings import AppConfig
        
        app_config = AppConfig()
        app_config.data_directory = str(temp_dir)
        app_config.conversation_file = "test_no_auto_save.json"
        app_config.auto_save = False
        
        manager = ConversationManager(app_config)
        
        # Add exchange (should not trigger auto-save)
        manager.add_exchange("Test message", "Test response")
        
        # Check that file was not created
        conversation_file = temp_dir / "test_no_auto_save.json"
        assert not conversation_file.exists()
    
    @pytest.mark.unit
    def test_save_with_permission_error(self, conversation_manager, monkeypatch):
        """Test handling of file permission errors during save."""
        # Mock open to raise permission error
        mock_file_open = mock_open()
        mock_file_open.side_effect = PermissionError("Permission denied")
        
        monkeypatch.setattr('builtins.open', mock_file_open)
        
        # Should handle permission error gracefully
        conversation_manager.add_exchange("Test", "Response")
        # Should not raise exception, just log warning
    
    @pytest.mark.unit
    def test_atomic_write_operation(self, conversation_manager, temp_dir):
        """Test atomic write operations for data safety."""
        manager = conversation_manager
        manager.add_exchange("Test message", "Test response")
        
        # Check that temporary file is not left behind
        temp_files = list(temp_dir.glob("*.tmp"))
        assert len(temp_files) == 0


class TestConversationExport:
    """Test cases for conversation export functionality."""
    
    @pytest.mark.unit
    def test_export_to_json(self, conversation_manager, sample_conversations, temp_dir):
        """Test exporting conversations to JSON format."""
        manager = conversation_manager
        
        # Add sample conversations
        for conv in sample_conversations:
            manager.add_exchange(conv['user'], conv['assistant'])
        
        export_file = temp_dir / "export_test.json"
        result = manager.export_conversations(export_file, ConversationFormat.JSON)
        
        assert result is True
        assert export_file.exists()
        
        # Verify exported content
        with open(export_file, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == len(sample_conversations)
        assert exported_data[0]['user'] == sample_conversations[0]['user']
    
    @pytest.mark.unit
    def test_export_to_csv(self, conversation_manager, sample_conversations, temp_dir):
        """Test exporting conversations to CSV format."""
        manager = conversation_manager
        
        # Add sample conversations
        for conv in sample_conversations:
            manager.add_exchange(conv['user'], conv['assistant'])
        
        export_file = temp_dir / "export_test.csv"
        result = manager.export_conversations(export_file, ConversationFormat.CSV)
        
        assert result is True
        assert export_file.exists()
        
        # Verify CSV content
        import csv
        with open(export_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == len(sample_conversations) + 1  # +1 for header
        assert 'Timestamp' in rows[0]  # Check header
    
    @pytest.mark.unit
    def test_export_to_txt(self, conversation_manager, sample_conversations, temp_dir):
        """Test exporting conversations to text format."""
        manager = conversation_manager
        
        # Add sample conversations
        for conv in sample_conversations:
            manager.add_exchange(conv['user'], conv['assistant'])
        
        export_file = temp_dir / "export_test.txt"
        result = manager.export_conversations(export_file, ConversationFormat.TXT)
        
        assert result is True
        assert export_file.exists()
        
        # Verify text content
        with open(export_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Conversation History Export" in content
        assert sample_conversations[0]['user'] in content
        assert sample_conversations[0]['assistant'] in content
    
    @pytest.mark.unit
    def test_export_to_html(self, conversation_manager, sample_conversations, temp_dir):
        """Test exporting conversations to HTML format."""
        manager = conversation_manager
        
        # Add sample conversations
        for conv in sample_conversations:
            manager.add_exchange(conv['user'], conv['assistant'])
        
        export_file = temp_dir / "export_test.html"
        result = manager.export_conversations(export_file, ConversationFormat.HTML)
        
        assert result is True
        assert export_file.exists()
        
        # Verify HTML content
        with open(export_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "<!DOCTYPE html>" in content
        assert "<title>Conversation History</title>" in content
        assert sample_conversations[0]['user'] in content
        assert sample_conversations[0]['assistant'] in content
    
    @pytest.mark.unit
    def test_export_with_date_range(self, conversation_manager, temp_dir):
        """Test exporting conversations with date filtering."""
        manager = conversation_manager
        
        # Add conversations with different dates
        base_time = datetime(2023, 10, 1)
        for i in range(5):
            timestamp = (base_time + timedelta(days=i)).isoformat()
            exchange = ConversationExchange(
                timestamp=timestamp,
                user=f"Message {i}",
                assistant=f"Response {i}"
            )
            manager._conversations.append(exchange)
        
        # Export with date range
        start_date = datetime(2023, 10, 2)
        end_date = datetime(2023, 10, 4)
        
        export_file = temp_dir / "filtered_export.json"
        result = manager.export_conversations(
            export_file, 
            ConversationFormat.JSON,
            date_range=(start_date, end_date)
        )
        
        assert result is True
        
        # Verify filtered content
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == 3  # Days 2, 3, 4
    
    @pytest.mark.unit
    def test_export_empty_conversations(self, conversation_manager, temp_dir):
        """Test exporting when no conversations exist."""
        manager = conversation_manager
        
        export_file = temp_dir / "empty_export.json"
        result = manager.export_conversations(export_file, ConversationFormat.JSON)
        
        assert result is False  # Should return False for empty export
        assert not export_file.exists()
    
    @pytest.mark.unit
    def test_export_unsupported_format(self, conversation_manager, sample_conversations, temp_dir):
        """Test exporting with unsupported format."""
        manager = conversation_manager
        
        # Add sample conversation
        manager.add_exchange("Test", "Response")
        
        export_file = temp_dir / "test_export.xml"
        
        with pytest.raises(ValueError) as exc_info:
            manager.export_conversations(export_file, "unsupported_format")
        
        assert "Unsupported export format" in str(exc_info.value)


class TestConversationStatistics:
    """Test cases for conversation statistics."""
    
    @pytest.mark.unit
    def test_statistics_empty(self, conversation_manager):
        """Test statistics when no conversations exist."""
        stats = conversation_manager.get_statistics()
        
        assert stats['total_exchanges'] == 0
        assert stats['first_conversation'] is None
        assert stats['last_conversation'] is None
        assert stats['total_user_chars'] == 0
        assert stats['total_assistant_chars'] == 0
        assert stats['average_user_length'] == 0
        assert stats['average_assistant_length'] == 0
        assert stats['total_tokens_used'] == 0
        assert stats['unique_models_used'] == 0
    
    @pytest.mark.unit
    def test_statistics_with_conversations(self, conversation_manager, sample_conversations):
        """Test statistics calculation with conversations."""
        manager = conversation_manager
        
        # Add sample conversations
        for conv in sample_conversations:
            manager.add_exchange(
                conv['user'], 
                conv['assistant'],
                conv['tokens_used'],
                conv['model_used']
            )
        
        stats = manager.get_statistics()
        
        assert stats['total_exchanges'] == len(sample_conversations)
        assert stats['first_conversation'] is not None
        assert stats['last_conversation'] is not None
        assert stats['total_user_chars'] > 0
        assert stats['total_assistant_chars'] > 0
        assert stats['average_user_length'] > 0
        assert stats['average_assistant_length'] > 0
        assert stats['total_tokens_used'] == sum(conv['tokens_used'] for conv in sample_conversations)
        assert stats['unique_models_used'] == 1  # All use same model
    
    @pytest.mark.unit
    def test_statistics_multiple_models(self, conversation_manager):
        """Test statistics with multiple AI models."""
        manager = conversation_manager
        
        # Add conversations with different models
        models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-3.5-turbo', 'claude-v1']
        for i, model in enumerate(models):
            manager.add_exchange(f"Message {i}", f"Response {i}", model_used=model)
        
        stats = manager.get_statistics()
        
        assert stats['unique_models_used'] == 3  # gpt-3.5-turbo, gpt-4, claude-v1


class TestConversationOptimization:
    """Test cases for conversation storage optimization."""
    
    @pytest.mark.unit
    def test_optimize_storage(self, conversation_manager):
        """Test storage optimization to remove old conversations."""
        manager = conversation_manager
        
        # Add many conversations
        for i in range(100):
            manager.add_exchange(f"Message {i}", f"Response {i}")
        
        assert len(manager._conversations) == 100
        
        # Optimize to keep only 50
        removed_count = manager.optimize_storage(max_exchanges=50)
        
        assert removed_count == 50
        assert len(manager._conversations) == 50
        
        # Should keep the most recent ones
        assert manager._conversations[0].user == "Message 50"
        assert manager._conversations[-1].user == "Message 99"
    
    @pytest.mark.unit
    def test_optimize_storage_no_optimization_needed(self, conversation_manager):
        """Test optimization when no optimization is needed."""
        manager = conversation_manager
        
        # Add few conversations
        for i in range(5):
            manager.add_exchange(f"Message {i}", f"Response {i}")
        
        removed_count = manager.optimize_storage(max_exchanges=10)
        
        assert removed_count == 0
        assert len(manager._conversations) == 5


@pytest.mark.integration
class TestConversationManagerIntegration:
    """Integration tests for conversation manager with other components."""
    
    def test_conversation_manager_with_ai_client(self, conversation_manager, ai_client, mock_openai):
        """Test integration between conversation manager and AI client."""
        # Generate AI response
        ai_response = ai_client.generate_response("Hello AI")
        
        # Add to conversation manager
        conversation_manager.add_exchange(
            user_message="Hello AI",
            ai_response=ai_response.content,
            tokens_used=ai_response.tokens_used,
            model_used=ai_response.model_used,
            response_time=ai_response.response_time
        )
        
        # Verify integration
        recent_context = conversation_manager.get_recent_context()
        assert len(recent_context) == 1
        assert recent_context[0]['user'] == "Hello AI"
        assert recent_context[0]['assistant'] == ai_response.content
    
    def test_full_conversation_flow(self, conversation_manager, ai_client, mock_openai):
        """Test complete conversation flow with context management."""
        messages = [
            "Hello, how are you?",
            "What can you help me with?",
            "Tell me about AI"
        ]
        
        for message in messages:
            # Get conversation context
            context = conversation_manager.get_recent_context()
            
            # Generate AI response with context
            ai_response = ai_client.generate_response(message, context)
            
            # Add to conversation history
            conversation_manager.add_exchange(
                user_message=message,
                ai_response=ai_response.content,
                tokens_used=ai_response.tokens_used,
                model_used=ai_response.model_used
            )
        
        # Verify complete conversation
        stats = conversation_manager.get_statistics()
        assert stats['total_exchanges'] == 3
        
        final_context = conversation_manager.get_recent_context()
        assert len(final_context) == 3
        assert final_context[0]['user'] == messages[0]
        assert final_context[-1]['user'] == messages[-1]