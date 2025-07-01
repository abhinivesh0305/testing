from typing import Dict, List
from elsai_chat_history.models.message import Message
from elsai_chat_history.config.loggerConfig import setup_logger

# Initialize logger
logger = setup_logger()

class MemoryStoreImpl:
    """Internal implementation of in-memory chat history storage."""
    
    def __init__(self):
        self._storage: Dict[str, List[Message]] = {}
        logger.info("Initialized MemoryStore")
    
    async def load_history(self, session_id: str) -> List[Message]:
        """Load chat history for a given session."""
        messages = self._storage.get(session_id, []).copy()
        logger.debug(f"Loaded {len(messages)} messages for session {session_id} from memory")
        return messages
    
    async def save_history(self, session_id: str, messages: List[Message]) -> None:
        """Save chat history for a given session."""
        self._storage[session_id] = messages.copy()
        logger.info(f"Saved {len(messages)} messages for session {session_id} to memory")
    
    async def append_message(self, session_id: str, message: Message) -> None:
        """Append a single message to the history."""
        if session_id not in self._storage:
            self._storage[session_id] = []
            logger.debug(f"Created new session {session_id} in memory")
        
        self._storage[session_id].append(message)
        logger.info(f"Appended message to session {session_id}. Total messages: {len(self._storage[session_id])}")
    
    async def clear_history(self, session_id: str) -> None:
        """Clear all history for a session."""
        if session_id in self._storage:
            message_count = len(self._storage[session_id])
            self._storage.pop(session_id, None)
            logger.info(f"Cleared {message_count} messages for session {session_id} from memory")
        else:
            logger.debug(f"No history found to clear for session {session_id}")
    
    async def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        sessions = list(self._storage.keys())
        logger.debug(f"Listed {len(sessions)} sessions from memory store")
        return sessions