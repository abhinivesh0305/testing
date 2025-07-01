"""
Conversational Intelligence Implementation

Core implementation for conversational intelligence capabilities.
Internal module - use ConversationalIntelligence wrapper class instead.
"""

from typing import List, Union, Optional, Dict, Any
import json
import re
from datetime import datetime
from pydantic import ValidationError

# Import logger setup
from elsai_utilities.config.loggerConfig import setup_logger

# Import all validators from validators module
from .validators import (
    FollowupQuestionsResponse,
    GenerationConfig,
    ActionItem,
    ActionDetectionConfig,  # Use ActionDetectionConfig instead of DetectionConfig
    DetectedTopic,
    DetectedIntent,
    TopicIntentResponse,
    TopicIntentDetectionConfig,  # This is the correct one for topics/intents
)


class _ConversationalIntelligenceImplementation:
    """
    Core implementation class for conversational intelligence operations.
    
    This is an internal implementation class. Use ConversationalIntelligence instead.
    """
    
    def __init__(self, llm_instance):
        """Initialize with LLM instance."""
        self._llm = llm_instance
        self.logger = setup_logger()
        self.logger.info("ConversationalIntelligenceImplementation initialized")
    
    # ==================== INTERNAL UTILITY METHODS ====================
    
    @staticmethod
    def _extract_json_content(raw_text: str) -> str:
        """Extract JSON from markdown blocks or return cleaned text."""
        logger = setup_logger()
        logger.debug(f"Extracting JSON content from text of length: {len(raw_text)}")
        
        cleaned = raw_text.strip()
        
        # Handle markdown code blocks
        if cleaned.startswith('```'):
            logger.debug("Processing markdown code block")
            lines = cleaned.split('\n')
            content_lines = []
            inside_block = False
            
            for line in lines:
                if line.strip().startswith('```'):
                    if inside_block:
                        break
                    else:
                        inside_block = True
                        continue
                if inside_block:
                    content_lines.append(line)
            
            result = '\n'.join(content_lines).strip()
            logger.debug(f"Extracted content from markdown block, length: {len(result)}")
            return result
        
        logger.debug("Returning cleaned text without markdown processing")
        return cleaned
    
    def _invoke_llm(self, prompt_text: str) -> str:
        """Internal method to get LLM response."""
        self.logger.debug(f"Invoking LLM with prompt length: {len(prompt_text)}")
        
        try:
            llm_response = self._llm.invoke(prompt_text)
            response_content = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            self.logger.debug(f"LLM response received, length: {len(response_content)}")
            return response_content
            
        except Exception as error:
            self.logger.error(f"LLM invocation failed: {error}")
            raise ValueError(f"LLM invocation failed: {error}")
    
    # ==================== FOLLOW-UP QUESTION GENERATION ====================
    
    def _process_followup_response(self, response_content: str, target_count: int) -> List[str]:
        """Internal method to parse and validate follow-up questions."""
        self.logger.debug(f"Processing followup response for {target_count} questions")
        
        # Define constant for the regex pattern
        ARRAY_PATTERN = r'\[[^\]]*\]'
        
        cleaned_content = self._extract_json_content(response_content)
        
        # Multiple parsing approaches
        parse_methods = [
            # Method 1: Direct JSON parsing
            lambda text: json.loads(text),
            
            # Method 2: Extract array pattern
            lambda text: json.loads(re.search(ARRAY_PATTERN, text, re.DOTALL).group(0)) 
                        if re.search(ARRAY_PATTERN, text, re.DOTALL) else None,
            
            # Method 3: Extract quoted strings
            lambda text: re.findall(r'"([^"]+\??)"', text) if re.findall(r'"([^"]+\??)"', text) else None
        ]
        
        extracted_data = None
        for i, method in enumerate(parse_methods):
            try:
                result = method(cleaned_content)
                if result and isinstance(result, list):
                    extracted_data = result
                    self.logger.debug(f"Successfully parsed using method {i+1}")
                    break
            except (json.JSONDecodeError, AttributeError, TypeError) as e:
                self.logger.debug(f"Parse method {i+1} failed: {e}")
                continue
        
        if not extracted_data:
            self.logger.error(f"Failed to parse followup response: {response_content[:200]}...")
            raise ValueError(f"Failed to parse response: {response_content}")
        
        # Apply Pydantic validation
        try:
            validated = FollowupQuestionsResponse(questions=extracted_data)
            questions = validated.questions
            
            # Adjust to target count
            if len(questions) > target_count:
                questions = questions[:target_count]
                self.logger.debug(f"Trimmed questions from {len(validated.questions)} to {target_count}")
            elif len(questions) < target_count:
                self.logger.warning(f"Expected {target_count} questions but received {len(questions)}")
            
            self.logger.info(f"Successfully processed {len(questions)} followup questions")
            return questions
            
        except ValidationError as validation_err:
            self.logger.error(f"Followup questions validation failed: {validation_err}")
            raise ValueError(f"Validation failed: {validation_err}")
    
    def _generate_followup_questions_internal(
        self,
        original_question: str,
        provided_answer: str,
        conversation_context: Union[str, List[str], None] = None,
        question_count: int = 3
    ) -> List[str]:
        """Internal method for generating follow-up questions."""
        
        self.logger.info(f"Generating {question_count} followup questions")
        self.logger.debug(f"Original question length: {len(original_question)}, Answer length: {len(provided_answer)}")
        
        # Validate inputs using Pydantic
        try:
            config = GenerationConfig(
                num_questions=question_count,
                user_question=original_question,
                answer=provided_answer,
                context=conversation_context
            )
            self.logger.debug("Input validation successful")
        except ValidationError as validation_err:
            self.logger.error(f"Input validation failed: {validation_err}")
            raise ValidationError(f"Invalid parameters: {validation_err}")
        
        # Prepare context section
        context_section = ""
        if config.context:
            if isinstance(config.context, list):
                context_section = "Context:\n" + "\n".join(str(item) for item in config.context)
                self.logger.debug(f"Using list context with {len(config.context)} items")
            else:
                context_section = f"Context:\n{config.context}"
                self.logger.debug("Using string context")
        
        # Construct prompt
        prompt_template = f"""Generate {config.num_questions} thoughtful follow-up questions for this conversation.
User asked: "{config.user_question}"
Assistant answered: "{config.answer}"
{context_section}
Return exactly {config.num_questions} questions as a JSON array of strings. Example format:
["Question 1?", "Question 2?", "Question 3?"]
Requirements:
- Each question must end with a question mark
- Questions should be unique and meaningful
- Focus on helping the user explore the topic deeper or clarify important points
- Avoid repetitive or overly similar questions"""
        
        # Get LLM response
        response_content = self._invoke_llm(prompt_template)
        
        # Process and validate
        questions = self._process_followup_response(response_content, config.num_questions)
        self.logger.info(f"Successfully generated {len(questions)} followup questions")
        return questions
        
    def _generate_followup_questions_safe_internal(
        self,
        original_question: str,
        provided_answer: str,
        conversation_context: Union[str, List[str], None] = None,
        question_count: int = 3,
        backup_questions: Optional[List[str]] = None
    ) -> List[str]:
        """Safe wrapper with fallback questions."""
        self.logger.info(f"Generating followup questions with safe fallback (count: {question_count})")
        
        try:
            return self._generate_followup_questions_internal(
                original_question, provided_answer, conversation_context, question_count
            )
        except ValueError as error:
            self.logger.warning(f"Followup question generation failed, using fallback: {error}")
            
            if backup_questions:
                fallback = backup_questions[:question_count]
                self.logger.info(f"Using provided backup questions: {len(fallback)}")
                return fallback
            
            default_fallback = [
                "Can you elaborate on this topic?",
                "What are the key considerations here?",
                "Are there any related aspects worth exploring?"
            ][:question_count]
            
            self.logger.info(f"Using default fallback questions: {len(default_fallback)}")
            return default_fallback
    
    # ==================== ACTION ITEM DETECTION ====================
    
    def _process_action_items_response(self, response_content: str) -> List[ActionItem]:
        """Internal method to parse action items from LLM response."""
        self.logger.debug("Processing action items response")
        
        # Define constant for the regex pattern
        ARRAY_PATTERN = r'\[[^\]]*\]'
        
        cleaned_content = self._extract_json_content(response_content)
        
        # Multiple parsing strategies
        parse_strategies = [
            # Strategy 1: Direct JSON parsing
            lambda text: json.loads(text),
            
            # Strategy 2: Extract array pattern
            lambda text: json.loads(re.search(ARRAY_PATTERN, text, re.DOTALL).group(0)) 
                        if re.search(ARRAY_PATTERN, text, re.DOTALL) else None,
            
            # Strategy 3: Extract object with action_items key
            lambda text: json.loads(text).get('action_items', []) 
                        if 'action_items' in text else None,
            
            # Strategy 4: Find individual action objects
            lambda text: re.findall(r'\{[^}]*"task"[^}]*\}', text, re.DOTALL)
        ]
        
        extracted_data = self._extract_data_with_strategies(parse_strategies, cleaned_content)
        
        if not extracted_data:
            self.logger.warning("No action items found in response")
            return []  # Return empty list if no data found
        
        # Convert to ActionItem objects
        processed_items = self._convert_to_action_items(extracted_data)
        
        self.logger.info(f"Successfully processed {len(processed_items)} action items")
        return processed_items
    
    def _extract_data_with_strategies(self, strategies, content):
        """Extract data using multiple parsing strategies."""
        for i, strategy in enumerate(strategies):
            try:
                result = strategy(content)
                if result:
                    if isinstance(result, list):
                        self.logger.debug(f"Action items parsed using strategy {i+1}")
                        return result
                    elif isinstance(result, dict):
                        self.logger.debug(f"Single action item parsed using strategy {i+1}")
                        return [result]
            except (json.JSONDecodeError, AttributeError, TypeError) as e:
                self.logger.debug(f"Action items parse strategy {i+1} failed: {e}")
                continue
        return None
    
    def _convert_to_action_items(self, extracted_data):
        """Convert extracted data to ActionItem objects."""
        processed_items = []
        for i, item in enumerate(extracted_data):
            action_item = self._process_single_action_item(item, i)
            if action_item:
                processed_items.append(action_item)
        return processed_items
    
    def _process_single_action_item(self, item, index):
        """Process a single action item."""
        try:
            if isinstance(item, str):
                # Parse string as JSON
                item = json.loads(item)
            
            if isinstance(item, dict):
                action_item = ActionItem(**item)
                self.logger.debug(f"Successfully processed action item {index+1}: {action_item.task}")
                return action_item
        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            self.logger.warning(f"Failed to process action item {index+1}: {e}")
        return None
    
    def _detect_action_items_internal(
        self,
        message_list: Union[List[str], str],
        context_included: bool = True,
        priority_extracted: bool = True,
        assignee_extracted: bool = True,
        due_date_extracted: bool = True,
        confidence_threshold: float = 0.7
    ) -> List[ActionItem]:
        """Internal method for action item detection."""
        
        # Normalize to list
        if isinstance(message_list, str):
            message_list = [message_list]
        
        self.logger.info(f"Detecting action items from {len(message_list)} messages")
        self.logger.debug(f"Config - context: {context_included}, priority: {priority_extracted}, "
                         f"assignee: {assignee_extracted}, due_date: {due_date_extracted}, "
                         f"threshold: {confidence_threshold}")
        
        # Validate parameters
        try:
            config = ActionDetectionConfig(
                messages=message_list,
                include_context=context_included,
                extract_priority=priority_extracted,
                extract_assignee=assignee_extracted,
                extract_due_date=due_date_extracted,
                min_confidence=confidence_threshold
            )
            self.logger.debug("Action detection config validation successful")
        except ValidationError as validation_err:
            self.logger.error(f"Action detection config validation failed: {validation_err}")
            raise ValidationError(f"Invalid parameters: {validation_err}")
        
        # Build conversation text
        conversation_content = "\n".join([f"Message {i+1}: {msg}" for i, msg in enumerate(config.messages)])
        
        # Determine fields to extract
        extraction_fields = ["task"]
        if config.extract_assignee:
            extraction_fields.append("assignee")
        if config.extract_due_date:
            extraction_fields.append("due")
        if config.extract_priority:
            extraction_fields.append("priority")
        if config.include_context:
            extraction_fields.append("context")
        
        extraction_fields.append("source_message")
        self.logger.debug(f"Extracting fields: {extraction_fields}")
        
        prompt_template = f"""Analyze the following conversation messages and extract any action items or tasks that need to be completed.

Conversation:
{conversation_content}

For each action item found, extract the following information as JSON:
- task: Clear description of what needs to be done
- assignee: Person assigned (if mentioned, otherwise empty string)
- due: Due date or deadline (if mentioned, otherwise empty string)
- priority: Priority level - high/medium/low (if indicated, otherwise empty string)
- context: Additional context or notes (if relevant, otherwise empty string)
- source_message: The original message containing this action item

Return a JSON array of action item objects. If no action items are found, return an empty array [].

Example format:
[
  {{
    "task": "Draft budget presentation",
    "assignee": "John",
    "due": "Friday",
    "priority": "high",
    "context": "For quarterly review meeting",
    "source_message": "John, can you draft the budget presentation by Friday for our quarterly review?"
  }}
]

Requirements:
- Only extract clear, actionable tasks
- Ignore casual conversation or statements
- Focus on explicit requests, assignments, or commitments
- Be precise with task descriptions
- Confidence threshold: {config.min_confidence}"""
        
        # Get LLM response
        response_content = self._invoke_llm(prompt_template)
        
        # Process and validate
        action_items = self._process_action_items_response(response_content)
        self.logger.info(f"Detected {len(action_items)} action items")
        return action_items
    
    # ==================== TOPIC AND INTENT DETECTION ====================
    
    def _process_topics_intents_response(self, response_content: str) -> TopicIntentResponse:
        """Internal method to parse topics and intents from LLM response."""
        self.logger.debug("Processing topics and intents response")
        
        # Define constants for regex patterns
        TOPICS_PATTERN = r'"topics"\s*:\s*(\[[^\]]*\])'
        INTENTS_PATTERN = r'"intents"\s*:\s*(\[[^\]]*\])'
        
        cleaned_content = self._extract_json_content(response_content)
        
        # Multiple parsing strategies
        parse_strategies = [
            # Strategy 1: Direct JSON parsing with topics and intents
            lambda text: json.loads(text),
            
            # Strategy 2: Extract JSON object pattern
            lambda text: json.loads(re.search(r'\{.*\}', text, re.DOTALL).group(0)) 
                        if re.search(r'\{.*\}', text, re.DOTALL) else None,
            
            # Strategy 3: Construct from separate arrays
            lambda text: {
                'topics': json.loads(re.search(TOPICS_PATTERN, text, re.DOTALL).group(1))
                         if re.search(TOPICS_PATTERN, text, re.DOTALL) else [],
                'intents': json.loads(re.search(INTENTS_PATTERN, text, re.DOTALL).group(1))
                          if re.search(INTENTS_PATTERN, text, re.DOTALL) else []
            }
        ]
        
        extracted_data = None
        for i, strategy in enumerate(parse_strategies):
            try:
                result = strategy(cleaned_content)
                if result and isinstance(result, dict):
                    extracted_data = result
                    self.logger.debug(f"Topics/intents parsed using strategy {i+1}")
                    break
            except (json.JSONDecodeError, AttributeError, TypeError) as e:
                self.logger.debug(f"Topics/intents parse strategy {i+1} failed: {e}")
                continue
        
        if not extracted_data:
            self.logger.warning("No topics/intents found in response, returning empty result")
            return TopicIntentResponse(topics=[], intents=[])
        
        # Ensure expected structure
        if 'topics' not in extracted_data:
            extracted_data['topics'] = []
        if 'intents' not in extracted_data:
            extracted_data['intents'] = []
        
        try:
            result = TopicIntentResponse(**extracted_data)
            self.logger.info(f"Successfully processed {len(result.topics)} topics and {len(result.intents)} intents")
            return result
        except ValidationError as e:
            self.logger.error(f"Topics/intents validation failed: {e}")
            return TopicIntentResponse(topics=[], intents=[])  
          
    def _detect_topics_and_intents_internal(
        self,
        message_list: Union[List[str], str],
        topics_detected: bool = True,
        intents_detected: bool = True,
        confidence_threshold: float = 0.6,
        topic_limit: int = 5,
        intent_limit: int = 3,
        context_included: bool = True
    ) -> TopicIntentResponse:
        """Internal method for topic and intent detection."""
        
        # Normalize to list
        if isinstance(message_list, str):
            message_list = [message_list]
        
        self.logger.info(f"Detecting topics and intents from {len(message_list)} messages")
        self.logger.debug(f"Config - topics: {topics_detected}, intents: {intents_detected}, "
                         f"threshold: {confidence_threshold}, topic_limit: {topic_limit}, "
                         f"intent_limit: {intent_limit}, context: {context_included}")
        
        # Validate parameters
        try:
            config = TopicIntentDetectionConfig(
                messages=message_list,
                detect_topics=topics_detected,
                detect_intents=intents_detected,
                min_confidence=confidence_threshold,
                max_topics=topic_limit,
                max_intents=intent_limit,
                include_context=context_included
            )
            self.logger.debug("Topic/intent detection config validation successful")
        except ValidationError as validation_err:
            self.logger.error(f"Topic/intent detection config validation failed: {validation_err}")
            raise ValidationError(f"Invalid parameters: {validation_err}")
        
        # Build conversation text
        conversation_content = "\n".join([f"Message {i+1}: {msg}" for i, msg in enumerate(config.messages)])
        
        # Build detection instructions
        detection_parts = []
        
        if config.detect_topics:
            detection_parts.append(f"""
Topics: Identify up to {config.max_topics} main topics discussed. For each topic, provide:
- name: Clear, concise topic name
- confidence: Confidence score (0.0-1.0)  
- keywords: List of relevant keywords (max 5)
- category: Broader category if applicable
- context: Brief context where topic appeared""")
        
        if config.detect_intents:
            detection_parts.append(f"""
Intents: Identify up to {config.max_intents} user intents. For each intent, provide:
- intent: Intent name (e.g., ask_question, make_request, seek_information)
- confidence: Confidence score (0.0-1.0)
- entities: Key entities mentioned (as key-value pairs)
- intent_type: Type (question, request, command, information, greeting, complaint, compliment, booking, support, general)
- context: Brief context
- source_message: Original message containing the intent""")
        
        prompt_template = f"""Analyze the following conversation messages and detect topics and intents.

Conversation:
{conversation_content}

{' '.join(detection_parts)}

Return a JSON object with this structure:
{{
  "topics": [
    {{
      "name": "Topic Name",
      "confidence": 0.85,
      "keywords": ["keyword1", "keyword2"],
      "category": "Category",
      "context": "Context description"
    }}
  ],
  "intents": [
    {{
      "intent": "intent_name",
      "confidence": 0.90,
      "entities": {{"entity_type": "entity_value"}},
      "intent_type": "question",
      "context": "Context description",
      "source_message": "Original message"
    }}
  ]
}}

Requirements:
- Only include topics/intents with confidence >= {config.min_confidence}
- Be precise and avoid overly broad classifications
- Focus on the most significant and clear topics/intents
- If no clear topics or intents are found, return empty arrays"""
        
        # Get LLM response
        response_content = self._invoke_llm(prompt_template)
        
        # Process and validate
        result = self._process_topics_intents_response(response_content)
        
        # Apply limits
        if len(result.topics) > config.max_topics:
            original_count = len(result.topics)
            result.topics = result.topics[:config.max_topics]
            self.logger.debug(f"Trimmed topics from {original_count} to {config.max_topics}")
            
        if len(result.intents) > config.max_intents:
            original_count = len(result.intents)
            result.intents = result.intents[:config.max_intents]
            self.logger.debug(f"Trimmed intents from {original_count} to {config.max_intents}")
        
        self.logger.info(f"Final result: {len(result.topics)} topics, {len(result.intents)} intents")
        return result
    
    def _detect_topics_only_internal(
        self,
        message_list: Union[List[str], str],
        confidence_threshold: float = 0.6,
        topic_limit: int = 5,
        context_included: bool = True
    ) -> List[DetectedTopic]:
        """Internal method to detect only topics."""
        self.logger.info("Detecting topics only")
        
        result = self._detect_topics_and_intents_internal(
            message_list=message_list,
            topics_detected=True,
            intents_detected=False,
            confidence_threshold=confidence_threshold,
            topic_limit=topic_limit,
            context_included=context_included
        )
        
        self.logger.info(f"Detected {len(result.topics)} topics only")
        return result.topics
    
    def _detect_intents_only_internal(
        self,
        message_list: Union[List[str], str],
        confidence_threshold: float = 0.6,
        intent_limit: int = 3,
        context_included: bool = True
    ) -> List[DetectedIntent]:
        """Internal method to detect only intents."""
        self.logger.info("Detecting intents only")
        
        result = self._detect_topics_and_intents_internal(
            message_list=message_list,
            topics_detected=False,
            intents_detected=True,
            confidence_threshold=confidence_threshold,
            intent_limit=intent_limit,
            context_included=context_included
        )
        
        self.logger.info(f"Detected {len(result.intents)} intents only")
        return result.intents
    
    # ==================== COMPREHENSIVE ANALYSIS ====================
    
    def _analyze_conversation_internal(
        self,
        message_list: Union[List[str], str],
        followup_included: bool = True,
        actions_included: bool = True,
        topics_included: bool = True,
        intents_included: bool = True,
        **additional_params
    ) -> Dict[str, Any]:
        """Internal method for comprehensive conversation analysis."""
        analysis_results = {}
        
        # Normalize to list
        if isinstance(message_list, str):
            message_list = [message_list]
        
        self.logger.info(f"Starting comprehensive analysis of {len(message_list)} messages")
        self.logger.debug(f"Analysis options - followup: {followup_included}, actions: {actions_included}, "
                         f"topics: {topics_included}, intents: {intents_included}")
        
        try:
            # Action item detection
            if actions_included:
                self._analyze_action_items(analysis_results, message_list, additional_params)
            
            # Topic and intent detection
            if topics_included or intents_included:
                self._analyze_topics_and_intents(analysis_results, message_list, topics_included, intents_included, additional_params)
            
            # Follow-up questions
            if followup_included:
                self._analyze_followup_questions(analysis_results, message_list, additional_params)
        
        except Exception as error:
            self.logger.error(f"Error during comprehensive analysis: {error}")
            analysis_results['error'] = str(error)
        
        self.logger.info("Comprehensive analysis completed")
        return analysis_results
    
    def _analyze_action_items(self, analysis_results, message_list, additional_params):
        """Analyze action items from messages."""
        self.logger.debug("Starting action item detection")
        analysis_results['action_items'] = self._detect_action_items_internal(
            message_list, 
            **{k: v for k, v in additional_params.items() if k in ['context_included', 'priority_extracted', 'assignee_extracted', 'due_date_extracted', 'confidence_threshold']}
        )
        self.logger.debug(f"Action item detection completed: {len(analysis_results['action_items'])} items")
    
    def _analyze_topics_and_intents(self, analysis_results, message_list, topics_included, intents_included, additional_params):
        """Analyze topics and intents from messages."""
        self.logger.debug("Starting topic/intent detection")
        topic_intent_result = self._detect_topics_and_intents_internal(
            message_list,
            topics_detected=topics_included,
            intents_detected=intents_included,
            **{k: v for k, v in additional_params.items() if k in ['confidence_threshold', 'topic_limit', 'intent_limit', 'context_included']}
        )
        
        if topics_included:
            analysis_results['topics'] = topic_intent_result.topics
            self.logger.debug(f"Topic detection completed: {len(analysis_results['topics'])} topics")
        if intents_included:
            analysis_results['intents'] = topic_intent_result.intents
            self.logger.debug(f"Intent detection completed: {len(analysis_results['intents'])} intents")
    
    def _analyze_followup_questions(self, analysis_results, message_list, additional_params):
        """Analyze and generate followup questions from messages."""
        if len(message_list) >= 2:
            self.logger.debug("Starting followup question generation")
            # Use last two messages as question and answer
            user_question = message_list[-2] if len(message_list) >= 2 else message_list[-1]
            answer = message_list[-1]
            
            analysis_results['followup_questions'] = self._generate_followup_questions_safe_internal(
                original_question=user_question,
                provided_answer=answer,
                conversation_context=message_list[:-2] if len(message_list) > 2 else None,
                **{k: v for k, v in additional_params.items() if k in ['question_count']}
            )
            self.logger.debug(f"Followup question generation completed: {len(analysis_results['followup_questions'])} questions")
        else:
            self.logger.warning("Followup questions requested but insufficient messages (need at least 2)")
    
    def _get_conversation_summary_internal(
        self,
        message_list: Union[List[str], str],
        **additional_params
    ) -> Dict[str, Any]:
        """Internal method to get conversation summary."""
        self.logger.info("Generating conversation summary")
        
        analysis = self._analyze_conversation_internal(message_list, **additional_params)
        
        summary = {
            'message_count': len(message_list) if isinstance(message_list, list) else 1,
            'action_items_count': len(analysis.get('action_items', [])),
            'topics_count': len(analysis.get('topics', [])),
            'intents_count': len(analysis.get('intents', [])),
            'followup_questions_count': len(analysis.get('followup_questions', [])),
        }
        
        # Add primary findings
        if 'topics' in analysis and analysis['topics']:
            summary['primary_topic'] = analysis['topics'][0].name
            summary['topic_confidence'] = analysis['topics'][0].confidence
            self.logger.debug(f"Primary topic: {summary['primary_topic']} (confidence: {summary['topic_confidence']})")
        
        if 'intents' in analysis and analysis['intents']:
            summary['primary_intent'] = analysis['intents'][0].intent
            summary['intent_confidence'] = analysis['intents'][0].confidence
            self.logger.debug(f"Primary intent: {summary['primary_intent']} (confidence: {summary['intent_confidence']})")
        
        if 'action_items' in analysis and analysis['action_items']:
            summary['has_urgent_actions'] = any(
                item.priority.lower() == 'high' for item in analysis['action_items']
            )
            self.logger.debug(f"Has urgent actions: {summary['has_urgent_actions']}")
        
        self.logger.info(f"Summary generated - {summary['message_count']} messages, "
                        f"{summary['action_items_count']} actions, {summary['topics_count']} topics, "
                        f"{summary['intents_count']} intents, {summary['followup_questions_count']} followup questions")
        
        return summary