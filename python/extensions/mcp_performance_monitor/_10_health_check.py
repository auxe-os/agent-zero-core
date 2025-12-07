import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle
from python.helpers.mcp_handler import MCPConfig
from agent import LoopData


@dataclass
class ServerHealthStatus:
    """Tracks health status of MCP servers"""
    server_name: str
    is_healthy: bool = True
    last_check: Optional[datetime] = None
    response_time: float = 0.0
    error_count: int = 0
    consecutive_failures: int = 0
    tool_count: int = 0


class McpHealthMonitor(Extension):
    """Monitors MCP server health and performance"""
    
    def __init__(self):
        """
        Initializes the McpHealthMonitor with default settings for check intervals
        and failure thresholds.
        """
        self.server_health: Dict[str, ServerHealthStatus] = {}
        self.check_interval = timedelta(minutes=2)
        self.last_check = datetime.now()
        self.max_consecutive_failures = 3
        self.unhealthy_servers = set()
    
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs) -> None:
        """
        Executes the MCP health monitoring check.

        This method runs periodically, triggers the health check for all configured
        MCP servers, and updates the tool selection based on server health.

        Args:
            loop_data: The current loop data (not used but part of the extension signature).
            **kwargs: Arbitrary keyword arguments.
        """
        try:
            # Check if it's time for health monitoring
            if datetime.now() - self.last_check < self.check_interval:
                return
            
            await self._perform_health_check()
            self.last_check = datetime.now()
            
            # Update tool selection based on server health
            await self._update_tool_selection()
            
        except Exception as e:
            PrintStyle().print(f"MCP health monitoring error: {e}")
    
    async def _perform_health_check(self):
        """
        Performs a health check on all configured MCP servers.

        For each server, it attempts to fetch the list of tools to verify
        connectivity and measures the response time. It tracks consecutive
        failures and marks a server as unhealthy if it exceeds a threshold.
        """
        mcp_config = MCPConfig.get_instance()
        
        for server in mcp_config.servers:
            server_name = server.name
            
            # Initialize health status if not exists
            if server_name not in self.server_health:
                self.server_health[server_name] = ServerHealthStatus(server_name=server_name)
            
            health = self.server_health[server_name]
            
            try:
                # Check server responsiveness
                start_time = datetime.now()
                
                # Get tools to test server connectivity
                tools = server.get_tools()
                health.tool_count = len(tools)
                
                # Calculate response time
                health.response_time = (datetime.now() - start_time).total_seconds()
                health.last_check = datetime.now()
                
                # Reset failure count on success
                if not health.is_healthy:
                    PrintStyle(background_color="green", font_color="white", padding=True).print(
                        f"MCP server '{server_name}' is back online"
                    )
                
                health.is_healthy = True
                health.consecutive_failures = 0
                
                # Remove from unhealthy set if recovered
                self.unhealthy_servers.discard(server_name)
                
            except Exception as e:
                health.consecutive_failures += 1
                health.error_count += 1
                health.last_check = datetime.now()
                
                # Mark as unhealthy after consecutive failures
                if health.consecutive_failures >= self.max_consecutive_failures:
                    if health.is_healthy:
                        PrintStyle(background_color="red", font_color="white", padding=True).print(
                            f"MCP server '{server_name}' marked as unhealthy after {health.consecutive_failures} failures"
                        )
                    
                    health.is_healthy = False
                    self.unhealthy_servers.add(server_name)
                
                # Health check completed for this server
                PrintStyle().print(
                    f"Health check completed for server '{server_name}'"
                )
    
    async def _update_tool_selection(self):
        """
        Updates the agent's context with the list of unhealthy MCP servers.
        This information can be used by the tool selector to avoid using tools
        from unhealthy servers.
        """
        if not self.unhealthy_servers:
            return
        
        # Store unhealthy servers list for tool selector to use
        if hasattr(self.agent, 'context'):
            self.agent.context.set_data('unhealthy_mcp_servers', list(self.unhealthy_servers))
        
        # Log summary
        PrintStyle().print(
            f"Currently unhealthy MCP servers: {', '.join(self.unhealthy_servers)}"
        )
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Gets a summary of the health status of all monitored MCP servers.

        Returns:
            A dictionary containing aggregated health statistics and detailed
            status for each server.
        """
        total_servers = len(self.server_health)
        healthy_servers = sum(1 for health in self.server_health.values() if health.is_healthy)
        
        return {
            'total_servers': total_servers,
            'healthy_servers': healthy_servers,
            'unhealthy_servers': len(self.unhealthy_servers),
            'unhealthy_server_list': list(self.unhealthy_servers),
            'last_check': self.last_check.isoformat(),
            'server_details': {
                name: {
                    'is_healthy': health.is_healthy,
                    'response_time': health.response_time,
                    'error_count': health.error_count,
                    'tool_count': health.tool_count,
                    'last_check': health.last_check.isoformat() if health.last_check else None
                }
                for name, health in self.server_health.items()
            }
        }
    
    def is_server_healthy(self, server_name: str) -> bool:
        """
        Checks if a specific MCP server is currently considered healthy.

        Args:
            server_name: The name of the server to check.

        Returns:
            True if the server is healthy or not being monitored, False otherwise.
        """
        health = self.server_health.get(server_name)
        return health.is_healthy if health else True
