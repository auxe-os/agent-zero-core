import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict

from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle
from agent import LoopData


class TrackToolUsage(Extension):
    """Tracks tool usage patterns to improve selection accuracy over time"""
    
    def __init__(self):
        self.usage_data = defaultdict(lambda: {
            'count': 0,
            'success_count': 0,
            'last_used': None,
            'average_response_time': 0.0,
            'contexts_used': []
        })
        self.session_start = datetime.now()
        self.current_session_tools = []
    
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """Track tool usage and update analytics"""
        try:
            # Get current tool usage from agent history
            # Note: Using simplified approach since get_last_entries may not exist
            tools_in_loop = []
            if hasattr(self.agent, 'history') and self.agent.history:
                # Get recent entries safely
                try:
                    recent_entries = getattr(self.agent.history, 'entries', [])
                    if recent_entries:
                        # Take last 10 entries
                        for entry in recent_entries[-10:]:
                            if isinstance(entry, dict) and entry.get('type') == 'tool_call':
                                tool_name = entry.get('tool_name', '')
                                if tool_name and tool_name not in tools_in_loop:
                                    tools_in_loop.append(tool_name)
                except Exception:
                    pass
            
            # Periodically analyze and update tool selection weights
            if self._should_update_weights():
                await self._update_selection_weights()
                
        except Exception as e:
            PrintStyle().print(f"Tool usage tracking error: {e}")
    
    def _record_tool_usage(self, tool_name: str, entry: Dict[str, Any]):
        """Record individual tool usage"""
        if not tool_name:
            return
            
        usage = self.usage_data[tool_name]
        usage['count'] += 1
        usage['last_used'] = datetime.now()
        
        # Track success based on response
        if entry.get('success', True):
            usage['success_count'] += 1
        
        # Track response time if available
        if 'response_time' in entry:
            current_avg = usage['average_response_time']
            new_time = entry['response_time']
            usage['average_response_time'] = (current_avg + new_time) / 2
        
        # Track context (task type)
        if 'context' in entry:
            usage['contexts_used'].append(entry['context'])
    
    def _should_update_weights(self) -> bool:
        """Check if it's time to update selection weights"""
        # Update every 10 tool uses or every 5 minutes
        total_uses = sum(usage['count'] for usage in self.usage_data.values())
        time_elapsed = datetime.now() - self.session_start
        
        return total_uses % 10 == 0 or time_elapsed > timedelta(minutes=5)
    
    async def _update_selection_weights(self):
        """Update tool selection weights based on usage patterns"""
        try:
            # Calculate success rates and preferences
            tool_preferences = {}
            
            for tool_name, usage in self.usage_data.items():
                if usage['count'] > 0:
                    success_rate = usage['success_count'] / usage['count']
                    recency_bonus = self._calculate_recency_bonus(usage['last_used'])
                    
                    # Combined preference score
                    preference = (success_rate * 0.6) + (recency_bonus * 0.4)
                    tool_preferences[tool_name] = preference
            
            # Store preferences for tool selector to use
            if hasattr(self.agent, 'context'):
                self.agent.context.set_data('tool_usage_preferences', tool_preferences)
                
            PrintStyle().print(
                f"Updated tool preferences for {len(tool_preferences)} tools"
            )
                
        except Exception as e:
            PrintStyle().print(f"Error updating tool weights: {e}")
    
    def _calculate_recency_bonus(self, last_used: datetime) -> float:
        """Calculate recency bonus for recently used tools"""
        if not last_used:
            return 0.0
            
        time_diff = datetime.now() - last_used
        hours_ago = time_diff.total_seconds() / 3600
        
        # Higher bonus for more recent usage (decay over 24 hours)
        if hours_ago < 1:
            return 1.0
        elif hours_ago < 6:
            return 0.8
        elif hours_ago < 24:
            return 0.5
        else:
            return 0.2
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        total_uses = sum(usage['count'] for usage in self.usage_data.values())
        
        return {
            'total_tool_uses': total_uses,
            'unique_tools_used': len(self.usage_data),
            'session_duration': str(datetime.now() - self.session_start),
            'top_tools': sorted(
                self.usage_data.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:5]
        }
