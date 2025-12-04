"""
API endpoint for managing MCP tool selection configuration
"""

from python.helpers.api import ApiHandler, Request, Response
from python.helpers.mcp_config import get_mcp_config_dict, update_mcp_config


class McpToolSelectionConfigGet(ApiHandler):
    """Get current MCP tool selection configuration"""
    
    async def process(self, input: dict, request: Request) -> dict | Response:
        try:
            config = get_mcp_config_dict()
            return {"success": True, "config": config}
        except Exception as e:
            return {"success": False, "error": str(e)}


class McpToolSelectionConfigUpdate(ApiHandler):
    """Update MCP tool selection configuration"""
    
    async def process(self, input: dict, request: Request) -> dict | Response:
        try:
            # Validate arguments
            if "max_tools_in_prompt" in input:
                max_tools = input["max_tools_in_prompt"]
                if not isinstance(max_tools, int) or max_tools < 1 or max_tools > 50:
                    return {"success": False, "error": "max_tools_in_prompt must be an integer between 1 and 50"}
            
            if "min_relevance_threshold" in input:
                threshold = input["min_relevance_threshold"]
                if not isinstance(threshold, (int, float)) or threshold < 0.0 or threshold > 1.0:
                    return {"success": False, "error": "min_relevance_threshold must be a number between 0.0 and 1.0"}
            
            if "cache_ttl_hours" in input:
                ttl = input["cache_ttl_hours"]
                if not isinstance(ttl, int) or ttl < 1 or ttl > 24:
                    return {"success": False, "error": "cache_ttl_hours must be an integer between 1 and 24"}
            
            # Update configuration
            update_mcp_config(input)
            
            # Return updated configuration
            new_config = get_mcp_config_dict()
            return {"success": True, "config": new_config}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class McpToolSelectionTest(ApiHandler):
    """Test intelligent tool selection with a sample message"""
    
    async def process(self, input: dict, request: Request) -> dict | Response:
        try:
            user_message = input.get("user_message", "")
            max_tools = input.get("max_tools", 10)
            
            if not user_message.strip():
                return {"success": False, "error": "user_message cannot be empty"}
            
            # Test intelligent tool selection
            from python.helpers.mcp_tool_selector import get_intelligent_mcp_prompt
            
            prompt = get_intelligent_mcp_prompt(user_message, max_tools=max_tools)
            
            # Extract tool count from prompt
            tool_count = 0
            if "###" in prompt:
                tool_count = len(prompt.split("###")) - 2  # Subtract header and empty sections
            
            return {
                "success": True,
                "user_message": user_message,
                "max_tools": max_tools,
                "tool_count": tool_count,
                "prompt_preview": prompt[:1000] + "..." if len(prompt) > 1000 else prompt,
                "full_prompt": prompt
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
