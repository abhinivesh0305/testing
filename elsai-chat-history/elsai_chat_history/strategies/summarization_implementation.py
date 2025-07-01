import uuid
from typing import List, Callable, Awaitable, Optional
from .base import MemoryStrategy
from elsai_chat_history.models.message import Message
from elsai_chat_history.config.loggerConfig import setup_logger

# Set up logger
logger = setup_logger()

class SummarizationStrategyImpl(MemoryStrategy):
    """Strategy for incrementally summarizing old messages to save space."""
    
    def __init__(
        self,
        summarizer_llm,
        trigger_count: int = 20,
        preserve_recent: int = 5,
        preserve_system: bool = True
    ):
        self.summarizer_llm = summarizer_llm
        self.trigger_count = trigger_count
        self.preserve_recent = preserve_recent
        self.preserve_system = preserve_system
        logger.info(f"SummarizationStrategyImpl initialized with trigger_count={trigger_count}, preserve_recent={preserve_recent}, preserve_system={preserve_system}")
    
    def should_apply(self, messages: List[Message]) -> bool:
        """Check if summarization should be applied."""
        should_apply = len(messages) > self.trigger_count
        logger.debug(f"Summarization check: {len(messages)} messages vs {self.trigger_count} trigger - should_apply: {should_apply}")
        return should_apply
    
    def _ensure_message_ids(self, messages: List[Message]) -> List[Message]:
        """Ensure all messages have unique message_id."""
        messages_without_ids = 0
        for message in messages:
            if not message.message_id:
                message.message_id = str(uuid.uuid4())
                messages_without_ids += 1
        
        if messages_without_ids > 0:
            logger.debug(f"Generated IDs for {messages_without_ids} messages without message_id")
        return messages
    
    def _find_last_summary(self, messages: List[Message]) -> Optional[Message]:
        """Find the most recent summary message."""
        for message in reversed(messages):
            if (message.role == "system" and 
                message.metadata.get("type") == "summary" and
                "summary_upto" in message.metadata):
                logger.debug(f"Found last summary message with ID: {message.message_id}")
                return message
        logger.debug("No previous summary message found")
        return None
    
    def _get_messages_after_summary(self, messages: List[Message], last_summary: Message) -> List[Message]:
        """Get messages that come after the last summary."""
        summary_upto = last_summary.metadata.get("summary_upto")
        if not summary_upto:
            logger.warning("Last summary found but no summary_upto metadata - returning all messages")
            return messages
        
        # Find the index of the message with summary_upto message_id
        summary_index = -1
        for i, msg in enumerate(messages):
            if msg.message_id == summary_upto:
                summary_index = i
                break
        
        if summary_index >= 0:
            messages_after = messages[summary_index + 1:]
            logger.debug(f"Found {len(messages_after)} messages after last summary (summary_upto: {summary_upto})")
            return messages_after
        else:
            # If we can't find the summary_upto message, summarize all non-system messages
            logger.warning(f"Could not find message with ID {summary_upto} - falling back to all non-system messages")
            return [msg for msg in messages if msg.role != "system" or msg.metadata.get("type") != "summary"]
    
    def _categorize_messages(self, messages: List[Message]) -> tuple:
        """Categorize messages into system, summary, and regular."""
        system, summary, regular = [], [], []
        for msg in messages:
            if msg.role == "system":
                if msg.metadata.get("type") == "summary":
                    summary.append(msg)
                elif self.preserve_system:
                    system.append(msg)
            else:
                regular.append(msg)
        logger.debug(f"Message categorization: {len(system)} system, {len(summary)} summaries, {len(regular)} regular")
        return system, summary, regular

    async def _generate_summary(self, messages: List[Message]) -> Optional[str]:
        """Generate summary content from messages."""
        prompt = [
            {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
            {"role": "user", "content": f"Summarize the following conversation:\n\n{messages}"}
        ]
        try:
            summary_content = await self.summarizer_llm.invoke(prompt)
            logger.info("Successfully generated summary content")
            return summary_content
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return None

    def _create_summary_message(self, content: str, messages: List[Message], summary_upto: Optional[str]) -> Message:
        """Create a new summary message."""
        return Message(
            role="system",
            content=f"[CONVERSATION_SUMMARY]: {content}",
            metadata={
                "type": "summary",
                "original_message_count": len(messages),
                "summary_upto": summary_upto,
                "timestamp_created": messages[-1].timestamp.isoformat() if messages else None
            },
            message_id=str(uuid.uuid4())
        )

    
    async def manage(self, messages: List[Message]) -> List[Message]:
        """Apply incremental summarization strategy to messages."""
        logger.info(f"Starting summarization management for {len(messages)} messages")

        if not self.should_apply(messages):
            logger.info("Summarization not needed - returning original messages")
            return messages

        messages = self._ensure_message_ids(messages)

        system_messages, summary_messages, regular_messages = self._categorize_messages(messages)
        last_summary = self._find_last_summary(summary_messages)

        messages_to_process = (
            self._get_messages_after_summary(regular_messages, last_summary)
            if last_summary else regular_messages
        )

        logger.info(f"{'Found existing' if last_summary else 'No existing'} summary - processing {len(messages_to_process)} messages")

        recent_messages = messages_to_process[-self.preserve_recent:] if self.preserve_recent > 0 else []
        summarizable_messages = messages_to_process[:-self.preserve_recent] if self.preserve_recent > 0 else messages_to_process

        logger.debug(f"Preserving {len(recent_messages)} recent messages, summarizing {len(summarizable_messages)} messages")

        if not summarizable_messages:
            logger.info("No messages to summarize - returning original messages")
            return messages

        summary_content = await self._generate_summary(summarizable_messages)
        if not summary_content:
            return messages

        summary_upto = summarizable_messages[-1].message_id if summarizable_messages else None
        new_summary = self._create_summary_message(summary_content, summarizable_messages, summary_upto)

        logger.info(f"Created new summary message (ID: {new_summary.message_id}) covering {len(summarizable_messages)} original messages")

        result = system_messages + summary_messages + [new_summary] + recent_messages
        logger.info(f"Summarization complete: {len(messages)} messages reduced to {len(result)} messages")
        return result