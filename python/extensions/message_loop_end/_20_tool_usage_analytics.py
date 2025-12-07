import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle
from agent import LoopData


class ToolUsageAnalytics(Extension):
    """Analyzes tool usage at the end of each message loop"""
    
    def __init__(self, agent, **kwargs):
        """
        Initializes the ToolUsageAnalytics extension.

        Args:
            agent: The agent instance.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(agent=agent, **kwargs)
        self.session_start = datetime.now()
        self.loop_count = 0
    
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the tool usage analysis at the end of a message loop.

        This method gathers data on the tools used in the loop, analyzes their
        effectiveness, updates selection preferences, and logs the analytics.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        try:
            self.loop_count += 1
            
            # Get tools used in this loop
            tools_used = self._get_tools_used_in_loop()
            
            if tools_used:
                # Analyze tool effectiveness
                await self._analyze_tool_effectiveness(tools_used)
                
                # Update tool selection preferences
                await self._update_selection_preferences(tools_used)
                
                # Log analytics data
                self._log_analytics(tools_used)
            
            # Periodic summary every 10 loops
            if self.loop_count % 10 == 0:
                await self._generate_summary()
                
        except Exception as e:
            PrintStyle().print(f"Tool usage analytics error: {e}")
    
    def _get_tools_used_in_loop(self) -> List[str]:
        """
        Gets a list of unique tool names used in the current message loop by
        inspecting the agent's recent history.

        Returns:
            A list of tool names.
        """
        tools_used = []
        
        try:
            # Check agent history for tool calls in this loop
            # Note: Using simplified approach since get_last_entries may not exist
            if hasattr(self.agent, 'history') and self.agent.history:
                try:
                    recent_entries = getattr(self.agent.history, 'entries', [])
                    if recent_entries:
                        # Take last 5 entries
                        for entry in recent_entries[-5:]:
                            if isinstance(entry, dict) and entry.get('type') == 'tool_call':
                                tool_name = entry.get('tool_name', '')
                                if tool_name and tool_name not in tools_used:
                                    tools_used.append(tool_name)
                except Exception:
                    pass
                            
        except Exception as e:
            PrintStyle().print(f"Error getting tools used: {e}")
        
        return tools_used
    
    async def _analyze_tool_effectiveness(self, tools_used: List[str]):
        """
        Analyzes the effectiveness of the tools used in the loop.

        It calculates an effectiveness score for each tool and stores it in the
        agent's context for future reference.

        Args:
            tools_used: A list of tool names used in the loop.
        """
        try:
            for tool_name in tools_used:
                # Get tool execution data
                tool_data = self._get_tool_execution_data(tool_name)
                
                if tool_data:
                    # Calculate effectiveness metrics
                    effectiveness = self._calculate_effectiveness(tool_data)
                    
                    # Store for future reference
                    if hasattr(self.agent, 'context'):
                        analytics_key = f'tool_analytics_{tool_name}'
                        existing_data = self.agent.context.get_data(analytics_key) or {}
                        
                        existing_data.update({
                            'last_used': datetime.now().isoformat(),
                            'effectiveness_score': effectiveness,
                            'usage_count': existing_data.get('usage_count', 0) + 1
                        })
                        
                        self.agent.context.set_data(analytics_key, existing_data)
                        
        except Exception as e:
            PrintStyle().print(f"Error analyzing tool effectiveness: {e}")
    
    def _get_tool_execution_data(self, tool_name: str) -> Dict[str, Any]:
        """
        Retrieves execution data for a specific tool from the agent's recent history.

        Args:
            tool_name: The name of the tool to get data for.

        Returns:
            A dictionary containing the tool call data, or an empty dictionary
            if not found.
        """
        try:
            # Look for tool execution in recent history
            # Note: Using simplified approach since get_last_entries may not exist
            if hasattr(self.agent, 'history') and self.agent.history:
                try:
                    recent_entries = getattr(self.agent.history, 'entries', [])
                    if recent_entries:
                        # Take last 10 entries
                        for entry in recent_entries[-10:]:
                            if isinstance(entry, dict) and entry.get('type') == 'tool_call' and entry.get('tool_name') == tool_name:
                                return entry
                except Exception:
                    pass
                        
        except Exception:
            pass
        
        return {}
    
    def _calculate_effectiveness(self, tool_data: Dict[str, Any]) -> float:
        """
        Calculates an effectiveness score for a tool based on its execution data.

        The score considers success status, response time, and output quality.

        Args:
            tool_data: A dictionary containing the tool's execution data.

        Returns:
            An effectiveness score between 0.0 and 1.0.
        """
        score = 0.5  # Base score
        
        # Factor in success rate
        if tool_data.get('success', True):
            score += 0.3
        
        # Factor in response time (faster is better)
        response_time = tool_data.get('response_time', 1.0)
        if response_time < 1.0:
            score += 0.2
        elif response_time < 2.0:
            score += 0.1
        
        # Factor in output quality (if available)
        if tool_data.get('output_quality', 'medium') == 'high':
            score += 0.2
        elif tool_data.get('output_quality', 'medium') == 'medium':
            score += 0.1
        
        return min(score, 1.0)
    
    async def _update_selection_preferences(self, tools_used: List[str]):
        """
        Updates the tool selection preferences based on the latest analytics.

        This method calculates a preference score for each used tool and updates
        the global preferences in the agent's context.

        Args:
            tools_used: A list of tool names used in the loop.
        """
        try:
            preferences = {}
            
            for tool_name in tools_used:
                analytics_key = f'tool_analytics_{tool_name}'
                tool_data = self.agent.context.get_data(analytics_key) if hasattr(self.agent, 'context') else None
                
                if tool_data:
                    # Calculate preference based on effectiveness and recent usage
                    effectiveness = tool_data.get('effectiveness_score', 0.5)
                    usage_count = tool_data.get('usage_count', 1)
                    
                    # Preference combines effectiveness and usage frequency
                    preference = (effectiveness * 0.7) + (min(usage_count / 10, 1.0) * 0.3)
                    preferences[tool_name] = preference
            
            # Update global preferences
            if preferences and hasattr(self.agent, 'context'):
                existing_prefs = self.agent.context.get_data('tool_selection_preferences') or {}
                existing_prefs.update(preferences)
                self.agent.context.set_data('tool_selection_preferences', existing_prefs)
                
        except Exception as e:
            PrintStyle().print(f"Error updating selection preferences: {e}")
    
    def _log_analytics(self, tools_used: List[str]):
        """
        Logs a simple message indicating which tools were used in the current loop.

        Args:
            tools_used: A list of tool names used in the loop.
        """
        try:
            PrintStyle().print(
                f"Tools used in loop {self.loop_count}: {', '.join(tools_used)}"
            )
                
        except Exception:
            pass
    
    async def _generate_summary(self):
        """
        Generates and logs a periodic summary of tool usage analytics for the
        current session.
        """
        try:
            if not hasattr(self.agent, 'context'):
                return
            
            # Collect all tool analytics
            all_analytics = {}
            for key in self.agent.context.data.keys():
                if key.startswith('tool_analytics_'):
                    tool_name = key.replace('tool_analytics_', '')
                    all_analytics[tool_name] = self.agent.context.get_data(key)
            
            # Generate summary
            summary = {
                'session_duration': str(datetime.now() - self.session_start),
                'total_loops': self.loop_count,
                'tools_analyzed': len(all_analytics),
                'top_tools': sorted(
                    all_analytics.items(),
                    key=lambda x: x[1].get('effectiveness_score', 0),
                    reverse=True
                )[:5]
            }
            
            # Log summary
            PrintStyle().print(
                f"Tool analytics summary: {json.dumps(summary, indent=2)}"
            )
                
            PrintStyle(background_color="blue", font_color="white", padding=True).print(
                f"Tool Analytics Summary: {len(all_analytics)} tools analyzed over {self.loop_count} loops"
            )
                
        except Exception as e:
            PrintStyle().print(f"Error generating summary: {e}")
