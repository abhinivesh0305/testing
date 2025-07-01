from typing import List
from .base import MemoryStrategy
from elsai_chat_history.models.message import Message
from .trimming_implementation import TrimmingStrategyImpl

class TrimmingStrategy(MemoryStrategy):
    """Strategy for trimming messages by count or token limit."""
    
    def __init__(
        self, 
        max_messages: int = None, 
        max_tokens: int = None,
        preserve_system: bool = True,
        preserve_recent: int = 2
    ):
        self._impl = TrimmingStrategyImpl(
            max_messages=max_messages,
            max_tokens=max_tokens,
            preserve_system=preserve_system,
            preserve_recent=preserve_recent
        )
    
    def should_apply(self, messages: List[Message]) -> bool:
        """Check if trimming should be applied."""
        return self._impl.should_apply(messages)
    
    async def manage(self, messages: List[Message]) -> List[Message]:
        """Apply trimming strategy to messages."""
        return await self._impl.manage(messages)