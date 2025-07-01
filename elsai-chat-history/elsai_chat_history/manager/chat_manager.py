from typing import List, Optional, Dict, Any
from elsai_chat_history.models.message import Message
from elsai_chat_history.stores.base import ChatHistoryStore
from elsai_chat_history.strategies.base import MemoryStrategy
from .chat_manager_implementation import _ChatHistoryManagerImpl


class ChatHistoryManager:
    """Core orchestrator for chat history management."""
    
    def __init__(
        self,
        store: ChatHistoryStore,
        strategy: Optional[MemoryStrategy] = None,
        auto_save: bool = True
    ):
        self._impl = _ChatHistoryManagerImpl(store, strategy, auto_save)
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None
    ) -> Message:
        """Add a new message to the chat history."""
        return await self._impl.add_message(session_id, role, content, metadata, message_id)
    
    async def get_history(self, session_id: str, force_reload: bool = False) -> List[Message]:
        """Get chat history for a session."""
        return await self._impl.get_history(session_id, force_reload)
    
    async def get_context(
        self, 
        session_id: str, 
        max_messages: Optional[int] = None,
        roles: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get formatted context for LLM calls."""
        return await self._impl.get_context(session_id, max_messages, roles)
    
    async def clear_session(self, session_id: str) -> None:
        """Clear all history for a session."""
        return await self._impl.clear_session(session_id)
    
    async def save_session(self, session_id: str) -> None:
        """Manually save a session to storage."""
        return await self._impl.save_session(session_id)
    
    async def list_sessions(self) -> List[str]:
        """List all available sessions."""
        return await self._impl.list_sessions()
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics about a session."""
        return await self._impl.get_session_stats(session_id)