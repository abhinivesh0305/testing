# message_serializer_impl.py
from typing import Dict, Any
from datetime import datetime
from elsai_chat_history.models.message import Message
from elsai_chat_history.config.loggerConfig import setup_logger

# Set up logger
logger = setup_logger()

class MessageSerializerImpl:
    """Internal implementation for message serialization utilities."""
    
    @staticmethod
    def _to_dict_impl(message: Message) -> Dict[str, Any]:
        """Internal implementation for converting Message to dictionary."""
        logger.debug(f"Serializing message to dict: role={message.role}, message_id={message.message_id}")
        
        try:
            result = {
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "metadata": message.metadata,
                "session_id": message.session_id,
                "message_id": message.message_id
            }
            logger.debug("Message successfully serialized to dictionary")
            return result
        except Exception as e:
            logger.error(f"Failed to serialize message to dict: {e}")
            raise
    
    @staticmethod
    def _from_dict_impl(data: Dict[str, Any]) -> Message:
        """Internal implementation for creating Message from dictionary."""
        logger.debug(f"Deserializing message from dict: role={data.get('role')}, message_id={data.get('message_id')}")
        
        try:
            # Handle timestamp conversion if it's a string
            if isinstance(data.get("timestamp"), str):
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                logger.debug("Converted timestamp from string to datetime")
            
            message = Message(**data)
            logger.debug("Message successfully deserialized from dictionary")
            return message
        except Exception as e:
            logger.error(f"Failed to deserialize message from dict: {e}")
            raise
    
    @staticmethod
    def _to_langchain_format_impl(message: Message) -> Dict[str, str]:
        """Internal implementation for converting to LangChain message format."""
        logger.debug(f"Converting message to LangChain format: role={message.role}, message_id={message.message_id}")
        
        try:
            result = {
                "role": message.role,
                "content": message.content
            }
            logger.debug("Message successfully converted to LangChain format")
            return result
        except Exception as e:
            logger.error(f"Failed to convert message to LangChain format: {e}")
            raise
    
    @staticmethod
    def _batch_to_langchain_impl(messages: list[Message]) -> list[Dict[str, str]]:
        """Internal implementation for converting list of messages to LangChain format."""
        logger.info(f"Converting batch of {len(messages)} messages to LangChain format")
        
        try:
            result = [MessageSerializerImpl._to_langchain_format_impl(msg) for msg in messages]
            logger.info(f"Successfully converted {len(result)} messages to LangChain format")
            return result
        except Exception as e:
            logger.error(f"Failed to convert message batch to LangChain format: {e}")
            raise