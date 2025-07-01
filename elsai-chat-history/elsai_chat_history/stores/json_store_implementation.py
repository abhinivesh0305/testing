import json
import os
from pathlib import Path
from typing import List
from .base import ChatHistoryStore
from elsai_chat_history.models.message import Message
from elsai_chat_history.utils.serialization import MessageSerializer
from elsai_chat_history.config.loggerConfig import setup_logger

# Initialize logger
logger = setup_logger()

class JSONStoreImpl(ChatHistoryStore):
    """JSON file-based implementation of chat history storage."""
    
    def __init__(self, storage_dir: str = "chat_histories"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        logger.info(f"Initialized JSONStore with storage directory: {self.storage_dir.absolute()}")
    
    def _get_file_path(self, session_id: str) -> Path:
        """Get the file path for a session."""
        return self.storage_dir / f"{session_id}.json"
    
    async def load_history(self, session_id: str) -> List[Message]:
        """Load chat history for a given session."""
        file_path = self._get_file_path(session_id)
        logger.debug(f"Loading history for session {session_id} from {file_path}")
        
        if not file_path.exists():
            logger.debug(f"No history file found for session {session_id}, returning empty list")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            messages = [Message.from_dict(msg_data) for msg_data in data]
            logger.info(f"Successfully loaded {len(messages)} messages for session {session_id}")
            return messages
            
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to load history for session {session_id}: {e}")
            raise ValueError(f"Failed to load history for session {session_id}: {e}")
    
    async def save_history(self, session_id: str, messages: List[Message]) -> None:
        """Save chat history for a given session."""
        file_path = self._get_file_path(session_id)
        logger.debug(f"Saving {len(messages)} messages for session {session_id} to {file_path}")
        
        try:
            data = [MessageSerializer.to_dict(msg) for msg in messages]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved {len(messages)} messages for session {session_id}")
            
        except (OSError, ValueError) as e:
            logger.error(f"Failed to save history for session {session_id}: {e}")
            raise ValueError(f"Failed to save history for session {session_id}: {e}")
    
    async def append_message(self, session_id: str, message: Message) -> None:
        """Append a single message to the history."""
        logger.debug(f"Appending message to session {session_id}")
        
        messages = await self.load_history(session_id)
        messages.append(message)
        await self.save_history(session_id, messages)
        
        logger.info(f"Successfully appended message to session {session_id}")
    
    async def clear_history(self, session_id: str) -> None:
        """Clear all history for a session."""
        file_path = self._get_file_path(session_id)
        logger.debug(f"Clearing history for session {session_id}")
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Successfully cleared history for session {session_id}")
        else:
            logger.debug(f"No history file to clear for session {session_id}")
    
    async def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        logger.debug(f"Listing sessions in directory {self.storage_dir}")
        
        sessions = [f.stem for f in self.storage_dir.glob("*.json")]
        logger.info(f"Found {len(sessions)} sessions in JSON store")
        return sessions