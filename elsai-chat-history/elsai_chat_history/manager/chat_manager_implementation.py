import uuid
from typing import List, Optional, Dict, Any
from elsai_chat_history.models.message import Message
from elsai_chat_history.stores.base import ChatHistoryStore
from elsai_chat_history.strategies.base import MemoryStrategy
from elsai_chat_history.config.loggerConfig import setup_logger

# Initialize logger
logger = setup_logger()

class _ChatHistoryManagerImpl:
    """Internal implementation for chat history management."""
    
    def __init__(
        self,
        store: ChatHistoryStore,
        strategy: Optional[MemoryStrategy] = None,
        auto_save: bool = True
    ):
        self.store = store
        self.strategy = strategy
        self.auto_save = auto_save
        self._cache: Dict[str, List[Message]] = {}
        logger.info(f"Initialized ChatHistoryManager with store: {type(store).__name__}, strategy: {type(strategy).__name__ if strategy else 'None'}, auto_save: {auto_save}")
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None
    ) -> Message:
        """Add a new message to the chat history."""
        logger.debug(f"Adding message for session {session_id}, role: {role}")
        
        # Generate message_id if not provided
        if not message_id:
            message_id = str(uuid.uuid4())
            logger.debug(f"Generated message_id: {message_id}")
            
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {},
            session_id=session_id,
            message_id=message_id
        )
        
        # Load current history if not cached
        if session_id not in self._cache:
            logger.debug(f"Loading history for session {session_id} (not in cache)")
            self._cache[session_id] = await self.store.load_history(session_id)
        
        # Add message to cache
        self._cache[session_id].append(message)
        logger.debug(f"Added message to cache. Session {session_id} now has {len(self._cache[session_id])} messages")
        
        # Apply memory management strategy
        if self.strategy:
            logger.debug(f"Applying memory strategy: {type(self.strategy).__name__}")
            original_count = len(self._cache[session_id])
            self._cache[session_id] = await self.strategy.manage(self._cache[session_id])
            new_count = len(self._cache[session_id])
            if original_count != new_count:
                logger.info(f"Memory strategy reduced messages from {original_count} to {new_count} for session {session_id}")
        
        # Auto-save if enabled
        if self.auto_save:
            logger.debug(f"Auto-saving session {session_id}")
            await self.store.save_history(session_id, self._cache[session_id])
        
        logger.info(f"Successfully added message to session {session_id}")
        return message
    
    async def get_history(self, session_id: str, force_reload: bool = False) -> List[Message]:
        """Get chat history for a session."""
        logger.debug(f"Getting history for session {session_id}, force_reload: {force_reload}")
        
        if force_reload or session_id not in self._cache:
            logger.debug(f"Loading history from store for session {session_id}")
            self._cache[session_id] = await self.store.load_history(session_id)
        
        message_count = len(self._cache[session_id])
        logger.debug(f"Returning {message_count} messages for session {session_id}")
        return self._cache[session_id].copy()
    
    async def get_context(
        self, 
        session_id: str, 
        max_messages: Optional[int] = None,
        roles: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get formatted context for LLM calls."""
        logger.debug(f"Getting context for session {session_id}, max_messages: {max_messages}, roles: {roles}")
        
        messages = await self.get_history(session_id)
        original_count = len(messages)
        
        # Filter by roles if specified
        if roles:
            messages = [msg for msg in messages if msg.role in roles]
            logger.debug(f"Filtered by roles {roles}: {len(messages)}/{original_count} messages")
        
        # Limit message count if specified
        if max_messages:
            messages = messages[-max_messages:]
            logger.debug(f"Limited to {max_messages} messages: returning {len(messages)} messages")
        
        # Convert to LLM-compatible format
        context = [{"role": msg.role, "content": msg.content} for msg in messages]
        logger.info(f"Generated context with {len(context)} messages for session {session_id}")
        return context
    
    async def clear_session(self, session_id: str) -> None:
        """Clear all history for a session."""
        logger.info(f"Clearing session {session_id}")
        await self.store.clear_history(session_id)
        self._cache.pop(session_id, None)
        logger.info(f"Successfully cleared session {session_id}")
    
    async def save_session(self, session_id: str) -> None:
        """Manually save a session to storage."""
        logger.debug(f"Manually saving session {session_id}")
        if session_id in self._cache:
            await self.store.save_history(session_id, self._cache[session_id])
            logger.info(f"Successfully saved session {session_id} with {len(self._cache[session_id])} messages")
        else:
            logger.warning(f"Attempted to save session {session_id} but it's not in cache")
    
    async def list_sessions(self) -> List[str]:
        """List all available sessions."""
        logger.debug("Listing all sessions")
        sessions = await self.store.list_sessions()
        logger.info(f"Found {len(sessions)} sessions")
        return sessions
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics about a session."""
        logger.debug(f"Getting statistics for session {session_id}")
        messages = await self.get_history(session_id)
        
        role_counts = {}
        summary_count = 0
        
        for message in messages:
            role_counts[message.role] = role_counts.get(message.role, 0) + 1
            if message.metadata.get("type") == "summary":
                summary_count += 1
        
        stats = {
            "total_messages": len(messages),
            "role_distribution": role_counts,
            "summary_count": summary_count,
            "first_message": messages[0].timestamp if messages else None,
            "last_message": messages[-1].timestamp if messages else None,
        }
        
        logger.info(f"Session {session_id} stats: {stats['total_messages']} messages, {summary_count} summaries")
        return stats