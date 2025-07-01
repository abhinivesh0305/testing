from typing import List
from .base import ChatHistoryStore
from elsai_chat_history.models.message import Message
from .sqlite_store_implementation import SQLiteStoreImpl


class SQLiteStore(ChatHistoryStore):
    """SQLite-based implementation of chat history storage."""
    
    def __init__(self, db_path: str = "chat_history.db"):
        self._impl = SQLiteStoreImpl(db_path)
    
    async def load_history(self, session_id: str) -> List[Message]:
        """Load chat history for a given session."""
        return await self._impl.load_history(session_id)
    
    async def save_history(self, session_id: str, messages: List[Message]) -> None:
        """Save chat history for a given session."""
        return await self._impl.save_history(session_id, messages)
    
    async def append_message(self, session_id: str, message: Message) -> None:
        """Append a single message to the history."""
        return await self._impl.append_message(session_id, message)
    
    async def clear_history(self, session_id: str) -> None:
        """Clear all history for a session."""
        return await self._impl.clear_history(session_id)
    
    async def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        return await self._impl.list_sessions()