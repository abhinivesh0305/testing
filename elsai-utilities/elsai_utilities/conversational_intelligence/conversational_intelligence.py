"""
Conversational Intelligence Wrapper

A comprehensive class that provides conversational intelligence capabilities including:
- Follow-up question generation
- Action item detection
- Topic and intent detection
"""

from typing import List, Union, Optional, Dict, Any
from .implementation import _ConversationalIntelligenceImplementation
from .validators import ActionItem, DetectedTopic, DetectedIntent, TopicIntentResponse


class ConversationalIntelligence:
    """
    A comprehensive wrapper class for conversational intelligence operations.
    
    This class provides methods for:
    - Generating follow-up questions
    - Detecting and extracting action items
    - Detecting topics and classifying intents
    """
    
    def __init__(self, llm):
        """
        Initialize the ConversationalIntelligence class.
        
        Args:
            llm: LLM instance with .invoke() method (e.g., ChatOpenAI, Claude, etc.)
        """
        self._core = _ConversationalIntelligenceImplementation(llm)
    
    # ==================== FOLLOW-UP QUESTIONS ====================
    
    def generate_followup_questions(
        self,
        user_question: str,
        answer: str,
        context: Union[str, List[str], None] = None,
        num_questions: int = 3
    ) -> List[str]:
        """
        Generate follow-up questions using the LLM with validation.
        
        Args:
            user_question: Original user question
            answer: Assistant's answer
            context: Optional context (string or list)
            num_questions: Number of questions to generate
        
        Returns:
            List of validated follow-up questions
            
        Raises:
            ValidationError: If input parameters are invalid
            ValueError: If LLM response cannot be parsed or validated
        """
        return self._core._generate_followup_questions_internal(
            user_question, answer, context, num_questions
        )
    
    def generate_followup_questions_safe(
        self,
        user_question: str,
        answer: str,
        context: Union[str, List[str], None] = None,
        num_questions: int = 3,
        fallback_questions: Optional[List[str]] = None
    ) -> List[str]:
        """
        Safe wrapper that returns fallback questions if validation fails.
        """
        return self._core._generate_followup_questions_safe_internal(
            user_question, answer, context, num_questions, fallback_questions
        )
    
    # ==================== ACTION ITEM DETECTION ====================
    
    def detect_action_items(
        self,
        messages: Union[List[str], str],
        include_context: bool = True,
        extract_priority: bool = True,
        extract_assignee: bool = True,
        extract_due_date: bool = True,
        min_confidence: float = 0.7
    ) -> List[ActionItem]:
        """
        Detect and extract action items from conversation messages.
        
        Args:
            messages: List of conversation messages or single message
            include_context: Whether to include context in extraction
            extract_priority: Whether to extract priority information
            extract_assignee: Whether to extract assignee information
            extract_due_date: Whether to extract due date information
            min_confidence: Minimum confidence threshold for detection
        
        Returns:
            List of validated ActionItem objects
            
        Raises:
            ValidationError: If input parameters are invalid
        """
        return self._core._detect_action_items_internal(
            messages, include_context, extract_priority, extract_assignee, 
            extract_due_date, min_confidence
        )
    
    # ==================== TOPIC AND INTENT DETECTION ====================
    
    def detect_topics_and_intents(
        self,
        messages: Union[List[str], str],
        detect_topics: bool = True,
        detect_intents: bool = True,
        min_confidence: float = 0.6,
        max_topics: int = 5,
        max_intents: int = 3,
        include_context: bool = True
    ) -> TopicIntentResponse:
        """
        Detect topics and classify intents from conversation messages.
        
        Args:
            messages: List of conversation messages or single message
            detect_topics: Whether to detect topics
            detect_intents: Whether to detect intents
            min_confidence: Minimum confidence threshold for detection
            max_topics: Maximum number of topics to return
            max_intents: Maximum number of intents to return
            include_context: Whether to include context in extraction
        
        Returns:
            TopicIntentResponse with validated topics and intents
            
        Raises:
            ValidationError: If input parameters are invalid
        """
        return self._core._detect_topics_and_intents_internal(
            messages, detect_topics, detect_intents, min_confidence, 
            max_topics, max_intents, include_context
        )
    
    def detect_topics_only(
        self,
        messages: Union[List[str], str],
        min_confidence: float = 0.6,
        max_topics: int = 5,
        include_context: bool = True
    ) -> List[DetectedTopic]:
        """
        Convenience method to detect only topics.
        
        Returns:
            List of DetectedTopic objects
        """
        return self._core._detect_topics_only_internal(
            messages, min_confidence, max_topics, include_context
        )
    
    def detect_intents_only(
        self,
        messages: Union[List[str], str],
        min_confidence: float = 0.6,
        max_intents: int = 3,
        include_context: bool = True
    ) -> List[DetectedIntent]:
        """
        Convenience method to detect only intents.
        
        Returns:
            List of DetectedIntent objects
        """
        return self._core._detect_intents_only_internal(
            messages, min_confidence, max_intents, include_context
        )
    
    # ==================== UTILITY AND CONVENIENCE METHODS ====================
    
    def analyze_conversation(
        self,
        messages: Union[List[str], str],
        include_followup: bool = True,
        include_actions: bool = True,
        include_topics: bool = True,
        include_intents: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Comprehensive conversation analysis that runs all available analyses.
        
        Args:
            messages: List of conversation messages or single message
            include_followup: Whether to generate follow-up questions (requires last message context)
            include_actions: Whether to detect action items
            include_topics: Whether to detect topics
            include_intents: Whether to detect intents
            **kwargs: Additional parameters for individual methods
        
        Returns:
            Dictionary containing all analysis results
        """
        return self._core._analyze_conversation_internal(
            messages, include_followup, include_actions, include_topics, include_intents, **kwargs
        )
    
    def get_conversation_summary(
        self,
        messages: Union[List[str], str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get a high-level summary of conversation analysis.
        
        Returns:
            Dictionary with summary statistics and key findings
        """
        return self._core._get_conversation_summary_internal(messages, **kwargs)