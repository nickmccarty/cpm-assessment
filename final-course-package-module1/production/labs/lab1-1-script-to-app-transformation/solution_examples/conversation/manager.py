"""
Conversation Management Module

This module handles all conversation history persistence with comprehensive
error handling, data validation, and backup strategies. It demonstrates
professional data management practices for AI applications.

Key improvements over the original script:
- Robust file operations with automatic backup
- Data validation and corruption recovery
- Flexible export/import capabilities
- Conversation search and filtering
- Memory-efficient handling of large histories
- Thread-safe operations for concurrent access
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Iterator
from pathlib import Path
import threading
import shutil
from dataclasses import dataclass, asdict
from enum import Enum
import logging


# Configure module logger
logger = logging.getLogger(__name__)


class ConversationFormat(Enum):
    """Supported conversation export formats."""
    JSON = "json"
    CSV = "csv"
    TXT = "txt"
    HTML = "html"


@dataclass
class ConversationExchange:
    """
    Structured representation of a conversation exchange.
    
    Attributes:
        timestamp: ISO format timestamp of the exchange
        user: User's message content
        assistant: AI assistant's response
        tokens_used: Number of tokens consumed (if available)
        model_used: AI model that generated the response
        response_time: Time taken for response generation
        metadata: Additional context or debugging information
    """
    timestamp: str
    user: str
    assistant: str
    tokens_used: int = 0
    model_used: str = ""
    response_time: float = 0.0
    metadata: Optional[Dict] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationExchange':
        """Create ConversationExchange from dictionary data."""
        return cls(
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            user=data.get('user', ''),
            assistant=data.get('assistant', ''),
            tokens_used=data.get('tokens_used', 0),
            model_used=data.get('model_used', ''),
            response_time=data.get('response_time', 0.0),
            metadata=data.get('metadata')
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    def to_openai_format(self) -> List[Dict[str, str]]:
        """Convert to OpenAI API message format."""
        return [
            {"role": "user", "content": self.user},
            {"role": "assistant", "content": self.assistant}
        ]


class ConversationManager:
    """
    Professional conversation history manager with robust file operations.
    
    This class provides comprehensive conversation management including:
    - Safe file operations with automatic backup
    - Data validation and corruption recovery
    - Conversation search and filtering
    - Multiple export formats
    - Memory-efficient handling of large histories
    - Thread-safe operations
    """
    
    def __init__(self, config):
        """
        Initialize conversation manager with configuration.
        
        Args:
            config: AppConfig object with file paths and settings
        """
        self.config = config
        self.file_path = Path(config.get_full_conversation_path())
        self._conversations: List[ConversationExchange] = []
        self._lock = threading.Lock()  # Thread safety
        
        # Ensure data directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing conversations
        self._load_conversations()
        
        logger.info(f"Conversation manager initialized: {len(self._conversations)} conversations loaded")
    
    def _load_conversations(self) -> None:
        """
        Load existing conversations from file with comprehensive error handling.
        """
        if not self.file_path.exists():
            logger.info("No existing conversation file found, starting fresh")
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate and convert data structure
            if isinstance(data, list):
                self._conversations = [
                    ConversationExchange.from_dict(item) 
                    for item in data
                ]
                logger.info(f"Loaded {len(self._conversations)} conversations successfully")
            else:
                logger.warning("Invalid conversation file format, starting fresh")
                self._create_backup("invalid_format")
                self._conversations = []
                
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted conversation file: {e}")
            self._handle_corrupted_file("json_decode_error")
            
        except Exception as e:
            logger.error(f"Unexpected error loading conversations: {e}")
            self._handle_corrupted_file("unexpected_error")
    
    def _handle_corrupted_file(self, error_type: str) -> None:
        """
        Handle corrupted conversation files with backup and recovery.
        
        Args:
            error_type: Type of corruption for backup naming
        """
        if self.config.backup_on_corruption:
            backup_created = self._create_backup(f"corrupted_{error_type}")
            if backup_created:
                logger.info("Corrupted file backed up, starting with fresh conversation history")
            else:
                logger.warning("Could not create backup of corrupted file")
        
        self._conversations = []
    
    def _create_backup(self, suffix: str) -> bool:
        """
        Create backup of current conversation file.
        
        Args:
            suffix: Suffix for backup filename
            
        Returns:
            bool: True if backup created successfully
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.file_path.with_suffix(f'.{suffix}_{timestamp}.backup')
            shutil.copy2(self.file_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def add_exchange(self, 
                    user_message: str, 
                    ai_response: str,
                    tokens_used: int = 0,
                    model_used: str = "",
                    response_time: float = 0.0,
                    metadata: Optional[Dict] = None) -> None:
        """
        Add a conversation exchange to history with validation.
        
        Args:
            user_message: User's input message
            ai_response: AI assistant's response
            tokens_used: Number of tokens consumed
            model_used: AI model that generated the response
            response_time: Time taken for response generation
            metadata: Additional context information
        """
        if not user_message.strip() or not ai_response.strip():
            logger.warning("Attempted to add exchange with empty message content")
            return
        
        exchange = ConversationExchange(
            timestamp=datetime.now().isoformat(),
            user=user_message.strip(),
            assistant=ai_response.strip(),
            tokens_used=tokens_used,
            model_used=model_used,
            response_time=response_time,
            metadata=metadata
        )
        
        with self._lock:
            self._conversations.append(exchange)
            
            if self.config.auto_save:
                self._save_conversations()
        
        logger.debug(f"Added conversation exchange: {len(user_message)} chars user, "
                    f"{len(ai_response)} chars assistant")
    
    def get_recent_context(self, 
                          max_exchanges: Optional[int] = None,
                          include_metadata: bool = False) -> List[Dict]:
        """
        Get recent conversation context for AI requests.
        
        Args:
            max_exchanges: Maximum number of exchanges to return
            include_metadata: Whether to include metadata in response
            
        Returns:
            List[Dict]: Recent conversation exchanges in API format
        """
        limit = max_exchanges or self.config.max_history_context
        
        with self._lock:
            recent_conversations = self._conversations[-limit:] if limit > 0 else []
        
        if include_metadata:
            return [exchange.to_dict() for exchange in recent_conversations]
        else:
            return [
                {
                    "user": exchange.user,
                    "assistant": exchange.assistant,
                    "timestamp": exchange.timestamp
                }
                for exchange in recent_conversations
            ]
    
    def get_openai_context(self, max_exchanges: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation context formatted for OpenAI API.
        
        Args:
            max_exchanges: Maximum number of exchanges to include
            
        Returns:
            List[Dict[str, str]]: Messages in OpenAI format
        """
        limit = max_exchanges or self.config.max_history_context
        
        with self._lock:
            recent_conversations = self._conversations[-limit:] if limit > 0 else []
        
        messages = []
        for exchange in recent_conversations:
            messages.extend(exchange.to_openai_format())
        
        return messages
    
    def search_conversations(self, 
                           query: str, 
                           case_sensitive: bool = False,
                           search_user: bool = True,
                           search_assistant: bool = True,
                           limit: Optional[int] = None) -> List[ConversationExchange]:
        """
        Search conversations for specific content.
        
        Args:
            query: Search term
            case_sensitive: Whether search should be case sensitive
            search_user: Whether to search user messages
            search_assistant: Whether to search assistant responses
            limit: Maximum number of results to return
            
        Returns:
            List[ConversationExchange]: Matching conversations
        """
        if not query.strip():
            return []
        
        search_query = query if case_sensitive else query.lower()
        results = []
        
        with self._lock:
            for exchange in self._conversations:
                match_found = False
                
                if search_user:
                    user_text = exchange.user if case_sensitive else exchange.user.lower()
                    if search_query in user_text:
                        match_found = True
                
                if search_assistant and not match_found:
                    assistant_text = exchange.assistant if case_sensitive else exchange.assistant.lower()
                    if search_query in assistant_text:
                        match_found = True
                
                if match_found:
                    results.append(exchange)
                    
                    if limit and len(results) >= limit:
                        break
        
        logger.debug(f"Search for '{query}' found {len(results)} results")
        return results
    
    def filter_by_date(self, 
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[ConversationExchange]:
        """
        Filter conversations by date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            List[ConversationExchange]: Conversations within date range
        """
        results = []
        
        with self._lock:
            for exchange in self._conversations:
                try:
                    exchange_date = datetime.fromisoformat(exchange.timestamp.replace('Z', '+00:00'))
                    
                    if start_date and exchange_date < start_date:
                        continue
                    if end_date and exchange_date > end_date:
                        continue
                    
                    results.append(exchange)
                    
                except ValueError:
                    logger.warning(f"Invalid timestamp format: {exchange.timestamp}")
                    continue
        
        return results
    
    def clear_history(self, create_backup: bool = True) -> bool:
        """
        Clear conversation history with optional backup.
        
        Args:
            create_backup: Whether to create backup before clearing
            
        Returns:
            bool: True if operation successful
        """
        try:
            if create_backup and self._conversations:
                self._create_backup("manual_clear")
            
            with self._lock:
                self._conversations.clear()
                
                if self.config.auto_save:
                    self._save_conversations()
            
            logger.info("Conversation history cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False
    
    def export_conversations(self, 
                           file_path: Union[str, Path],
                           format_type: ConversationFormat = ConversationFormat.JSON,
                           date_range: Optional[tuple] = None) -> bool:
        """
        Export conversations to various formats.
        
        Args:
            file_path: Output file path
            format_type: Export format (JSON, CSV, TXT, HTML)
            date_range: Optional (start_date, end_date) tuple
            
        Returns:
            bool: True if export successful
        """
        try:
            export_path = Path(file_path)
            
            # Filter conversations if date range specified
            if date_range:
                start_date, end_date = date_range
                conversations = self.filter_by_date(start_date, end_date)
            else:
                with self._lock:
                    conversations = self._conversations.copy()
            
            if not conversations:
                logger.warning("No conversations to export")
                return False
            
            # Ensure output directory exists
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export based on format
            if format_type == ConversationFormat.JSON:
                self._export_json(export_path, conversations)
            elif format_type == ConversationFormat.CSV:
                self._export_csv(export_path, conversations)
            elif format_type == ConversationFormat.TXT:
                self._export_txt(export_path, conversations)
            elif format_type == ConversationFormat.HTML:
                self._export_html(export_path, conversations)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            
            logger.info(f"Exported {len(conversations)} conversations to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def _export_json(self, file_path: Path, conversations: List[ConversationExchange]) -> None:
        """Export conversations to JSON format."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([conv.to_dict() for conv in conversations], f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, file_path: Path, conversations: List[ConversationExchange]) -> None:
        """Export conversations to CSV format."""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'User', 'Assistant', 'Tokens Used', 'Model', 'Response Time'])
            
            for conv in conversations:
                writer.writerow([
                    conv.timestamp,
                    conv.user,
                    conv.assistant,
                    conv.tokens_used,
                    conv.model_used,
                    conv.response_time
                ])
    
    def _export_txt(self, file_path: Path, conversations: List[ConversationExchange]) -> None:
        """Export conversations to plain text format."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Conversation History Export\\n")
            f.write(f"Generated: {datetime.now().isoformat()}\\n")
            f.write("=" * 50 + "\\n\\n")
            
            for i, conv in enumerate(conversations, 1):
                f.write(f"Exchange {i} - {conv.timestamp}\\n")
                f.write(f"User: {conv.user}\\n")
                f.write(f"Assistant: {conv.assistant}\\n")
                if conv.tokens_used:
                    f.write(f"Tokens: {conv.tokens_used}, Model: {conv.model_used}\\n")
                f.write("-" * 30 + "\\n\\n")
    
    def _export_html(self, file_path: Path, conversations: List[ConversationExchange]) -> None:
        """Export conversations to HTML format."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Conversation History</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .exchange { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; }
                .timestamp { color: #666; font-size: 0.8em; }
                .user { background-color: #e3f2fd; padding: 10px; margin: 5px 0; }
                .assistant { background-color: #f3e5f5; padding: 10px; margin: 5px 0; }
                .metadata { color: #888; font-size: 0.8em; }
            </style>
        </head>
        <body>
            <h1>Conversation History</h1>
            <p>Generated: {timestamp}</p>
            {exchanges}
        </body>
        </html>
        """
        
        exchanges_html = ""
        for i, conv in enumerate(conversations, 1):
            exchanges_html += f"""
            <div class="exchange">
                <div class="timestamp">Exchange {i} - {conv.timestamp}</div>
                <div class="user"><strong>User:</strong> {conv.user}</div>
                <div class="assistant"><strong>Assistant:</strong> {conv.assistant}</div>
                <div class="metadata">Tokens: {conv.tokens_used}, Model: {conv.model_used}, Response Time: {conv.response_time:.2f}s</div>
            </div>
            """
        
        html_content = html_template.format(
            timestamp=datetime.now().isoformat(),
            exchanges=exchanges_html
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _save_conversations(self) -> None:
        """
        Save conversations to file with atomic write operation.
        """
        try:
            # Use temporary file for atomic write
            temp_path = self.file_path.with_suffix('.tmp')
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(
                    [conv.to_dict() for conv in self._conversations], 
                    f, 
                    indent=2, 
                    ensure_ascii=False
                )
            
            # Atomic replace
            temp_path.replace(self.file_path)
            
            logger.debug(f"Saved {len(self._conversations)} conversations to {self.file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save conversations: {e}")
            # Clean up temporary file if it exists
            temp_path = self.file_path.with_suffix('.tmp')
            if temp_path.exists():
                temp_path.unlink()
    
    def get_statistics(self) -> Dict[str, Union[int, str, float]]:
        """
        Get comprehensive conversation statistics.
        
        Returns:
            Dict: Statistics about conversation history
        """
        with self._lock:
            if not self._conversations:
                return {
                    "total_exchanges": 0,
                    "first_conversation": None,
                    "last_conversation": None,
                    "total_user_chars": 0,
                    "total_assistant_chars": 0,
                    "average_user_length": 0,
                    "average_assistant_length": 0,
                    "total_tokens_used": 0,
                    "unique_models_used": 0
                }
            
            total_user_chars = sum(len(conv.user) for conv in self._conversations)
            total_assistant_chars = sum(len(conv.assistant) for conv in self._conversations)
            total_tokens = sum(conv.tokens_used for conv in self._conversations)
            unique_models = len(set(conv.model_used for conv in self._conversations if conv.model_used))
            
            return {
                "total_exchanges": len(self._conversations),
                "first_conversation": self._conversations[0].timestamp,
                "last_conversation": self._conversations[-1].timestamp,
                "total_user_chars": total_user_chars,
                "total_assistant_chars": total_assistant_chars,
                "average_user_length": round(total_user_chars / len(self._conversations), 1),
                "average_assistant_length": round(total_assistant_chars / len(self._conversations), 1),
                "total_tokens_used": total_tokens,
                "unique_models_used": unique_models,
                "file_path": str(self.file_path),
                "auto_save_enabled": self.config.auto_save
            }
    
    def optimize_storage(self, max_exchanges: Optional[int] = None) -> int:
        """
        Optimize storage by removing old conversations.
        
        Args:
            max_exchanges: Maximum number of recent exchanges to keep
            
        Returns:
            int: Number of exchanges removed
        """
        if not max_exchanges:
            max_exchanges = self.config.max_history_context * 10  # Default: 10x context limit
        
        with self._lock:
            if len(self._conversations) <= max_exchanges:
                return 0
            
            # Create backup before optimization
            self._create_backup("before_optimization")
            
            # Keep only recent conversations
            removed_count = len(self._conversations) - max_exchanges
            self._conversations = self._conversations[-max_exchanges:]
            
            if self.config.auto_save:
                self._save_conversations()
        
        logger.info(f"Storage optimized: removed {removed_count} old conversations")
        return removed_count


if __name__ == "__main__":
    # Example usage and testing
    import sys
    import os
    
    # Add parent directory to path to import config
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from config.settings import AppConfig
        
        # Test configuration
        app_config = AppConfig()
        app_config.conversation_file = "test_conversations.json"
        
        # Initialize manager
        manager = ConversationManager(app_config)
        
        print("✓ Conversation Manager initialized successfully")
        print(f"  File path: {manager.file_path}")
        print(f"  Auto-save: {app_config.auto_save}")
        
        # Display statistics
        stats = manager.get_statistics()
        print("\\nCurrent Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Test adding an exchange
        manager.add_exchange(
            "Hello, this is a test message",
            "Hello! This is a test response from the AI assistant.",
            tokens_used=25,
            model_used="gpt-3.5-turbo",
            response_time=1.5
        )
        
        print(f"\\n✓ Test exchange added. Total conversations: {len(manager._conversations)}")
        
    except ImportError:
        print("❌ Could not import configuration module")
    except Exception as e:
        print(f"❌ Error testing conversation manager: {e}")