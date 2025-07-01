from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Union, Optional, Dict

# Constants to avoid duplication
EMPTY_MESSAGES_ERROR = 'Messages list cannot be empty'
NO_VALID_MESSAGES_ERROR = 'No valid messages found'

# Pydantic Models for Follow-up Questions
class FollowupQuestionsResponse(BaseModel):
    """Pydantic model to validate LLM response for follow-up questions."""
    questions: List[str] = Field(
        ..., 
        min_items=1, 
        max_items=10,
        description="List of follow-up questions"
    )
    
    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        """Validate and format questions."""
        if not v:
            raise ValueError('Questions list cannot be empty')
        
        # Process each question
        processed_questions = []
        for question in v:
            if not question or not str(question).strip():
                raise ValueError('Question cannot be empty')
            
            question = str(question).strip()
            if not question.endswith('?'):
                question += '?'  # Auto-add question mark if missing
                
            if len(question) < 5:  # Minimum reasonable question length
                raise ValueError('Question too short')
                
            processed_questions.append(question)
        
        # Remove duplicates (case-insensitive)
        seen = set()
        unique_questions = []
        
        for question in processed_questions:
            question_lower = question.lower().strip()
            if question_lower not in seen:
                seen.add(question_lower)
                unique_questions.append(question)
        
        return unique_questions

class GenerationConfig(BaseModel):
    """Configuration for follow-up question generation."""
    num_questions: int = Field(default=3, ge=1, le=10)
    user_question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    context: Optional[Union[str, List[str]]] = None
    
    @field_validator('user_question', 'answer')
    @classmethod
    def validate_non_empty(cls, v):
        if not str(v).strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return str(v).strip()

# Pydantic Models for Action Items
class ActionItem(BaseModel):
    """Pydantic model for a single action item."""
    task: str = Field(..., min_length=1, description="Description of the task")
    assignee: str = Field(default="", description="Person assigned to the task")
    due: str = Field(default="", description="Due date or deadline")
    priority: str = Field(default="", description="Priority level (high, medium, low)")
    context: str = Field(default="", description="Additional context or notes")
    source_message: str = Field(default="", description="Original message containing the action")
    
    @field_validator('task')
    @classmethod
    def validate_task(cls, v):
        """Validate and clean task description."""
        if not v or not str(v).strip():
            raise ValueError('Task description cannot be empty')
        
        task = str(v).strip()
        # Remove common prefixes that might be included
        prefixes_to_remove = [
            "action item:", "task:", "todo:", "to do:", "action:", 
            "please", "can you", "could you", "would you"
        ]
        
        task_lower = task.lower()
        for prefix in prefixes_to_remove:
            if task_lower.startswith(prefix):
                task = task[len(prefix):].strip()
                break
        
        # Ensure first letter is capitalized
        if task:
            task = task[0].upper() + task[1:] if len(task) > 1 else task.upper()
        
        return task
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority level."""
        if not v:
            return ""
        
        priority = str(v).lower().strip()
        valid_priorities = ["high", "medium", "low", "urgent", "normal"]
        
        # Map common priority indicators
        priority_mapping = {
            "urgent": "high",
            "asap": "high",
            "critical": "high",
            "important": "high",
            "normal": "medium",
            "regular": "medium",
            "low": "low",
            "minor": "low"
        }
        
        if priority in priority_mapping:
            return priority_mapping[priority]
        elif priority in valid_priorities:
            return priority
        else:
            return ""

# Pydantic Models for Topic and Intent Detection
class DetectedTopic(BaseModel):
    """Pydantic model for a detected topic."""
    name: str = Field(..., min_length=1, description="Name of the topic")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    keywords: List[str] = Field(default_factory=list, description="Key terms related to this topic")
    category: str = Field(default="", description="Broader category this topic belongs to")
    context: str = Field(default="", description="Context where this topic appeared")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate and clean topic name."""
        if not v or not str(v).strip():
            raise ValueError('Topic name cannot be empty')
        
        name = str(v).strip()
        # Capitalize first letter
        if name:
            name = name[0].upper() + name[1:] if len(name) > 1 else name.upper()
        
        return name
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        """Validate and clean keywords."""
        if not isinstance(v, list):
            return []
        
        # Clean and deduplicate keywords
        cleaned_keywords = []
        seen = set()
        
        for keyword in v:
            if keyword and str(keyword).strip():
                clean_keyword = str(keyword).strip().lower()
                if clean_keyword not in seen:
                    seen.add(clean_keyword)
                    cleaned_keywords.append(str(keyword).strip())
        
        return cleaned_keywords[:10]  # Limit to 10 keywords

class DetectedIntent(BaseModel):
    """Pydantic model for a detected intent."""
    intent: str = Field(..., min_length=1, description="Name of the detected intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    entities: Dict[str, str] = Field(default_factory=dict, description="Extracted entities")
    intent_type: str = Field(default="", description="Type of intent (question, request, information, etc.)")
    context: str = Field(default="", description="Context where this intent appeared")
    source_message: str = Field(default="", description="Original message containing the intent")
    
    @field_validator('intent')
    @classmethod
    def validate_intent(cls, v):
        """Validate and clean intent name."""
        if not v or not str(v).strip():
            raise ValueError('Intent name cannot be empty')
        
        intent = str(v).strip().lower().replace(' ', '_')
        return intent
    
    @field_validator('intent_type')
    @classmethod
    def validate_intent_type(cls, v):
        """Validate intent type."""
        if not v:
            return ""
        
        intent_type = str(v).lower().strip()
        valid_types = [
            "question", "request", "command", "information", "greeting", 
            "complaint", "compliment", "booking", "support", "general"
        ]
        
        return intent_type if intent_type in valid_types else "general"

class TopicIntentResponse(BaseModel):
    """Pydantic model to validate LLM response for topic and intent detection."""
    topics: List[DetectedTopic] = Field(
        default_factory=list,
        description="List of detected topics"
    )
    intents: List[DetectedIntent] = Field(
        default_factory=list,
        description="List of detected intents"
    )
    
    @field_validator('topics')
    @classmethod
    def validate_topics(cls, v):
        """Validate topics list."""
        if not isinstance(v, list):
            raise ValueError('Topics must be a list')
        
        # Remove duplicates based on topic name (case-insensitive)
        seen_topics = set()
        unique_topics = []
        
        for topic in v:
            if isinstance(topic, dict):
                try:
                    topic = DetectedTopic(**topic)
                except ValidationError:
                    continue
            
            topic_key = topic.name.lower().strip()
            if topic_key not in seen_topics and topic_key:
                seen_topics.add(topic_key)
                unique_topics.append(topic)
        
        # Sort by confidence (highest first)
        unique_topics.sort(key=lambda x: x.confidence, reverse=True)
        return unique_topics[:10]  # Limit to top 10 topics
    
    @field_validator('intents')
    @classmethod
    def validate_intents(cls, v):
        """Validate intents list."""
        if not isinstance(v, list):
            raise ValueError('Intents must be a list')
        
        # Remove duplicates based on intent name (case-insensitive)
        seen_intents = set()
        unique_intents = []
        
        for intent in v:
            if isinstance(intent, dict):
                try:
                    intent = DetectedIntent(**intent)
                except ValidationError:
                    continue
            
            intent_key = intent.intent.lower().strip()
            if intent_key not in seen_intents and intent_key:
                seen_intents.add(intent_key)
                unique_intents.append(intent)
        
        # Sort by confidence (highest first)
        unique_intents.sort(key=lambda x: x.confidence, reverse=True)
        return unique_intents

class TopicIntentDetectionConfig(BaseModel):
    """Configuration for topic and intent detection."""
    messages: List[str] = Field(..., min_items=1)
    detect_topics: bool = Field(default=True)
    detect_intents: bool = Field(default=True)
    min_confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    max_topics: int = Field(default=5, ge=1, le=10)
    max_intents: int = Field(default=3, ge=1, le=10)
    include_context: bool = Field(default=True)
    
    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v):
        """Validate messages list."""
        if not v:
            raise ValueError(EMPTY_MESSAGES_ERROR)
        
        # Filter out empty messages
        valid_messages = [str(msg).strip() for msg in v if str(msg).strip()]
        if not valid_messages:
            raise ValueError(NO_VALID_MESSAGES_ERROR)
        
        return valid_messages

class ActionDetectionConfig(BaseModel):
    """Configuration for action item detection."""
    messages: List[str] = Field(..., min_items=1)
    include_context: bool = Field(default=True)
    extract_priority: bool = Field(default=True)
    extract_assignee: bool = Field(default=True)
    extract_due_date: bool = Field(default=True)
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    
    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v):
        """Validate messages list."""
        if not v:
            raise ValueError(EMPTY_MESSAGES_ERROR)
        
        # Filter out empty messages
        valid_messages = [str(msg).strip() for msg in v if str(msg).strip()]
        if not valid_messages:
            raise ValueError(NO_VALID_MESSAGES_ERROR)
        
        return valid_messages