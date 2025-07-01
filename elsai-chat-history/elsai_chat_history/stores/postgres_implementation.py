import asyncpg
import json
from typing import List, Optional
from .base import ChatHistoryStore
from elsai_chat_history.models.message import Message
from elsai_chat_history.config.loggerConfig import setup_logger

# Initialize logger
logger = setup_logger()

class PostgresStoreImpl(ChatHistoryStore):
    """PostgreSQL-based implementation of chat history storage."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._pool: Optional[asyncpg.Pool] = None
        logger.info("Initialized PostgresStore")
    
    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            logger.debug("Creating new PostgreSQL connection pool")
            
            async def init_connection(conn):
                await conn.set_type_codec(
                    'jsonb',
                    encoder=json.dumps,
                    decoder=json.loads,
                    schema='pg_catalog'
                )
            
            self._pool = await asyncpg.create_pool(
                self.connection_string,
                init=init_connection
            )
            await self._init_db()
            logger.info("Successfully created PostgreSQL connection pool and initialized database")
        return self._pool
    
    async def _init_db(self):
        """Initialize the database schema."""
        logger.debug("Initializing PostgreSQL database schema")
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    message_id TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id 
                ON chat_messages(session_id)
            """)
        logger.info("Database schema initialized successfully")
    
    async def load_history(self, session_id: str) -> List[Message]:
        """Load chat history for a given session."""
        logger.debug(f"Loading history for session {session_id} from PostgreSQL")
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT role, content, timestamp, metadata, message_id
                FROM chat_messages 
                WHERE session_id = $1
                ORDER BY id ASC
            """, session_id)
            
            messages = []
            for row in rows:
                # Handle metadata properly - ensure it's a dict
                metadata = row["metadata"]
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
                        logger.warning(f"Failed to parse metadata for message in session {session_id}")
                elif metadata is None:
                    metadata = {}
                
                message_data = {
                    "role": row["role"],
                    "content": row["content"],
                    "timestamp": row["timestamp"],
                    "metadata": metadata,
                    "message_id": row["message_id"],
                    "session_id": session_id
                }
                messages.append(Message.from_dict(message_data))
            
            logger.info(f"Successfully loaded {len(messages)} messages for session {session_id} from PostgreSQL")
            return messages
    
    async def save_history(self, session_id: str, messages: List[Message]) -> None:
        """Save chat history for a given session."""
        logger.debug(f"Saving {len(messages)} messages for session {session_id} to PostgreSQL")
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Clear existing messages for the session
                deleted_count = await conn.fetchval("SELECT COUNT(*) FROM chat_messages WHERE session_id = $1", session_id)
                await conn.execute("DELETE FROM chat_messages WHERE session_id = $1", session_id)
                logger.debug(f"Deleted {deleted_count} existing messages for session {session_id}")
                
                # Insert new messages
                for message in messages:
                    await conn.execute("""
                        INSERT INTO chat_messages 
                        (session_id, role, content, timestamp, metadata, message_id)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """, 
                    session_id,
                    message.role,
                    message.content,
                    message.timestamp,
                    message.metadata,  # JSONB codec will handle this
                    message.message_id
                    )
        
        logger.info(f"Successfully saved {len(messages)} messages for session {session_id} to PostgreSQL")
    
    async def append_message(self, session_id: str, message: Message) -> None:
        """Append a single message to the history."""
        logger.debug(f"Appending message to session {session_id} in PostgreSQL")
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_messages 
                (session_id, role, content, timestamp, metadata, message_id)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, 
            session_id,
            message.role,
            message.content,
            message.timestamp,
            message.metadata,  # JSONB codec will handle this
            message.message_id
            )
        
        logger.info(f"Successfully appended message to session {session_id} in PostgreSQL")
    
    async def clear_history(self, session_id: str) -> None:
        """Clear all history for a session."""
        logger.debug(f"Clearing history for session {session_id} from PostgreSQL")
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            deleted_count = await conn.fetchval("SELECT COUNT(*) FROM chat_messages WHERE session_id = $1", session_id)
            await conn.execute("DELETE FROM chat_messages WHERE session_id = $1", session_id)
        
        logger.info(f"Successfully cleared {deleted_count} messages for session {session_id} from PostgreSQL")
    
    async def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        logger.debug("Listing sessions from PostgreSQL")
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT DISTINCT session_id FROM chat_messages")
            sessions = [row["session_id"] for row in rows]
        
        logger.info(f"Found {len(sessions)} sessions in PostgreSQL store")
        return sessions
    
    async def close(self):
        """Close the connection pool."""
        if self._pool:
            logger.info("Closing PostgreSQL connection pool")
            await self._pool.close()
            logger.info("PostgreSQL connection pool closed")