# message_serializer.py
from typing import Dict, Any
from elsai_chat_history.models.message import Message
from .serialization_implementation import MessageSerializerImpl


class MessageSerializer:
    """Utilities for converting between Message objects and storage formats."""
    
    @staticmethod
    def to_dict(message: Message) -> Dict[str, Any]:
        """Convert Message to dictionary."""
        return MessageSerializerImpl._to_dict_impl(message)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Message:
        """Create Message from dictionary."""
        return MessageSerializerImpl._from_dict_impl(data)
    
    @staticmethod
    def to_langchain_format(message: Message) -> Dict[str, str]:
        """Convert to LangChain message format."""
        return MessageSerializerImpl._to_langchain_format_impl(message)
    
    @staticmethod
    def batch_to_langchain(messages: list[Message]) -> list[Dict[str, str]]:
        """Convert list of messages to LangChain format."""
        return MessageSerializerImpl._batch_to_langchain_impl(messages)