"""
MCP Configuration and Settings Management

This module provides configuration management for MCP tool selection,
including settings for intelligent tool selection and fallback options.
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from python.helpers.settings import get_settings


@dataclass
class MCPToolSelectionConfig:
    """Configuration for MCP tool selection behavior"""
    
    # Enable/disable intelligent tool selection
    enable_intelligent_selection: bool = True
    
    # Maximum number of tools to include in prompt
    max_tools_in_prompt: int = 15
    
    # Minimum relevance score threshold
    min_relevance_threshold: float = 0.1
    
    # Enable capability caching
    enable_caching: bool = True
    
    # Cache TTL in hours
    cache_ttl_hours: int = 1
    
    # Fallback to static prompt if intelligent selection fails
    fallback_to_static: bool = True
    
    # Include tool confidence scores in prompts
    include_confidence_scores: bool = True
    
    # Include use cases in prompts
    include_use_cases: bool = True
    
    # Group tools by category in prompts
    group_by_category: bool = True
    
    # Debug mode for tool selection
    debug_mode: bool = False


class MCPConfigManager:
    """Manages MCP configuration settings"""
    
    def __init__(self):
        self._config: Optional[MCPToolSelectionConfig] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from settings"""
        try:
            settings = get_settings()
            mcp_settings = settings.get('mcp', {})
            
            self._config = MCPToolSelectionConfig(
                enable_intelligent_selection=mcp_settings.get('enable_intelligent_selection', True),
                max_tools_in_prompt=mcp_settings.get('max_tools_in_prompt', 15),
                min_relevance_threshold=mcp_settings.get('min_relevance_threshold', 0.1),
                enable_caching=mcp_settings.get('enable_caching', True),
                cache_ttl_hours=mcp_settings.get('cache_ttl_hours', 1),
                fallback_to_static=mcp_settings.get('fallback_to_static', True),
                include_confidence_scores=mcp_settings.get('include_confidence_scores', True),
                include_use_cases=mcp_settings.get('include_use_cases', True),
                group_by_category=mcp_settings.get('group_by_category', True),
                debug_mode=mcp_settings.get('debug_mode', False)
            )
        except Exception as e:
            # Fallback to default config if loading fails
            from python.helpers.print_style import PrintStyle
            PrintStyle().print(f"Error loading MCP config, using defaults: {e}")
            self._config = MCPToolSelectionConfig()
    
    def get_config(self) -> MCPToolSelectionConfig:
        """Get the current MCP configuration"""
        return self._config if self._config else MCPToolSelectionConfig()
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        if self._config is None:
            self._config = MCPToolSelectionConfig()
        
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def is_intelligent_selection_enabled(self) -> bool:
        """Check if intelligent tool selection is enabled"""
        return self._config.enable_intelligent_selection if self._config else True
    
    def get_max_tools_in_prompt(self) -> int:
        """Get maximum number of tools to include in prompt"""
        return self._config.max_tools_in_prompt if self._config else 15
    
    def should_fallback_to_static(self) -> bool:
        """Check if should fallback to static prompt"""
        return self._config.fallback_to_static if self._config else True
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self._config.debug_mode if self._config else False


# Global instance
_config_manager = MCPConfigManager()


def get_mcp_config() -> MCPToolSelectionConfig:
    """Get the global MCP configuration"""
    return _config_manager.get_config()


def is_intelligent_selection_enabled() -> bool:
    """Check if intelligent tool selection is enabled"""
    return _config_manager.is_intelligent_selection_enabled()


def get_max_tools_in_prompt() -> int:
    """Get maximum number of tools to include in prompt"""
    return _config_manager.get_max_tools_in_prompt()


def should_fallback_to_static() -> bool:
    """Check if should fallback to static prompt"""
    return _config_manager.should_fallback_to_static()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return _config_manager.is_debug_mode()


def update_mcp_config(updates: Dict[str, Any]):
    """Update MCP configuration"""
    _config_manager.update_config(updates)


# Utility function to get configuration as dict for API endpoints
def get_mcp_config_dict() -> Dict[str, Any]:
    """Get MCP configuration as dictionary"""
    config = get_mcp_config()
    return {
        'enable_intelligent_selection': config.enable_intelligent_selection,
        'max_tools_in_prompt': config.max_tools_in_prompt,
        'min_relevance_threshold': config.min_relevance_threshold,
        'enable_caching': config.enable_caching,
        'cache_ttl_hours': config.cache_ttl_hours,
        'fallback_to_static': config.fallback_to_static,
        'include_confidence_scores': config.include_confidence_scores,
        'include_use_cases': config.include_use_cases,
        'group_by_category': config.group_by_category,
        'debug_mode': config.debug_mode
    }
