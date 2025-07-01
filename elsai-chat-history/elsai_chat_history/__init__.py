"""
Chat History Manager for LangGraph

A modular, extensible system for managing chat history with multiple storage backends
and memory management strategies.
"""

from .models import Message
from .stores import ChatHistoryStore, MemoryStore, JSONStore, SQLiteStore
from .strategies import MemoryStrategy, TrimmingStrategy, SummarizationStrategy
from .manager import ChatHistoryManager
from .utils import MessageSerializer, TokenCounter

__version__ = "1.0.0"
__all__ = [
    "Message",
    "ChatHistoryStore",
    "MemoryStore", 
    "JSONStore",
    "SQLiteStore",
    "MemoryStrategy",
    "TrimmingStrategy",
    "SummarizationStrategy", 
    "ChatHistoryManager",
    "MessageSerializer",
    "TokenCounter"
]
