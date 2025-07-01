from abc import ABC, abstractmethod
from typing import List
from elsai_chat_history.models.message import Message


class MemoryStrategy(ABC):
    """Abstract base class for memory management strategies."""
    
    @abstractmethod
    async def manage(self, messages: List[Message]) -> List[Message]:
        """Apply memory management strategy to the message list."""
        pass
    
    @abstractmethod
    def should_apply(self, messages: List[Message]) -> bool:
        """Check if the strategy should be applied to the current message list."""
        pass