from typing import List
from .json_store_implementation import JSONStoreImpl
from elsai_chat_history.models.message import Message


class JSONStore:
    """JSON file-based implementation of chat history storage."""
    
    def __init__(self, storage_dir: str = "chat_histories"):
        self._impl = JSONStoreImpl(storage_dir)
    
    def _get_file_path(self, session_id: str):
        """Get the file path for a session."""
        return self._impl._get_file_path(session_id)
    
    async def load_history(self, session_id: str) -> List[Message]:
        """Load chat history for a given session."""
        return await self._impl.load_history(session_id)
    
    async def save_history(self, session_id: str, messages: List[Message]) -> None:
        """Save chat history for a given session."""
        await self._impl.save_history(session_id, messages)
    
    async def append_message(self, session_id: str, message: Message) -> None:
        """Append a single message to the history."""
        await self._impl.append_message(session_id, message)
    
    async def clear_history(self, session_id: str) -> None:
        """Clear all history for a session."""
        await self._impl.clear_history(session_id)
    
    async def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        return await self._impl.list_sessions()