import asyncio
from datetime import datetime
from typing import Dict, Any, List

from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle
from python.helpers.mcp_handler import MCPConfig
from agent import LoopData


class McpHealthCheck(Extension):
    """Performs MCP health check at the end of each message loop"""
    
    def __init__(self, agent, **kwargs):
        super().__init__(agent=agent, **kwargs)
        self.last_check = None
        self.check_interval = 5  # Check every 5 loops
        self.loop_count = 0
    
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs) -> None:
        """Perform MCP health check"""
        try:
            self.loop_count += 1
            
            # Only check periodically to avoid overhead
            if self.loop_count % self.check_interval != 0:
                return
            
            await self._perform_health_check()
            self.last_check = datetime.now()
            
        except Exception as e:
            PrintStyle().print(f"MCP health check error: {e}")
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            mcp_config = MCPConfig.get_instance()
            
            if not mcp_config.servers:
                return
            
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'servers': {},
                'total_servers': len(mcp_config.servers),
                'healthy_servers': 0,
                'unhealthy_servers': 0
            }
            
            for server in mcp_config.servers:
                server_health = await self._check_server_health(server)
                health_status['servers'][server.name] = server_health
                
                if server_health['is_healthy']:
                    health_status['healthy_servers'] += 1
                else:
                    health_status['unhealthy_servers'] += 1
            
            # Store health status for monitoring
            if hasattr(self.agent, 'context'):
                self.agent.context.set_data('mcp_health_status', health_status)
            
            # Log health summary
            self._log_health_summary(health_status)
            
            # Take action if needed
            await self._handle_health_issues(health_status)
            
        except Exception as e:
            PrintStyle().print(f"Error performing health check: {e}")
    
    async def _check_server_health(self, server) -> Dict[str, Any]:
        """Check health of individual server"""
        server_health = {
            'server_name': server.name,
            'is_healthy': True,
            'response_time': 0.0,
            'tool_count': 0,
            'error_message': None
        }
        
        try:
            start_time = datetime.now()
            
            # Test server connectivity by getting tools
            tools = server.get_tools()
            server_health['tool_count'] = len(tools)
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            server_health['response_time'] = response_time
            
            # Check if response time is acceptable
            if response_time > 5.0:  # 5 second threshold
                server_health['is_healthy'] = False
                server_health['error_message'] = f"Slow response: {response_time:.2f}s"
            
        except Exception as e:
            server_health['is_healthy'] = False
            server_health['error_message'] = str(e)
        
        return server_health
    
    def _log_health_summary(self, health_status: Dict[str, Any]):
        """Log health check summary"""
        try:
            healthy = health_status['healthy_servers']
            total = health_status['total_servers']
            
            if healthy == total:
                status_msg = "All MCP servers healthy"
                status_color = "green"
            elif healthy > 0:
                status_msg = f"{healthy}/{total} MCP servers healthy"
                status_color = "yellow"
            else:
                status_msg = "No MCP servers healthy"
                status_color = "red"
            
            PrintStyle(background_color=status_color, font_color="white", padding=True).print(
                f"MCP Health Check: {status_msg}"
            )
            
            # Log detailed status
            PrintStyle().print(
                f"MCP health status: {healthy}/{total} servers healthy"
            )
                
        except Exception:
            pass
    
    async def _handle_health_issues(self, health_status: Dict[str, Any]):
        """Handle any health issues discovered"""
        try:
            unhealthy_servers = [
                name for name, health in health_status['servers'].items()
                if not health['is_healthy']
            ]
            
            if unhealthy_servers:
                # Store unhealthy servers for tool selector to avoid
                if hasattr(self.agent, 'context'):
                    self.agent.context.set_data('unhealthy_mcp_servers', unhealthy_servers)
                
                # Log warning
                PrintStyle().print(
                    f"Unhealthy MCP servers detected: {', '.join(unhealthy_servers)}"
                )
                
                PrintStyle(background_color="orange", font_color="black", padding=True).print(
                    f"Warning: Unhealthy MCP servers: {', '.join(unhealthy_servers)}"
                )
            
        except Exception as e:
            PrintStyle().print(f"Error handling health issues: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        if hasattr(self.agent, 'context'):
            return self.agent.context.get_data('mcp_health_status') or {}
        return {}
