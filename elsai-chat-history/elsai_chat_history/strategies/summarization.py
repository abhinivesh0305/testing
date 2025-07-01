from typing import List
from .summarization_implementation import SummarizationStrategyImpl
from elsai_chat_history.models.message import Message


class SummarizationStrategy:
    """Strategy for incrementally summarizing old messages to save space."""
    
    def __init__(
        self,
        summarizer_llm,
        trigger_count: int = 20,
        preserve_recent: int = 5,
        preserve_system: bool = True
    ):
        self._impl = SummarizationStrategyImpl(
            summarizer_llm=summarizer_llm,
            trigger_count=trigger_count,
            preserve_recent=preserve_recent,
            preserve_system=preserve_system
        )
    
    def should_apply(self, messages: List[Message]) -> bool:
        """Check if summarization should be applied."""
        return self._impl.should_apply(messages)
    
    async def manage(self, messages: List[Message]) -> List[Message]:
        """Apply incremental summarization strategy to messages."""
        return await self._impl.manage(messages)