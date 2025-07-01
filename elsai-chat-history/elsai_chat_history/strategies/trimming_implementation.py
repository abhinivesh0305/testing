from typing import List
from elsai_chat_history.models.message import Message
from elsai_chat_history.utils.token_counter import TokenCounter
from elsai_chat_history.config.loggerConfig import setup_logger

# Set up logger
logger = setup_logger()

class TrimmingStrategyImpl:
    """Internal implementation for trimming strategy."""
    
    def __init__(
        self, 
        max_messages: int = None, 
        max_tokens: int = None,
        preserve_system: bool = True,
        preserve_recent: int = 2
    ):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.preserve_system = preserve_system
        self.preserve_recent = preserve_recent
        self.token_counter = TokenCounter() if max_tokens else None
        
        logger.info(f"TrimmingStrategyImpl initialized with max_messages={max_messages}, max_tokens={max_tokens}, preserve_system={preserve_system}, preserve_recent={preserve_recent}")
    
    def should_apply(self, messages: List[Message]) -> bool:
        """Check if trimming should be applied."""
        message_count_exceeded = self.max_messages and len(messages) > self.max_messages
        token_count_exceeded = False
        
        if self.max_tokens and self.token_counter:
            total_tokens = sum(self.token_counter.count_tokens(msg.content) for msg in messages)
            token_count_exceeded = total_tokens > self.max_tokens
            logger.debug(f"Token count check: {total_tokens} tokens vs {self.max_tokens} max - exceeded: {token_count_exceeded}")
        
        should_apply = message_count_exceeded or token_count_exceeded
        logger.debug(f"Trimming check: {len(messages)} messages (max: {self.max_messages}) - should_apply: {should_apply}")
        
        return should_apply
    
    def _separate_messages(self, messages: List[Message]):
        """Separate messages into system, trimmable, and recent."""
        system_messages = [m for m in messages if m.role == "system"] if self.preserve_system else []
        non_system_messages = [m for m in messages if m.role != "system"]
        recent_messages = non_system_messages[-self.preserve_recent:] if self.preserve_recent > 0 else []
        trimmable_messages = non_system_messages[:-self.preserve_recent] if self.preserve_recent > 0 else non_system_messages

        logger.debug(f"Message separation: {len(system_messages)} system, {len(recent_messages)} recent, {len(trimmable_messages)} trimmable")
        return system_messages, trimmable_messages, recent_messages

    def _apply_message_limit(self, system_messages, recent_messages, trimmable_messages):
        """Trim messages based on message count limit."""
        if not self.max_messages:
            return trimmable_messages

        available_slots = self.max_messages - len(system_messages) - len(recent_messages)
        logger.debug(f"Message limit trimming: {available_slots} slots available for trimmable messages")

        if available_slots <= 0:
            logger.info("All trimmable messages removed due to message limit")
            return []

        original_count = len(trimmable_messages)
        trimmable_messages = trimmable_messages[-available_slots:]
        trimmed_count = original_count - len(trimmable_messages)

        if trimmed_count > 0:
            logger.info(f"Trimmed {trimmed_count} messages due to message limit")

        return trimmable_messages

    def _apply_token_limit(self, system_messages, trimmable_messages, recent_messages):
        """Trim messages based on token count limit."""
        if not (self.max_tokens and self.token_counter):
            return trimmable_messages

        result_messages = system_messages + trimmable_messages + recent_messages
        total_tokens = sum(self.token_counter.count_tokens(msg.content) for msg in result_messages)
        logger.debug(f"Token limit trimming: starting with {total_tokens} tokens (max: {self.max_tokens})")

        trimmed_by_tokens = 0
        while total_tokens > self.max_tokens and trimmable_messages:
            removed = trimmable_messages.pop(0)
            removed_tokens = self.token_counter.count_tokens(removed.content)
            total_tokens -= removed_tokens
            trimmed_by_tokens += 1
            logger.debug(f"Removed message with {removed_tokens} tokens, new total: {total_tokens}")

        if trimmed_by_tokens > 0:
            logger.info(f"Trimmed {trimmed_by_tokens} messages due to token limit")
        if total_tokens > self.max_tokens:
            logger.warning(f"Unable to reach token limit: {total_tokens} tokens remaining")

        return trimmable_messages

    async def manage(self, messages: List[Message]) -> List[Message]:
        """Apply trimming strategy to messages."""
        logger.info(f"Starting trimming management for {len(messages)} messages")

        if not self.should_apply(messages):
            logger.info("Trimming not needed - returning original messages")
            return messages

        system_messages, trimmable_messages, recent_messages = self._separate_messages(messages)
        trimmable_messages = self._apply_message_limit(system_messages, recent_messages, trimmable_messages)
        trimmable_messages = self._apply_token_limit(system_messages, trimmable_messages, recent_messages)

        result = system_messages + trimmable_messages + recent_messages
        logger.info(f"Trimming complete: {len(messages)} messages reduced to {len(result)} messages")
        return result