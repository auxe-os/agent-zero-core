import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque

from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle
from agent import LoopData


@dataclass
class ContextState:
    """Tracks the evolving context of the conversation"""
    current_task: str = ""
    task_type: str = "general"
    keywords: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    intent: str = ""
    conversation_stage: str = "beginning"
    previous_tools: List[str] = field(default_factory=list)
    success_indicators: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.entities is None:
            self.entities = []
        if self.previous_tools is None:
            self.previous_tools = []
        if self.success_indicators is None:
            self.success_indicators = []


class ContextEnhancer(Extension):
    """Enhances context analysis for better tool selection"""
    
    def __init__(self):
        """
        Initializes the ContextEnhancer with predefined patterns for intent and
        conversation stage detection.
        """
        self.context_history = deque(maxlen=10)  # Keep last 10 context states
        self.intent_patterns = {
            'search': ['find', 'search', 'look for', 'query', 'lookup'],
            'create': ['create', 'make', 'build', 'generate', 'write', 'develop'],
            'analyze': ['analyze', 'understand', 'explain', 'review', 'examine'],
            'fix': ['fix', 'debug', 'solve', 'repair', 'resolve'],
            'modify': ['modify', 'change', 'update', 'edit', 'improve'],
            'test': ['test', 'validate', 'check', 'verify', 'confirm']
        }
        self.stage_indicators = {
            'beginning': ['hello', 'hi', 'start', 'begin', 'help me'],
            'exploring': ['what', 'how', 'tell me about', 'explain'],
            'implementing': ['do', 'create', 'make', 'implement'],
            'refining': ['improve', 'fix', 'modify', 'change'],
            'completing': ['done', 'finish', 'complete', 'thank']
        }
    
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the context enhancement process.

        This method analyzes the latest user message, enhances it with historical
        context, and stores the enriched data for the tool selector.

        Args:
            loop_data: The current loop data (not directly used but part of the extension signature).
            **kwargs: Arbitrary keyword arguments.
        """
        try:
            # Get current user message
            user_message = self._get_current_user_message()
            if not user_message:
                return
            
            # Analyze current context
            current_context = self._analyze_message_context(user_message)
            
            # Enhance with conversation history
            self._enhance_with_history(current_context)
            
            # Store enhanced context for tool selector
            self._store_enhanced_context(current_context)
            
            # Update context history
            self.context_history.append(current_context)
            
        except Exception as e:
            PrintStyle().print(f"Context enhancement error: {e}")
    
    def _get_current_user_message(self) -> str:
        """
        Retrieves the content of the last user message from the agent.

        Returns:
            The user message as a string, or an empty string if not found.
        """
        try:
            if hasattr(self.agent, 'last_user_message') and self.agent.last_user_message:
                if hasattr(self.agent.last_user_message, 'content'):
                    content = self.agent.last_user_message.content
                    if isinstance(content, str):
                        return content
                    elif isinstance(content, dict) and 'message' in content:
                        return str(content['message'])
        except Exception:
            pass
        return ""
    
    def _analyze_message_context(self, message: str) -> ContextState:
        """
        Analyzes a single message to extract its context.

        This includes keywords, entities, intent, task type, and conversation stage.

        Args:
            message: The message string to analyze.

        Returns:
            A ContextState object representing the analyzed context.
        """
        message_lower = message.lower()
        
        context = ContextState()
        context.current_task = message
        
        # Extract keywords (meaningful words > 3 chars)
        words = re.findall(r'\b\w+\b', message_lower)
        context.keywords = [word for word in words if len(word) > 3 and word.isalpha()]
        
        # Extract entities (proper nouns, capitalized words)
        entities = re.findall(r'\b[A-Z][a-z]+\b', message)
        context.entities = entities
        
        # Determine intent
        context.intent = self._determine_intent(message_lower)
        
        # Determine task type
        context.task_type = self._determine_task_type(message_lower, context.keywords)
        
        # Determine conversation stage
        context.conversation_stage = self._determine_conversation_stage(message_lower)
        
        return context
    
    def _determine_intent(self, message: str) -> str:
        """
        Determines the user's intent based on keywords in the message.

        Args:
            message: The lowercased message string.

        Returns:
            The detected intent (e.g., 'search', 'create') or 'general'.
        """
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in message for keyword in keywords):
                return intent
        return 'general'
    
    def _determine_task_type(self, message: str, keywords: List[str]) -> str:
        """
        Determines the type of task based on keywords in the message.

        Args:
            message: The lowercased message string.
            keywords: A list of keywords from the message.

        Returns:
            The detected task type (e.g., 'search', 'analysis') or 'general'.
        """
        if any(word in message for word in ['search', 'find', 'look for', 'query']):
            return 'search'
        elif any(word in message for word in ['analyze', 'understand', 'explain', 'review']):
            return 'analysis'
        elif any(word in message for word in ['create', 'make', 'build', 'generate', 'write']):
            return 'creation'
        elif any(word in message for word in ['fix', 'debug', 'solve', 'repair']):
            return 'troubleshooting'
        elif any(word in message for word in ['process', 'transform', 'convert', 'format']):
            return 'processing'
        elif any(word in message for word in ['test', 'validate', 'check', 'verify']):
            return 'testing'
        else:
            return 'general'
    
    def _determine_conversation_stage(self, message: str) -> str:
        """
        Determines the current stage of the conversation based on keywords.

        Args:
            message: The lowercased message string.

        Returns:
            The detected stage (e.g., 'beginning', 'exploring') or 'middle'.
        """
        for stage, indicators in self.stage_indicators.items():
            if any(indicator in message for indicator in indicators):
                return stage
        return 'middle'
    
    def _enhance_with_history(self, context: ContextState):
        """
        Enhances the current context by incorporating information from the
        previous context state.

        Args:
            context: The current ContextState object to be enhanced.
        """
        if not self.context_history:
            return
        
        # Get previous context
        previous_context = self.context_history[-1]
        
        # Track task progression
        if previous_context.task_type != context.task_type:
            # Task type changed, might be new phase
            context.success_indicators = previous_context.success_indicators.copy()
        
        # Track tool usage patterns
        context.previous_tools = previous_context.previous_tools.copy()
        
        # Detect task completion indicators
        completion_words = ['done', 'finished', 'complete', 'thank', 'thanks']
        if any(word in context.current_task.lower() for word in completion_words):
            context.success_indicators.append('task_completed')
    
    def _store_enhanced_context(self, context: ContextState):
        """
        Stores the enhanced context data in the agent's context.

        Args:
            context: The enhanced ContextState object.
        """
        if hasattr(self.agent, 'context'):
            # Store as enhanced context data
            enhanced_data = {
                'task_type': context.task_type,
                'intent': context.intent,
                'conversation_stage': context.conversation_stage,
                'keywords': context.keywords,
                'entities': context.entities,
                'previous_tools': context.previous_tools,
                'success_indicators': context.success_indicators,
                'context_confidence': self._calculate_context_confidence(context)
            }
            
            self.agent.context.set_data('enhanced_context', enhanced_data)
    
    def _calculate_context_confidence(self, context: ContextState) -> float:
        """
        Calculates a confidence score for the context analysis.

        The score is based on the number of keywords, clarity of intent, and
        presence of entities.

        Args:
            context: The ContextState object to score.

        Returns:
            A confidence score between 0.0 and 1.0.
        """
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on keyword count
        if len(context.keywords) > 5:
            confidence += 0.2
        elif len(context.keywords) > 2:
            confidence += 0.1
        
        # Boost confidence if intent is clear
        if context.intent != 'general':
            confidence += 0.2
        
        # Boost confidence if entities were found
        if len(context.entities) > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Gets a summary of the current context analysis.

        Returns:
            A dictionary containing key metrics of the current context, or a
            status message if no history is available.
        """
        if not self.context_history:
            return {'status': 'no_context_history'}
        
        current = self.context_history[-1]
        
        return {
            'current_task_type': current.task_type,
            'current_intent': current.intent,
            'conversation_stage': current.conversation_stage,
            'keyword_count': len(current.keywords),
            'entity_count': len(current.entities),
            'context_history_length': len(self.context_history),
            'context_confidence': self._calculate_context_confidence(current)
        }
