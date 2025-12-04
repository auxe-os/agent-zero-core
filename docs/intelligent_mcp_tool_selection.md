# Intelligent MCP Tool Selection

This document describes the intelligent MCP tool selection system that enhances the agent's ability to dynamically select and utilize the most relevant tools based on task context.

## Overview

The traditional approach dumps all available MCP tools into the agent's prompt, which can be overwhelming and inefficient. The intelligent tool selection system analyzes tool capabilities, categorizes them, and dynamically selects the most relevant tools for each specific task.

## Key Features

### 1. Capability Analysis
- **Tool Categorization**: Automatically categorizes tools into predefined categories (web_search, code_analysis, file_operations, etc.)
- **Keyword Extraction**: Extracts relevant keywords from tool names, descriptions, and schemas
- **Input/Output Type Analysis**: Analyzes tool schemas to understand data types
- **Use Case Identification**: Identifies potential use cases from tool descriptions
- **Confidence Scoring**: Calculates confidence scores for tool analysis accuracy

### 2. Context-Aware Selection
- **Task Type Detection**: Analyzes user messages to determine task type (search, analysis, creation, etc.)
- **Keyword Matching**: Matches user message keywords with tool capabilities
- **Relevance Scoring**: Scores tools based on relevance to the current context
- **Dynamic Filtering**: Filters tools based on minimum relevance thresholds

### 3. Dynamic Prompt Generation
- **Focused Prompts**: Generates prompts with only the most relevant tools
- **Categorized Organization**: Groups tools by category for better organization
- **Usage Guidance**: Includes use cases and capability information
- **Confidence Indicators**: Shows confidence scores for tool recommendations

## Architecture

### Core Components

#### 1. ToolCapabilityAnalyzer
```python
class ToolCapabilityAnalyzer:
    """Analyzes MCP tools to extract capabilities and categorize them"""
```

**Responsibilities:**
- Parse tool schemas and descriptions
- Extract and categorize capabilities
- Calculate confidence scores
- Cache analysis results for performance

#### 2. ContextAwareToolSelector
```python
class ContextAwareToolSelector:
    """Selects relevant tools based on task context"""
```

**Responsibilities:**
- Analyze user message context
- Determine task types and required capabilities
- Score and rank tools by relevance
- Select top N most relevant tools

#### 3. DynamicToolPromptGenerator
```python
class DynamicToolPromptGenerator:
    """Generates dynamic tool prompts based on selected tools"""
```

**Responsibilities:**
- Generate focused prompts with selected tools
- Organize tools by category
- Include usage guidance and confidence scores
- Format prompts for optimal agent understanding

### Configuration System

#### MCPToolSelectionConfig
```python
@dataclass
class MCPToolSelectionConfig:
    enable_intelligent_selection: bool = True
    max_tools_in_prompt: int = 15
    min_relevance_threshold: float = 0.1
    enable_caching: bool = True
    fallback_to_static: bool = True
    debug_mode: bool = False
```

## Usage

### Basic Integration

The system is automatically integrated into the agent's prompt generation process:

```python
# In python/extensions/system_prompt/_10_system_prompt.py
def get_mcp_tools_prompt(agent: Agent):
    # Automatically uses intelligent selection if enabled
    # Falls back to static prompt if disabled or on error
```

### Configuration

Configure the system through settings:

```json
{
  "mcp": {
    "enable_intelligent_selection": true,
    "max_tools_in_prompt": 15,
    "min_relevance_threshold": 0.1,
    "enable_caching": true,
    "cache_ttl_hours": 1,
    "fallback_to_static": true,
    "include_confidence_scores": true,
    "include_use_cases": true,
    "group_by_category": true,
    "debug_mode": false
  }
}
```

### API Endpoints

#### Get Configuration
```python
GET /api/mcp_tool_selection_config_get
```

#### Update Configuration
```python
POST /api/mcp_tool_selection_config_update
{
  "enable_intelligent_selection": true,
  "max_tools_in_prompt": 10
}
```

#### Test Tool Selection
```python
POST /api/mcp_tool_selection_test
{
  "user_message": "Search for information about Python web frameworks",
  "max_tools": 5
}
```

## Tool Categories

The system recognizes the following predefined categories:

| Category | Description | Example Keywords |
|----------|-------------|------------------|
| web_search | Web searching and information retrieval | search, web, internet, find, lookup |
| code_analysis | Code repository analysis and documentation | code, analyze, repository, github |
| file_operations | File system operations | file, read, write, create, delete |
| data_processing | Data transformation and processing | data, process, transform, parse |
| communication | Messaging and notification systems | send, message, notify, email |
| system | System operations and command execution | system, execute, run, command |
| ai_ml | AI and machine learning operations | ai, ml, model, predict, generate |
| database | Database operations | database, db, query, sql |
| api | API interactions and HTTP requests | api, request, fetch, http |
| content | Content creation and management | content, text, markdown, document |
| research | Research and investigation tasks | research, study, investigate, analyze |
| automation | Automation and workflow management | automate, workflow, pipeline, schedule |

## Performance Considerations

### Caching
- Tool capability analysis results are cached for 1 hour by default
- Cache TTL is configurable via `cache_ttl_hours`
- Caching significantly improves performance for repeated tool analysis

### Relevance Threshold
- Tools with relevance scores below `min_relevance_threshold` are excluded
- Default threshold is 0.1 (10% relevance)
- Higher thresholds reduce prompt size but may miss relevant tools

### Maximum Tools
- `max_tools_in_prompt` limits the number of tools included
- Default is 15 tools maximum
- Balance between comprehensiveness and prompt efficiency

## Debug Mode

Enable debug mode to monitor tool selection behavior:

```python
# Enable debug mode
update_mcp_config({"debug_mode": True})
```

Debug mode provides:
- Tool selection counts
- Context analysis results
- Fallback notifications
- Performance metrics

## Error Handling

The system includes robust error handling:

1. **Graceful Degradation**: Falls back to static prompts if intelligent selection fails
2. **Import Error Handling**: Works even if tool selector module is unavailable
3. **Configuration Validation**: Validates configuration parameters
4. **Performance Monitoring**: Tracks and reports performance issues

## Examples

### Example 1: Web Search Task
**User Message**: "Search for information about React hooks"

**Selected Tools**:
- `exa.web_search_exa` (web_search category, high relevance)
- `exa.get_code_context_exa` (code_analysis category, medium relevance)

**Generated Prompt**:
```
## "Intelligently Selected MCP Tools" for your task:

**Task Context:** search task with keywords: search, information, react, hooks

### Web Search Tools

#### **exa.web_search_exa**
Real-time web search using Exa AI
**Use Cases:** search, find, lookup
**Input Types:** string
**Output Types:** json, text
**Relevance:** 0.85
```

### Example 2: Code Analysis Task
**User Message**: "Analyze this Python code for performance issues"

**Selected Tools**:
- `exa.get_code_context_exa` (code_analysis category, high relevance)
- `github.code_search` (code_analysis category, medium relevance)

### Example 3: No Relevant Tools
**User Message**: "Tell me a joke"

**Result**: Falls back to static prompt or returns "No relevant MCP tools found"

## Best Practices

1. **Configuration**: Tune `max_tools_in_prompt` and `min_relevance_threshold` based on your use case
2. **Monitoring**: Enable debug mode during development to monitor selection quality
3. **Categories**: Ensure tool descriptions include relevant keywords for better categorization
4. **Performance**: Monitor cache hit rates and adjust TTL as needed
5. **Testing**: Use the test API endpoint to validate tool selection for different scenarios

## Troubleshooting

### Common Issues

1. **No Tools Selected**: Check if `min_relevance_threshold` is too high
2. **Poor Categorization**: Improve tool descriptions with relevant keywords
3. **Performance Issues**: Enable caching and adjust TTL settings
4. **Fallback to Static**: Check error logs and debug output

### Debug Information

Enable debug mode to get detailed information about:
- Context analysis results
- Tool relevance scores
- Selection decisions
- Performance metrics

## Future Enhancements

Potential future improvements:
1. **Learning System**: Machine learning to improve relevance scoring
2. **Custom Categories**: User-defined tool categories
3. **Usage Analytics**: Track tool usage patterns to improve selection
4. **A/B Testing**: Compare intelligent vs static selection performance
5. **Tool Recommendations**: Suggest tools based on historical usage patterns
