import re
from typing import Optional
from elsai_chat_history.config.loggerConfig import setup_logger

# Set up logger
logger = setup_logger()

class _TokenCounterImpl:
    """Internal implementation for token counting utility."""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        # Simple approximation: ~4 characters per token for most models
        self.chars_per_token = 4
        logger.info(f"TokenCounterImpl initialized with model={model}, chars_per_token={self.chars_per_token}")
    
    def _count_tokens_internal(self, text: str) -> int:
        """Internal token counting implementation."""
        if not text:
            logger.debug("Empty text provided - returning 0 tokens")
            return 0
        
        # Simple estimation based on character count
        # This is a rough approximation - for production use, consider tiktoken
        token_count = max(1, len(text) // self.chars_per_token)
        logger.debug(f"Token count for text ({len(text)} chars): {token_count} tokens")
        return token_count
    
    def _count_tokens_in_messages_internal(self, messages: list) -> int:
        """Internal implementation for counting tokens across multiple messages."""
        logger.debug(f"Counting tokens for {len(messages)} messages")
        
        total = 0
        processed_messages = 0
        
        for message in messages:
            try:
                if hasattr(message, 'content'):
                    tokens = self._count_tokens_internal(message.content)
                    total += tokens
                    processed_messages += 1
                elif isinstance(message, dict) and 'content' in message:
                    tokens = self._count_tokens_internal(message['content'])
                    total += tokens
                    processed_messages += 1
                elif isinstance(message, str):
                    tokens = self._count_tokens_internal(message)
                    total += tokens
                    processed_messages += 1
                else:
                    logger.warning(f"Unrecognized message format: {type(message)} - skipping")
            except Exception as e:
                logger.error(f"Error processing message for token counting: {e}")
                continue
        
        logger.info(f"Token counting complete: {total} tokens across {processed_messages} messages")
        return total