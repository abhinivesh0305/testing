from typing import List
from elsai_chat_history.models.message import Message
from .postgres_implementation import PostgresStoreImpl


class PostgresStore:
    """PostgreSQL-based implementation of chat history storage."""
    
    def __init__(self, connection_string: str):
        self._impl = PostgresStoreImpl(connection_string)
    
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
    
    async def close(self):
        """Close the connection pool."""
        return await self._impl.close()