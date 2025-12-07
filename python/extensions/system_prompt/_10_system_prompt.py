from typing import Any
from python.helpers.extension import Extension
from python.helpers.mcp_handler import MCPConfig
from agent import Agent, LoopData
from python.helpers.settings import get_settings
from python.helpers import projects


class SystemPrompt(Extension):
    """
    An extension responsible for assembling the main system prompt by combining
    various components like the main instructions, tool definitions, and contextual
    information.
    """

    async def execute(
        self,
        system_prompt: list[str] = [],
        loop_data: LoopData = LoopData(),
        **kwargs: Any
    ):
        """
        Executes the system prompt assembly extension.

        This method gathers various parts of the system prompt (main, tools,
        MCP tools, secrets, project info) and appends them to the system_prompt list.

        Args:
            system_prompt: A list to which the prompt components will be added.
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        # append main system prompt and tools
        main = get_main_prompt(self.agent)
        tools = get_tools_prompt(self.agent)
        mcp_tools = get_mcp_tools_prompt(self.agent)
        secrets_prompt = get_secrets_prompt(self.agent)
        project_prompt = get_project_prompt(self.agent)

        system_prompt.append(main)
        system_prompt.append(tools)
        if mcp_tools:
            system_prompt.append(mcp_tools)
        if secrets_prompt:
            system_prompt.append(secrets_prompt)
        if project_prompt:
            system_prompt.append(project_prompt)


def get_main_prompt(agent: Agent):
    """
    Gets the main system prompt for the agent.

    Args:
        agent: The agent instance.

    Returns:
        The main system prompt string.
    """
    return agent.read_prompt("agent.system.main.md")


def get_tools_prompt(agent: Agent):
    """
    Gets the tools definition prompt for the agent, including vision-specific
    tools if the model supports them.

    Args:
        agent: The agent instance.

    Returns:
        The tools prompt string.
    """
    prompt = agent.read_prompt("agent.system.tools.md")
    if agent.config.chat_model.vision:
        prompt += "\n\n" + agent.read_prompt("agent.system.tools_vision.md")
    return prompt


def get_mcp_tools_prompt(agent: Agent):
    """
    Gets the tools prompt for Multi-Context Parallel (MCP) tools.

    This can either be a static list of all tools or an intelligently selected
    subset based on the current conversation context.

    Args:
        agent: The agent instance.

    Returns:
        The MCP tools prompt string, or an empty string if no MCP servers are configured.
    """
    mcp_config = MCPConfig.get_instance()
    if mcp_config.servers:
        pre_progress = agent.context.log.progress
        agent.context.log.set_progress(
            "Collecting MCP tools"
        )  # MCP might be initializing, better inform via progress bar
        
        # Check if intelligent selection is enabled
        try:
            from python.helpers.mcp_config import is_intelligent_selection_enabled, get_max_tools_in_prompt, should_fallback_to_static, is_debug_mode
            
            if is_intelligent_selection_enabled():
                # Get the last user message for context
                user_message = ""
                if hasattr(agent, 'last_user_message') and agent.last_user_message:
                    if hasattr(agent.last_user_message, 'content'):
                        content = agent.last_user_message.content
                        if isinstance(content, str):
                            user_message = content
                        elif isinstance(content, dict) and 'message' in content:
                            user_message = str(content['message'])
                
                # Import the intelligent tool selector
                from python.helpers.mcp_tool_selector import get_intelligent_mcp_prompt
                
                # Generate intelligent prompt
                max_tools = get_max_tools_in_prompt()
                tools = get_intelligent_mcp_prompt(user_message, max_tools=max_tools)
                
                # Debug logging
                if is_debug_mode():
                    from python.helpers.print_style import PrintStyle
                    PrintStyle(background_color="blue", font_color="white", padding=True).print(
                        f"Intelligent MCP tool selection: {len(tools.split('###'))-2 if '###' in tools else 0} tools selected for context: {user_message[:100]}..."
                    )
                
                # If intelligent selection failed and fallback is enabled
                if not tools or "No relevant MCP tools" in tools:
                    if should_fallback_to_static():
                        tools = MCPConfig.get_instance().get_tools_prompt()
                        if is_debug_mode():
                            from python.helpers.print_style import PrintStyle
                            PrintStyle(background_color="yellow", font_color="black", padding=True).print(
                                "Falling back to static MCP tools prompt"
                            )
                    else:
                        tools = "## MCP tool selection disabled - no relevant tools found\n"
            else:
                # Intelligent selection disabled, use static prompt
                tools = MCPConfig.get_instance().get_tools_prompt()
                if is_debug_mode():
                    from python.helpers.print_style import PrintStyle
                    PrintStyle(background_color="grey", font_color="white", padding=True).print(
                        "Using static MCP tools prompt (intelligent selection disabled)"
                    )
                
        except Exception as e:
            # Fallback to static prompt on any error
            from python.helpers.print_style import PrintStyle
            PrintStyle().print(f"Error with intelligent MCP tool selection: {e}")
            tools = MCPConfig.get_instance().get_tools_prompt()
            
        agent.context.log.set_progress(pre_progress)  # return original progress
        return tools
    return ""


def get_secrets_prompt(agent: Agent):
    """
    Gets the prompt component that includes available secrets and variables.

    Args:
        agent: The agent instance.

    Returns:
        The secrets and variables prompt string, or an empty string on error.
    """
    try:
        # Use lazy import to avoid circular dependencies
        from python.helpers.secrets import get_secrets_manager

        secrets_manager = get_secrets_manager(agent.context)
        secrets = secrets_manager.get_secrets_for_prompt()
        vars = get_settings()["variables"]
        return agent.read_prompt("agent.system.secrets.md", secrets=secrets, vars=vars)
    except Exception as e:
        # If secrets module is not available or has issues, return empty string
        return ""


def get_project_prompt(agent: Agent):
    """
    Gets the prompt component related to the active project.

    This will either provide details about the active project or a message
    indicating that no project is active.

    Args:
        agent: The agent instance.

    Returns:
        The project-related prompt string.
    """
    result = agent.read_prompt("agent.system.projects.main.md")
    project_name = agent.context.get_data(projects.CONTEXT_DATA_KEY_PROJECT)
    if project_name:
        project_vars = projects.build_system_prompt_vars(project_name)
        result += "\n\n" + agent.read_prompt(
            "agent.system.projects.active.md", **project_vars
        )
    else:
        result += "\n\n" + agent.read_prompt("agent.system.projects.inactive.md")
    return result
