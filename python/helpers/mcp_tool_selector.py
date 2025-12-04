"""
Intelligent MCP Tool Selection System

This module provides context-aware tool selection capabilities for MCP servers,
analyzing tool capabilities and dynamically selecting the most relevant tools
based on the current task context.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import threading
from datetime import datetime, timedelta

from python.helpers.print_style import PrintStyle
from python.helpers.mcp_handler import MCPConfig


@dataclass
class ToolCapability:
    """Represents a tool's capabilities and metadata"""
    name: str
    server: str
    description: str
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class ToolContext:
    """Represents the current task context"""
    user_message: str = ""
    task_type: str = ""
    keywords: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    excluded_categories: List[str] = field(default_factory=list)


class ToolCapabilityAnalyzer:
    """Analyzes MCP tools to extract capabilities and categorize them"""
    
    # Predefined categories and their keywords
    CATEGORIES = {
        "web_search": ["search", "web", "internet", "find", "lookup", "query", "browse"],
        "code_analysis": ["code", "analyze", "repository", "github", "documentation", "examples"],
        "file_operations": ["file", "read", "write", "create", "delete", "directory", "folder"],
        "data_processing": ["data", "process", "transform", "parse", "format", "convert"],
        "communication": ["send", "message", "notify", "email", "slack", "chat"],
        "system": ["system", "execute", "run", "command", "shell", "process"],
        "ai_ml": ["ai", "ml", "model", "predict", "classify", "generate"],
        "database": ["database", "db", "query", "sql", "store", "retrieve"],
        "api": ["api", "request", "fetch", "http", "rest", "endpoint"],
        "content": ["content", "text", "markdown", "document", "article"],
        "research": ["research", "investigate", "study", "analyze", "report"],
        "automation": ["automate", "workflow", "pipeline", "schedule", "trigger"],
    }
    
    def __init__(self):
        self._capability_cache: Dict[str, ToolCapability] = {}
        self._cache_lock = threading.Lock()
        self._cache_timestamp: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(hours=1)  # Cache for 1 hour
    
    def analyze_tool(self, tool: Dict[str, Any], server_name: str) -> ToolCapability:
        """Analyze a single tool to extract its capabilities"""
        tool_name = tool.get('name', '')
        tool_key = f"{server_name}.{tool_name}"
        
        # Check cache first
        with self._cache_lock:
            if tool_key in self._capability_cache:
                timestamp = self._cache_timestamp.get(tool_key, datetime.min)
                if datetime.now() - timestamp < self._cache_ttl:
                    return self._capability_cache[tool_key]
        
        # Extract information from tool schema
        description = tool.get('description', '')
        input_schema = tool.get('input_schema', {})
        
        # Analyze capabilities
        categories = self._categorize_tool(tool_name, description, input_schema)
        keywords = self._extract_keywords(tool_name, description, input_schema)
        input_types = self._extract_input_types(input_schema)
        output_types = self._extract_output_types(description)
        use_cases = self._extract_use_cases(description)
        
        capability = ToolCapability(
            name=tool_name,
            server=server_name,
            description=description,
            categories=categories,
            keywords=keywords,
            input_types=input_types,
            output_types=output_types,
            use_cases=use_cases,
            confidence_score=self._calculate_confidence(categories, keywords)
        )
        
        # Cache the result
        with self._cache_lock:
            self._capability_cache[tool_key] = capability
            self._cache_timestamp[tool_key] = datetime.now()
        
        return capability
    
    def _categorize_tool(self, name: str, description: str, input_schema: Dict) -> List[str]:
        """Categorize the tool based on its name, description, and schema"""
        text = f"{name} {description}".lower()
        categories = []
        
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        # Analyze input schema for additional clues
        schema_str = json.dumps(input_schema).lower()
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in schema_str for keyword in keywords):
                if category not in categories:
                    categories.append(category)
        
        return categories or ["general"]
    
    def _extract_keywords(self, name: str, description: str, input_schema: Dict) -> List[str]:
        """Extract relevant keywords from tool information"""
        text = f"{name} {description}".lower()
        
        # Extract words that are likely meaningful
        words = re.findall(r'\b\w+\b', text)
        
        # Filter out common words and keep relevant ones
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'a', 'an', 'as', 'if', 'then', 'else', 'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'}
        
        keywords = [word for word in words if len(word) > 2 and word not in common_words]
        
        # Extract property names from input schema
        if 'properties' in input_schema:
            for prop_name in input_schema['properties'].keys():
                keywords.append(prop_name.lower())
        
        return list(set(keywords))
    
    def _extract_input_types(self, input_schema: Dict) -> List[str]:
        """Extract input data types from schema"""
        types = []
        
        if 'type' in input_schema:
            types.append(input_schema['type'])
        
        if 'properties' in input_schema:
            for prop in input_schema['properties'].values():
                if 'type' in prop:
                    types.append(prop['type'])
                if 'enum' in prop:
                    types.append('enum')
        
        return list(set(types))
    
    def _extract_output_types(self, description: str) -> List[str]:
        """Extract output data types from description"""
        text = description.lower()
        output_types = []
        
        if any(word in text for word in ['json', 'object', 'data']):
            output_types.append('json')
        if any(word in text for word in ['text', 'string', 'content']):
            output_types.append('text')
        if any(word in text for word in ['list', 'array', 'results']):
            output_types.append('array')
        if any(word in text for word in ['number', 'int', 'float', 'count']):
            output_types.append('number')
        if any(word in text for word in ['boolean', 'true', 'false']):
            output_types.append('boolean')
        
        return output_types or ['text']
    
    def _extract_use_cases(self, description: str) -> List[str]:
        """Extract potential use cases from description"""
        # Look for action phrases and patterns
        use_cases = []
        
        # Common patterns
        patterns = [
            r'used to (\w+)',
            r'(\w+) the',
            r'(\w+) a',
            r'(\w+) an',
            r'can (\w+)',
            r'allows you to (\w+)',
            r'helps (\w+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description.lower())
            use_cases.extend(matches)
        
        return list(set(use_cases))
    
    def _calculate_confidence(self, categories: List[str], keywords: List[str]) -> float:
        """Calculate confidence score for the analysis"""
        base_score = 0.5
        
        # More categories = higher confidence (to a point)
        category_bonus = min(len(categories) * 0.1, 0.3)
        
        # More keywords = higher confidence (to a point)
        keyword_bonus = min(len(keywords) * 0.02, 0.2)
        
        return min(base_score + category_bonus + keyword_bonus, 1.0)


class ContextAwareToolSelector:
    """Selects relevant tools based on task context"""
    
    def __init__(self):
        self.analyzer = ToolCapabilityAnalyzer()
        self._context_cache: Dict[str, List[ToolCapability]] = {}
        self._cache_lock = threading.Lock()
    
    def analyze_context(self, user_message: str, task_history: Optional[List[str]] = None) -> ToolContext:
        """Analyze the current task context"""
        context = ToolContext()
        context.user_message = user_message.lower()
        
        # Extract keywords from user message
        words = re.findall(r'\b\w+\b', context.user_message)
        context.keywords = [word for word in words if len(word) > 3]
        
        # Determine task type based on keywords
        context.task_type = self._determine_task_type(context.user_message, context.keywords)
        
        # Extract required capabilities
        context.required_capabilities = self._extract_required_capabilities(context.user_message)
        
        return context
    
    def select_tools(self, context: ToolContext, max_tools: int = 10) -> List[ToolCapability]:
        """Select the most relevant tools for the given context"""
        # Get all available tools
        mcp_config = MCPConfig.get_instance()
        all_tools = []
        
        for server in mcp_config.servers:
            try:
                server_tools = server.get_tools()
                for tool in server_tools:
                    capability = self.analyzer.analyze_tool(tool, server.name)
                    all_tools.append(capability)
            except Exception as e:
                PrintStyle().print(f"Error analyzing tools from server {server.name}: {e}")
        
        # Score tools based on relevance
        scored_tools = []
        for tool in all_tools:
            score = self._calculate_relevance_score(tool, context)
            if score > 0.1:  # Only consider tools with some relevance
                scored_tools.append((tool, score))
        
        # Sort by score and return top tools
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, score in scored_tools[:max_tools]]
    
    def _determine_task_type(self, message: str, keywords: List[str]) -> str:
        """Determine the type of task based on the message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['search', 'find', 'look for', 'query']):
            return 'search'
        elif any(word in message_lower for word in ['analyze', 'understand', 'explain', 'review']):
            return 'analysis'
        elif any(word in message_lower for word in ['create', 'make', 'build', 'generate', 'write']):
            return 'creation'
        elif any(word in message_lower for word in ['fix', 'debug', 'solve', 'repair']):
            return 'troubleshooting'
        elif any(word in message_lower for word in ['process', 'transform', 'convert', 'format']):
            return 'processing'
        elif any(word in message_lower for word in ['test', 'validate', 'check', 'verify']):
            return 'testing'
        else:
            return 'general'
    
    def _extract_required_capabilities(self, message: str) -> List[str]:
        """Extract required capabilities from the message"""
        capabilities = []
        message_lower = message.lower()
        
        # Look for capability indicators
        if any(word in message_lower for word in ['web', 'internet', 'online', 'website']):
            capabilities.append('web_search')
        if any(word in message_lower for word in ['code', 'programming', 'software', 'app']):
            capabilities.append('code_analysis')
        if any(word in message_lower for word in ['file', 'document', 'data']):
            capabilities.append('file_operations')
        if any(word in message_lower for word in ['research', 'study', 'investigate']):
            capabilities.append('research')
        
        return capabilities
    
    def _calculate_relevance_score(self, tool: ToolCapability, context: ToolContext) -> float:
        """Calculate relevance score for a tool given the context"""
        score = 0.0
        
        # Category matching
        for category in tool.categories:
            if category in context.required_capabilities:
                score += 0.4
            elif context.task_type == 'search' and category == 'web_search':
                score += 0.3
            elif context.task_type == 'analysis' and category in ['code_analysis', 'research']:
                score += 0.3
            elif context.task_type == 'creation' and category in ['content', 'ai_ml']:
                score += 0.3
        
        # Keyword matching
        keyword_matches = len(set(tool.keywords) & set(context.keywords))
        score += keyword_matches * 0.1
        
        # Use case matching
        for use_case in tool.use_cases:
            if use_case in context.user_message:
                score += 0.2
        
        # Boost based on confidence score
        score *= tool.confidence_score
        
        return min(score, 1.0)


class DynamicToolPromptGenerator:
    """Generates dynamic tool prompts based on selected tools"""
    
    def generate_prompt(self, selected_tools: List[ToolCapability], context: ToolContext) -> str:
        """Generate a focused prompt with only relevant tools"""
        if not selected_tools:
            return "## No relevant MCP tools available for this task.\n"
        
        prompt = '## "Intelligently Selected MCP Tools" for your task:\n\n'
        prompt += f"**Task Context:** {context.task_type} task with keywords: {', '.join(context.keywords[:5])}\n\n"
        
        # Group tools by category
        tools_by_category = defaultdict(list)
        for tool in selected_tools:
            for category in tool.categories:
                tools_by_category[category].append(tool)
        
        for category, tools in tools_by_category.items():
            prompt += f"### {category.replace('_', ' ').title()} Tools\n\n"
            
            for tool in tools:
                prompt += f"#### **{tool.server}.{tool.name}**\n"
                prompt += f"{tool.description}\n\n"
                
                # Add capability insights
                if tool.use_cases:
                    prompt += f"**Use Cases:** {', '.join(tool.use_cases[:3])}\n\n"
                
                # Add input/output information
                if tool.input_types:
                    prompt += f"**Input Types:** {', '.join(tool.input_types)}\n\n"
                
                if tool.output_types:
                    prompt += f"**Output Types:** {', '.join(tool.output_types)}\n\n"
                
                # Add relevance score
                prompt += f"**Relevance:** {tool.confidence_score:.2f}\n\n"
                
                prompt += "---\n\n"
        
        # Add usage guidance
        prompt += "### Usage Guidance\n"
        prompt += f"Based on your {context.task_type} task, these tools are most relevant. "
        prompt += "Start with the highest relevance tools and consider the use cases listed above.\n"
        
        return prompt


# Main integration function
def get_intelligent_mcp_prompt(user_message: str = "", max_tools: int = 10) -> str:
    """Get an intelligent MCP tools prompt based on the current context"""
    try:
        selector = ContextAwareToolSelector()
        
        # Analyze context
        context = selector.analyze_context(user_message)
        
        # Select relevant tools
        selected_tools = selector.select_tools(context, max_tools)
        
        # Generate dynamic prompt
        generator = DynamicToolPromptGenerator()
        return generator.generate_prompt(selected_tools, context)
        
    except Exception as e:
        PrintStyle().print(f"Error generating intelligent MCP prompt: {e}")
        # Fallback to static prompt
        return MCPConfig.get_instance().get_tools_prompt()


# Utility function for backward compatibility
def get_mcp_tools_with_intelligence(user_message: str = "", max_tools: int = 10) -> str:
    """Get MCP tools prompt with intelligent selection (backward compatible)"""
    return get_intelligent_mcp_prompt(user_message, max_tools)
