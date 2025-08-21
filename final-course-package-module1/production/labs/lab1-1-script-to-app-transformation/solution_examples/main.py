"""
AI Assistant Main Application

This is the main entry point for Sarah's professional AI Assistant application.
It demonstrates clean application architecture with proper error handling,
configuration management, and user interaction patterns.

Key improvements over the original script:
- Clean separation of concerns with modular architecture
- Comprehensive error handling and user feedback
- Professional configuration management with environment variables
- Intuitive command system with help and validation
- Graceful startup and shutdown procedures
- Logging and debugging capabilities
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from config.settings import load_configuration, print_configuration_help
from core.ai_client import AIClient
from conversation.manager import ConversationManager


# Configure application logging
def setup_logging(log_level: str = "INFO") -> None:
    """Setup application logging with appropriate formatting."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ai_assistant.log', encoding='utf-8')
        ]
    )


class AIAssistant:
    """
    Main AI Assistant application class.
    
    This class orchestrates all components and provides the main
    user interface for the AI assistant. It demonstrates professional
    application architecture with clean separation of concerns.
    """
    
    def __init__(self, ai_config, app_config):
        """
        Initialize AI Assistant with configuration.
        
        Args:
            ai_config: AIConfig object with AI service settings
            app_config: AppConfig object with application settings
        """
        self.ai_config = ai_config
        self.app_config = app_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        try:
            self.ai_client = AIClient(ai_config)
            self.conversation_manager = ConversationManager(app_config)
            
            self.logger.info("AI Assistant initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Assistant: {e}")
            raise
    
    def run(self) -> None:
        """
        Main application run loop with comprehensive error handling.
        """
        self._print_welcome()
        
        try:
            self._main_interaction_loop()
        except KeyboardInterrupt:
            self._handle_graceful_shutdown()
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            print(f"\\n❌ An unexpected error occurred: {e}")
            print("Please check the log file for more details.")
    
    def _print_welcome(self) -> None:
        """Print welcome message and system information."""
        print("🤖 Sarah's AI Assistant v2.0 - Professional Edition")
        print("=" * 55)
        print(f"✓ AI Model: {self.ai_config.model}")
        print(f"✓ Max Tokens: {self.ai_config.max_tokens}")
        print(f"✓ Temperature: {self.ai_config.temperature}")
        print(f"✓ Conversation File: {self.app_config.get_full_conversation_path()}")
        print(f"✓ Auto-save: {'Enabled' if self.app_config.auto_save else 'Disabled'}")
        
        # Show conversation statistics
        stats = self.conversation_manager.get_statistics()
        if stats['total_exchanges'] > 0:
            print(f"✓ Previous conversations: {stats['total_exchanges']} exchanges")
        
        print("\\nType /help for commands, or just start chatting!")
        print("Type /quit, /exit, or press Ctrl+C to exit")
        print("-" * 55)
    
    def _main_interaction_loop(self) -> None:
        """
        Main interaction loop handling user input and responses.
        """
        while True:
            try:
                # Get user input
                user_input = input("\\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if self._is_exit_command(user_input):
                    self._handle_graceful_shutdown()
                    break
                
                # Process command or chat message
                if self._is_command(user_input):
                    response = self._execute_command(user_input)
                    print(f"\\n🤖 {response}")
                else:
                    response = self._process_chat_message(user_input)
                    print(f"\\n🤖 AI: {response}")
                
            except KeyboardInterrupt:
                raise  # Re-raise to be handled by outer try/catch
            except Exception as e:
                self.logger.error(f"Error in interaction loop: {e}")
                print(f"\\n❌ An error occurred: {e}")
                print("Please try again or type /help for assistance.")
    
    def _process_chat_message(self, user_message: str) -> str:
        """
        Process a regular chat message through the AI service.
        
        Args:
            user_message: User's input message
            
        Returns:
            str: AI response or error message
        """
        try:
            # Get conversation context
            context = self.conversation_manager.get_recent_context()
            
            # Generate AI response
            ai_response = self.ai_client.generate_response(user_message, context)
            
            if ai_response.success:
                # Save successful conversation with metadata
                self.conversation_manager.add_exchange(
                    user_message=user_message,
                    ai_response=ai_response.content,
                    tokens_used=ai_response.tokens_used,
                    model_used=ai_response.model_used,
                    response_time=ai_response.response_time,
                    metadata={
                        "attempt_count": ai_response.attempt_count,
                        "error_type": ai_response.error_type.value if ai_response.error_type else None
                    }
                )
                
                self.logger.debug(f"Chat response generated: {ai_response.tokens_used} tokens, "
                                f"{ai_response.response_time:.2f}s")
                
                return ai_response.content
            else:
                self.logger.warning(f"AI response failed: {ai_response.error_message}")
                return f"Sorry, I encountered an error: {ai_response.error_message}"
                
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
            return "I'm having technical difficulties. Please try again in a moment."
    
    def _execute_command(self, command: str) -> str:
        """
        Execute special commands.
        
        Args:
            command: Command string starting with '/'
            
        Returns:
            str: Command result message
        """
        command = command.strip().lower()
        
        try:
            if command == '/help':
                return self._get_help_text()
            
            elif command == '/clear':
                success = self.conversation_manager.clear_history()
                if success:
                    return "✓ Conversation history cleared successfully."
                else:
                    return "❌ Failed to clear conversation history."
            
            elif command == '/stats':
                return self._get_statistics_text()
            
            elif command.startswith('/save '):
                filename = command[6:].strip()
                return self._save_conversation(filename)
            
            elif command.startswith('/export '):
                return self._handle_export_command(command)
            
            elif command.startswith('/search '):
                query = command[8:].strip()
                return self._search_conversations(query)
            
            elif command == '/config':
                return self._get_configuration_info()
            
            elif command == '/health':
                return self._check_system_health()
            
            else:
                return f"❌ Unknown command: {command}\\nType /help for available commands."
                
        except Exception as e:
            self.logger.error(f"Error executing command {command}: {e}")
            return f"❌ Error executing command: {e}"
    
    def _get_help_text(self) -> str:
        """Get comprehensive help text."""
        return """🤖 AI Assistant Commands:

Basic Commands:
  /help           - Show this help message
  /quit, /exit    - Exit the assistant
  /clear          - Clear conversation history
  /stats          - Show usage statistics

File Operations:
  /save <filename>     - Save conversation to specific file
  /export json <file>  - Export to JSON format
  /export csv <file>   - Export to CSV format
  /export txt <file>   - Export to plain text
  /export html <file>  - Export to HTML format

Search & Information:
  /search <query>      - Search conversation history
  /config              - Show current configuration
  /health              - Check system health status

Tips:
  • Just type your message to chat with the AI
  • Use quotes for filenames with spaces: /save "my file.json"
  • All conversations are automatically saved
  • Use Ctrl+C to exit gracefully"""
    
    def _get_statistics_text(self) -> str:
        """Get comprehensive statistics display."""
        ai_stats = self.ai_client.get_statistics()
        conv_stats = self.conversation_manager.get_statistics()
        
        return f"""📊 AI Assistant Statistics:

AI Service:
  • Total requests: {ai_stats['total_requests']}
  • Successful requests: {ai_stats['successful_requests']}
  • Failed requests: {ai_stats['failed_requests']}
  • Success rate: {ai_stats['success_rate_percent']}%
  • Total tokens used: {ai_stats['total_tokens_used']:,}
  • Average response time: {ai_stats['average_response_time_seconds']}s
  • Model: {ai_stats['model_used']}

Conversations:
  • Total exchanges: {conv_stats['total_exchanges']}
  • First conversation: {conv_stats.get('first_conversation', 'None')}
  • Last conversation: {conv_stats.get('last_conversation', 'None')}
  • Average user message length: {conv_stats.get('average_user_length', 0)} chars
  • Average AI response length: {conv_stats.get('average_assistant_length', 0)} chars
  • File: {conv_stats.get('file_path', 'None')}"""
    
    def _save_conversation(self, filename: str) -> str:
        """
        Save conversation to specified file.
        
        Args:
            filename: Target filename
            
        Returns:
            str: Result message
        """
        if not filename:
            return "❌ Please specify a filename: /save filename.json"
        
        try:
            # Add .json extension if not present
            if not filename.endswith('.json'):
                filename += '.json'
            
            success = self.conversation_manager.export_conversations(filename)
            if success:
                return f"✓ Conversation saved to {filename}"
            else:
                return f"❌ Failed to save conversation to {filename}"
                
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            return f"❌ Error saving file: {e}"
    
    def _handle_export_command(self, command: str) -> str:
        """
        Handle export commands with format specification.
        
        Args:
            command: Full export command
            
        Returns:
            str: Result message
        """
        parts = command.split()
        if len(parts) < 3:
            return "❌ Usage: /export <format> <filename>\\nFormats: json, csv, txt, html"
        
        format_type = parts[1].lower()
        filename = ' '.join(parts[2:])
        
        try:
            from conversation.manager import ConversationFormat
            
            format_map = {
                'json': ConversationFormat.JSON,
                'csv': ConversationFormat.CSV,
                'txt': ConversationFormat.TXT,
                'html': ConversationFormat.HTML
            }
            
            if format_type not in format_map:
                return "❌ Unsupported format. Use: json, csv, txt, or html"
            
            success = self.conversation_manager.export_conversations(
                filename, 
                format_map[format_type]
            )
            
            if success:
                return f"✓ Conversation exported to {filename} ({format_type.upper()})"
            else:
                return f"❌ Failed to export conversation"
                
        except Exception as e:
            self.logger.error(f"Error exporting conversation: {e}")
            return f"❌ Export error: {e}"
    
    def _search_conversations(self, query: str) -> str:
        """
        Search conversation history.
        
        Args:
            query: Search query
            
        Returns:
            str: Search results
        """
        if not query:
            return "❌ Please provide a search query: /search your query"
        
        try:
            results = self.conversation_manager.search_conversations(query, limit=5)
            
            if not results:
                return f"🔍 No conversations found containing '{query}'"
            
            response = f"🔍 Found {len(results)} conversation(s) containing '{query}':\\n\\n"
            
            for i, exchange in enumerate(results, 1):
                # Truncate long messages for display
                user_preview = (exchange.user[:100] + "...") if len(exchange.user) > 100 else exchange.user
                assistant_preview = (exchange.assistant[:100] + "...") if len(exchange.assistant) > 100 else exchange.assistant
                
                response += f"{i}. {exchange.timestamp}\\n"
                response += f"   User: {user_preview}\\n"
                response += f"   AI: {assistant_preview}\\n\\n"
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error searching conversations: {e}")
            return f"❌ Search error: {e}"
    
    def _get_configuration_info(self) -> str:
        """Get current configuration information."""
        return f"""⚙️ Current Configuration:

AI Settings:
  • Model: {self.ai_config.model}
  • Max Tokens: {self.ai_config.max_tokens}
  • Temperature: {self.ai_config.temperature}
  • Timeout: {self.ai_config.timeout}s
  • Max Retries: {self.ai_config.max_retries}

Application Settings:
  • Conversation File: {self.app_config.get_full_conversation_path()}
  • Max History Context: {self.app_config.max_history_context}
  • Auto-save: {self.app_config.auto_save}
  • Log Level: {self.app_config.log_level}
  • Data Directory: {self.app_config.data_directory}"""
    
    def _check_system_health(self) -> str:
        """Check system health and connectivity."""
        try:
            # Check AI client health
            ai_healthy = self.ai_client.health_check()
            
            # Check conversation manager
            conv_stats = self.conversation_manager.get_statistics()
            conv_healthy = True  # If we can get stats, it's working
            
            # Check file system
            file_path = Path(self.app_config.get_full_conversation_path())
            file_accessible = file_path.parent.exists() and os.access(file_path.parent, os.W_OK)
            
            health_status = "✓ Healthy" if ai_healthy else "❌ Issues detected"
            
            return f"""🏥 System Health Check:

AI Service: {'✓ Connected' if ai_healthy else '❌ Connection issues'}
Conversation Manager: {'✓ Operational' if conv_healthy else '❌ Issues detected'}
File System: {'✓ Accessible' if file_accessible else '❌ Permission issues'}

Overall Status: {health_status}

{f'Total conversations: {conv_stats["total_exchanges"]}' if conv_stats else 'No conversation data'}"""
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return f"❌ Health check failed: {e}"
    
    def _is_command(self, user_input: str) -> bool:
        """Check if user input is a command."""
        return user_input.strip().startswith('/')
    
    def _is_exit_command(self, user_input: str) -> bool:
        """Check if user input is an exit command."""
        exit_commands = ['/quit', '/exit', 'quit', 'exit', 'bye']
        return user_input.strip().lower() in exit_commands
    
    def _handle_graceful_shutdown(self) -> None:
        """Handle graceful application shutdown."""
        print("\\n\\n👋 Thank you for using Sarah's AI Assistant!")
        
        # Display final statistics
        stats = self.ai_client.get_statistics()
        if stats['total_requests'] > 0:
            print(f"📊 Session summary: {stats['total_requests']} requests, "
                  f"{stats['total_tokens_used']:,} tokens used")
        
        print("💾 Your conversations have been automatically saved.")
        print("Have a great day!")
        
        self.logger.info("AI Assistant shutdown gracefully")


def main():
    """
    Main application entry point with comprehensive error handling.
    """
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            print_configuration_help()
            return
        elif sys.argv[1] == '--version':
            print("Sarah's AI Assistant v2.0 - Professional Edition")
            return
    
    try:
        # Load configuration
        ai_config, app_config = load_configuration()
        
        # Setup logging
        setup_logging(app_config.log_level)
        logger = logging.getLogger(__name__)
        logger.info("Starting AI Assistant application")
        
        # Initialize and run assistant
        assistant = AIAssistant(ai_config, app_config)
        assistant.run()
        
    except ValueError as e:
        print(f"\\n❌ Configuration Error: {e}")
        print("\\nRun 'python main.py --help' for configuration guidance.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\\n❌ Failed to start AI Assistant: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()