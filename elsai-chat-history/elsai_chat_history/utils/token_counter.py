from typing import Optional
from .token_counter_implementation import _TokenCounterImpl

class TokenCounter:
    """Simple token counting utility."""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self._impl = _TokenCounterImpl(model)
        self.model = self._impl.model
    
    def count_tokens(self, text: str) -> int:
        """Count approximate tokens in text."""
        return self._impl._count_tokens_internal(text)
    
    def count_tokens_in_messages(self, messages: list) -> int:
        """Count tokens across multiple messages."""
        return self._impl._count_tokens_in_messages_internal(messages)