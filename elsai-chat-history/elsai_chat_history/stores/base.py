from abc import ABC, abstractmethod
from typing import List, Optional
from elsai_chat_history.models.message import Message


class ChatHistoryStore(ABC):
    """Abstract base class for chat history storage backends."""
    
    @abstractmethod
    async def load_history(self, session_id: str) -> List[Message]:
        """Load chat history for a given session."""
        pass
    
    @abstractmethod
    async def save_history(self, session_id: str, messages: List[Message]) -> None:
        """Save chat history for a given session."""
        pass
    
    @abstractmethod
    async def append_message(self, session_id: str, message: Message) -> None:
        """Append a single message to the history."""
        pass
    
    @abstractmethod
    async def clear_history(self, session_id: str) -> None:
        """Clear all history for a session."""
        pass
    
    @abstractmethod
    async def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        pass
