import sqlite3
import json
from typing import List
from pathlib import Path
from .base import ChatHistoryStore
from elsai_chat_history.models.message import Message
from elsai_chat_history.utils.serialization import MessageSerializer
from elsai_chat_history.config.loggerConfig import setup_logger

# Initialize logger
logger = setup_logger()

class SQLiteStoreImpl(ChatHistoryStore):
    """SQLite-based implementation of chat history storage - Internal implementation."""
    
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = Path(db_path)
        self._init_db()
        logger.info(f"Initialized SQLiteStore with database path: {self.db_path.absolute()}")
    
    def _init_db(self):
        """Initialize the database schema."""
        logger.debug("Initializing SQLite database schema")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    message_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON chat_messages(session_id)
            """)
        
        logger.info("SQLite database schema initialized successfully")
    
    async def load_history(self, session_id: str) -> List[Message]:
        """Load chat history for a given session."""
        logger.debug(f"Loading history for session {session_id} from SQLite")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT role, content, timestamp, metadata, message_id
                FROM chat_messages 
                WHERE session_id = ?
                ORDER BY id ASC
            """, (session_id,))
            
            messages = []
            for row in cursor.fetchall():
                try:
                    message_data = {
                        "role": row["role"],
                        "content": row["content"],
                        "timestamp": row["timestamp"],
                        "metadata": json.loads(row["metadata"] or "{}"),
                        "message_id": row["message_id"],
                        "session_id": session_id
                    }
                    messages.append(Message.from_dict(message_data))
                except (ValueError) as e:
                    logger.warning(f"Failed to parse message for session {session_id}: {e}")
                    continue
            
            logger.info(f"Successfully loaded {len(messages)} messages for session {session_id} from SQLite")
            return messages
    
    async def save_history(self, session_id: str, messages: List[Message]) -> None:
        """Save chat history for a given session."""
        logger.debug(f"Saving {len(messages)} messages for session {session_id} to SQLite")
        
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing messages for the session
            cursor = conn.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (session_id,))
            deleted_count = cursor.fetchone()[0]
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            logger.debug(f"Deleted {deleted_count} existing messages for session {session_id}")
            
            # Insert new messages
            for message in messages:
                try:
                    conn.execute("""
                        INSERT INTO chat_messages 
                        (session_id, role, content, timestamp, metadata, message_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        session_id,
                        message.role,
                        message.content,
                        message.timestamp.isoformat(),
                        json.dumps(message.metadata),
                        message.message_id
                    ))
                except Exception as e:
                    logger.error(f"Failed to save message {message.message_id} for session {session_id}: {e}")
                    raise
        
        logger.info(f"Successfully saved {len(messages)} messages for session {session_id} to SQLite")
    
    async def append_message(self, session_id: str, message: Message) -> None:
        """Append a single message to the history."""
        logger.debug(f"Appending message to session {session_id} in SQLite")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO chat_messages 
                (session_id, role, content, timestamp, metadata, message_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                message.role,
                message.content,
                message.timestamp.isoformat(),
                json.dumps(message.metadata),
                message.message_id
            ))
        
        logger.info(f"Successfully appended message to session {session_id} in SQLite")
    
    async def clear_history(self, session_id: str) -> None:
        """Clear all history for a session."""
        logger.debug(f"Clearing history for session {session_id} from SQLite")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (session_id,))
            deleted_count = cursor.fetchone()[0]
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        
        logger.info(f"Successfully cleared {deleted_count} messages for session {session_id} from SQLite")
    
    async def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        logger.debug("Listing sessions from SQLite")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT session_id FROM chat_messages")
            sessions = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Found {len(sessions)} sessions in SQLite store")
        return sessions