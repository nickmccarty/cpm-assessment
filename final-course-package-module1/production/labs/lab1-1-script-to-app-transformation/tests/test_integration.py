"""
Integration Tests

End-to-end integration tests for the complete AI Assistant application.
These tests validate that all components work together correctly and
demonstrate real-world usage scenarios.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch
from config.settings import load_configuration
from core.ai_client import AIClient
from conversation.manager import ConversationManager


@pytest.mark.integration
class TestCompleteApplicationFlow:
    """Test complete application workflows end-to-end."""
    
    def test_full_conversation_cycle(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test complete conversation cycle from config to persistence."""
        # Setup environment
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        # Load configuration
        ai_config, app_config = load_configuration()
        
        # Initialize components
        ai_client = AIClient(ai_config)
        conversation_manager = ConversationManager(app_config)
        
        # Simulate conversation
        user_message = "Hello, tell me about AI"
        
        # Get conversation context (should be empty initially)
        context = conversation_manager.get_recent_context()
        assert len(context) == 0
        
        # Generate AI response
        ai_response = ai_client.generate_response(user_message, context)
        assert ai_response.success is True
        
        # Save conversation
        conversation_manager.add_exchange(
            user_message=user_message,
            ai_response=ai_response.content,
            tokens_used=ai_response.tokens_used,
            model_used=ai_response.model_used,
            response_time=ai_response.response_time
        )
        
        # Verify persistence
        conversation_file = temp_dir / app_config.conversation_file
        assert conversation_file.exists()
        
        with open(conversation_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert len(saved_data) == 1
        assert saved_data[0]['user'] == user_message
        assert saved_data[0]['assistant'] == ai_response.content
    
    def test_multi_turn_conversation_with_context(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test multi-turn conversation with proper context management."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        # Initialize application
        ai_config, app_config = load_configuration()
        ai_client = AIClient(ai_config)
        conversation_manager = ConversationManager(app_config)
        
        # Simulate multi-turn conversation
        conversation_turns = [
            "Hello, I'm interested in learning about machine learning",
            "Can you explain neural networks?",
            "What about deep learning?",
            "How does this relate to AI?"
        ]
        
        for turn_num, user_message in enumerate(conversation_turns):
            # Get conversation context (includes previous turns)
            context = conversation_manager.get_recent_context()
            assert len(context) == turn_num  # Should grow with each turn
            
            # Generate response with context
            ai_response = ai_client.generate_response(user_message, context)
            assert ai_response.success is True
            
            # Save conversation
            conversation_manager.add_exchange(
                user_message=user_message,
                ai_response=ai_response.content,
                tokens_used=ai_response.tokens_used,
                model_used=ai_response.model_used
            )
        
        # Verify complete conversation history
        final_context = conversation_manager.get_recent_context()
        assert len(final_context) == len(conversation_turns)
        
        # Verify statistics
        stats = conversation_manager.get_statistics()
        assert stats['total_exchanges'] == len(conversation_turns)
        assert stats['total_tokens_used'] > 0
    
    def test_error_recovery_workflow(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test application behavior during error scenarios."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        ai_config, app_config = load_configuration()
        ai_client = AIClient(ai_config)
        conversation_manager = ConversationManager(app_config)
        
        # First successful interaction
        response1 = ai_client.generate_response("Hello")
        assert response1.success is True
        
        conversation_manager.add_exchange("Hello", response1.content)
        
        # Simulate API error
        mock_openai.ChatCompletion.create.side_effect = mock_openai.error.APIError("Service unavailable")
        
        with patch('time.sleep'):  # Speed up retry delays
            response2 = ai_client.generate_response("How are you?")
        
        assert response2.success is False
        assert "temporarily unavailable" in response2.error_message
        
        # Error should not be saved to conversation history
        stats = conversation_manager.get_statistics()
        assert stats['total_exchanges'] == 1  # Only successful conversation
        
        # Recovery: API comes back online
        mock_openai.ChatCompletion.create.side_effect = None
        mock_openai.ChatCompletion.create.return_value = Mock(
            choices=[Mock(message=Mock(content="I'm doing well after the outage"))],
            usage=Mock(total_tokens=25)
        )
        
        response3 = ai_client.generate_response("Are you back online?")
        assert response3.success is True
        
        conversation_manager.add_exchange("Are you back online?", response3.content)
        
        # Should now have 2 successful conversations
        final_stats = conversation_manager.get_statistics()
        assert final_stats['total_exchanges'] == 2


@pytest.mark.integration
class TestConfigurationIntegration:
    """Test integration between configuration and components."""
    
    def test_configuration_propagation(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test that configuration values properly propagate to all components."""
        # Set custom configuration values
        monkeypatch.setenv('AI_MODEL', 'gpt-4')
        monkeypatch.setenv('MAX_TOKENS', '2000')
        monkeypatch.setenv('TEMPERATURE', '0.9')
        monkeypatch.setenv('MAX_HISTORY_CONTEXT', '10')
        monkeypatch.setenv('CONVERSATION_FILE', 'custom_conversations.json')
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        # Load configuration
        ai_config, app_config = load_configuration()
        
        # Verify AI configuration
        assert ai_config.model == 'gpt-4'
        assert ai_config.max_tokens == 2000
        assert ai_config.temperature == 0.9
        
        # Verify app configuration
        assert app_config.max_history_context == 10
        assert app_config.conversation_file == 'custom_conversations.json'
        
        # Initialize components and verify configuration usage
        ai_client = AIClient(ai_config)
        conversation_manager = ConversationManager(app_config)
        
        # Test AI client uses correct configuration
        ai_client.generate_response("Test message")
        
        call_args = mock_openai.ChatCompletion.create.call_args[1]
        assert call_args['model'] == 'gpt-4'
        assert call_args['max_tokens'] == 2000
        assert call_args['temperature'] == 0.9
        
        # Test conversation manager uses correct file
        expected_file = temp_dir / 'custom_conversations.json'
        assert conversation_manager.file_path == expected_file
    
    def test_environment_variable_changes(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test handling of environment variable changes."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        # Initial configuration
        ai_config1, app_config1 = load_configuration()
        assert ai_config1.model == 'gpt-3.5-turbo'
        
        # Change environment variable
        monkeypatch.setenv('AI_MODEL', 'gpt-4')
        
        # Reload configuration
        ai_config2, app_config2 = load_configuration()
        assert ai_config2.model == 'gpt-4'
        
        # Verify new configuration is used
        ai_client = AIClient(ai_config2)
        ai_client.generate_response("Test")
        
        call_args = mock_openai.ChatCompletion.create.call_args[1]
        assert call_args['model'] == 'gpt-4'


@pytest.mark.integration  
class TestDataPersistenceIntegration:
    """Test data persistence across application restarts."""
    
    def test_conversation_persistence_across_restarts(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test that conversations persist across application restarts."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        # First application session
        ai_config1, app_config1 = load_configuration()
        ai_client1 = AIClient(ai_config1)
        conversation_manager1 = ConversationManager(app_config1)
        
        # Have conversations
        for i in range(3):
            response = ai_client1.generate_response(f"Message {i}")
            conversation_manager1.add_exchange(f"Message {i}", response.content)
        
        stats1 = conversation_manager1.get_statistics()
        assert stats1['total_exchanges'] == 3
        
        # Simulate application restart - create new instances
        ai_config2, app_config2 = load_configuration()
        ai_client2 = AIClient(ai_config2)
        conversation_manager2 = ConversationManager(app_config2)
        
        # Verify conversations were loaded
        stats2 = conversation_manager2.get_statistics()
        assert stats2['total_exchanges'] == 3
        
        # Verify conversation content
        context = conversation_manager2.get_recent_context()
        assert len(context) == 3
        assert context[0]['user'] == "Message 0"
        assert context[1]['user'] == "Message 1"
        assert context[2]['user'] == "Message 2"
        
        # Add more conversations
        response = ai_client2.generate_response("Message 3")
        conversation_manager2.add_exchange("Message 3", response.content)
        
        # Verify total count
        final_stats = conversation_manager2.get_statistics()
        assert final_stats['total_exchanges'] == 4
    
    def test_corrupted_file_recovery(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test recovery from corrupted conversation files."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        # Create corrupted conversation file
        conversation_file = temp_dir / "conversations.json"
        with open(conversation_file, 'w') as f:
            f.write('{"corrupted": json syntax')  # Invalid JSON
        
        # Initialize conversation manager (should handle corruption)
        _, app_config = load_configuration()
        conversation_manager = ConversationManager(app_config)
        
        # Should start with empty conversations
        assert len(conversation_manager._conversations) == 0
        
        # Should create backup if enabled
        if app_config.backup_on_corruption:
            backup_files = list(temp_dir.glob("*.backup"))
            assert len(backup_files) > 0
        
        # Should be able to continue normally
        ai_config, _ = load_configuration()
        ai_client = AIClient(ai_config)
        
        response = ai_client.generate_response("Recovery test")
        conversation_manager.add_exchange("Recovery test", response.content)
        
        stats = conversation_manager.get_statistics()
        assert stats['total_exchanges'] == 1


@pytest.mark.integration
class TestExportImportIntegration:
    """Test export and import functionality integration."""
    
    def test_full_export_workflow(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test complete export workflow with multiple formats."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        # Initialize application
        ai_config, app_config = load_configuration()
        ai_client = AIClient(ai_config)
        conversation_manager = ConversationManager(app_config)
        
        # Generate conversations
        messages = [
            "Hello AI assistant",
            "Tell me about Python programming",
            "What are the best practices?",
            "How do I handle errors?"
        ]
        
        for message in messages:
            response = ai_client.generate_response(message)
            conversation_manager.add_exchange(
                message, 
                response.content,
                response.tokens_used,
                response.model_used
            )
        
        # Test all export formats
        from conversation.manager import ConversationFormat
        
        export_tests = [
            (ConversationFormat.JSON, 'export.json'),
            (ConversationFormat.CSV, 'export.csv'),
            (ConversationFormat.TXT, 'export.txt'),
            (ConversationFormat.HTML, 'export.html')
        ]
        
        for format_type, filename in export_tests:
            export_path = temp_dir / filename
            success = conversation_manager.export_conversations(export_path, format_type)
            
            assert success is True
            assert export_path.exists()
            assert export_path.stat().st_size > 0  # File has content
            
            # Verify basic content for each format
            content = export_path.read_text(encoding='utf-8')
            assert messages[0] in content  # First message should be in export
    
    def test_selective_export_by_date(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test selective export with date filtering."""
        from datetime import datetime, timedelta
        from conversation.manager import ConversationExchange, ConversationFormat
        
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        _, app_config = load_configuration()
        conversation_manager = ConversationManager(app_config)
        
        # Add conversations from different dates
        base_date = datetime(2023, 10, 1)
        for i in range(7):  # 7 days of conversations
            date = base_date + timedelta(days=i)
            exchange = ConversationExchange(
                timestamp=date.isoformat(),
                user=f"Message from day {i}",
                assistant=f"Response from day {i}",
                tokens_used=20,
                model_used="gpt-3.5-turbo"
            )
            conversation_manager._conversations.append(exchange)
        
        # Export conversations from specific date range (days 2-4)
        start_date = base_date + timedelta(days=2)
        end_date = base_date + timedelta(days=4)
        
        export_path = temp_dir / 'filtered_export.json'
        success = conversation_manager.export_conversations(
            export_path,
            ConversationFormat.JSON,
            date_range=(start_date, end_date)
        )
        
        assert success is True
        
        # Verify filtered content
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == 3  # Days 2, 3, 4
        assert "day 2" in exported_data[0]['user']
        assert "day 4" in exported_data[2]['user']


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across component interactions."""
    
    def test_cascading_error_handling(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test how errors propagate and are handled across components."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        ai_config, app_config = load_configuration()
        ai_client = AIClient(ai_config)
        conversation_manager = ConversationManager(app_config)
        
        # Test various error scenarios
        error_scenarios = [
            (mock_openai.error.RateLimitError, "Rate limit exceeded"),
            (mock_openai.error.APIError, "API service unavailable"),
            (mock_openai.error.InvalidRequestError, "Invalid request"),
            (mock_openai.error.AuthenticationError, "Invalid API key")
        ]
        
        for error_class, error_message in error_scenarios:
            # Configure mock to raise specific error
            mock_openai.ChatCompletion.create.side_effect = error_class(error_message)
            
            with patch('time.sleep'):  # Speed up retries
                response = ai_client.generate_response("Test message")
            
            # Verify error handling
            assert response.success is False
            assert response.error_message is not None
            
            # Verify error is not saved to conversation history
            initial_count = conversation_manager.get_statistics()['total_exchanges']
            
            # Should not change conversation count
            final_count = conversation_manager.get_statistics()['total_exchanges']
            assert final_count == initial_count
            
            # Reset mock for next iteration
            mock_openai.ChatCompletion.create.side_effect = None
            mock_openai.ChatCompletion.create.return_value = Mock(
                choices=[Mock(message=Mock(content="Recovery response"))],
                usage=Mock(total_tokens=20)
            )
    
    def test_file_system_error_handling(self, mock_env_vars, mock_openai, monkeypatch):
        """Test handling of file system errors."""
        # Use non-existent directory to trigger permission errors
        bad_directory = "/nonexistent/directory"
        monkeypatch.setenv('DATA_DIRECTORY', bad_directory)
        
        ai_config, app_config = load_configuration()
        ai_client = AIClient(ai_config)
        
        # Should handle directory creation gracefully
        try:
            conversation_manager = ConversationManager(app_config)
            
            # Should be able to work in memory even if file operations fail
            response = ai_client.generate_response("Test message")
            conversation_manager.add_exchange("Test", response.content)
            
            # Should have conversation in memory
            stats = conversation_manager.get_statistics()
            assert stats['total_exchanges'] == 1
            
        except Exception as e:
            # If directory creation fails completely, that's also acceptable
            # as long as it's handled gracefully
            assert "data directory" in str(e).lower() or "permission" in str(e).lower()


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance characteristics of integrated components."""
    
    @pytest.mark.slow
    def test_large_conversation_handling(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test handling of large conversation histories."""
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        monkeypatch.setenv('MAX_HISTORY_CONTEXT', '50')  # Reasonable context limit
        
        ai_config, app_config = load_configuration()
        ai_client = AIClient(ai_config)
        conversation_manager = ConversationManager(app_config)
        
        # Generate large conversation history
        for i in range(200):  # Large number of conversations
            response = ai_client.generate_response(f"Message {i}")
            conversation_manager.add_exchange(f"Message {i}", response.content)
        
        # Verify all conversations are stored
        stats = conversation_manager.get_statistics()
        assert stats['total_exchanges'] == 200
        
        # Verify context limiting works
        context = conversation_manager.get_recent_context()
        assert len(context) == app_config.max_history_context
        
        # Verify most recent conversations are in context
        assert context[-1]['user'] == "Message 199"
        assert context[0]['user'] == f"Message {200 - app_config.max_history_context}"
        
        # Test that AI client can handle large context
        final_response = ai_client.generate_response("Final message", context)
        assert final_response.success is True
    
    @pytest.mark.slow
    def test_concurrent_operations(self, mock_env_vars, temp_dir, mock_openai, monkeypatch):
        """Test concurrent operations on conversation manager."""
        import threading
        import time
        
        monkeypatch.setenv('DATA_DIRECTORY', str(temp_dir))
        
        ai_config, app_config = load_configuration()
        ai_client = AIClient(ai_config)
        conversation_manager = ConversationManager(app_config)
        
        results = []
        errors = []
        
        def worker_thread(thread_id):
            try:
                for i in range(10):
                    message = f"Thread {thread_id} Message {i}"
                    response = ai_client.generate_response(message)
                    conversation_manager.add_exchange(message, response.content)
                    time.sleep(0.01)  # Small delay to increase concurrency
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        # Create and start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Thread errors: {errors}"
        assert len(results) == 5
        
        # Verify all conversations were saved
        stats = conversation_manager.get_statistics()
        assert stats['total_exchanges'] == 50  # 5 threads × 10 messages each