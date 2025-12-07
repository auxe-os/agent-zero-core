from python.helpers import files, memory
from python.helpers.tool import Tool, Response
from agent import Agent
from python.helpers.log import LogItem


class UpdateBehaviour(Tool):
    """A tool for updating the agent's behaviour."""

    async def execute(self, adjustments="", **kwargs):
        """Executes the tool.

        Args:
            adjustments: The adjustments to make to the agent's behaviour.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object.
        """

        # stringify adjustments if needed
        if not isinstance(adjustments, str):
            adjustments = str(adjustments)

        await update_behaviour(self.agent, self.log, adjustments)
        return Response(
            message=self.agent.read_prompt("behaviour.updated.md"), break_loop=False
        )

    # async def before_execution(self, **kwargs):
    #     pass

    # async def after_execution(self, response, **kwargs):
    #     pass


async def update_behaviour(agent: Agent, log_item: LogItem, adjustments: str):
    """Updates the agent's behaviour.

    Args:
        agent: The agent to update.
        log_item: The log item to stream progress to.
        adjustments: The adjustments to make to the agent's behaviour.
    """

    # get system message and current ruleset
    system = agent.read_prompt("behaviour.merge.sys.md")
    current_rules = read_rules(agent)

    # log query streamed by LLM
    async def log_callback(content):
        log_item.stream(ruleset=content)

    msg = agent.read_prompt(
        "behaviour.merge.msg.md", current_rules=current_rules, adjustments=adjustments
    )

    # call util llm to find solutions in history
    adjustments_merge = await agent.call_utility_model(
        system=system,
        message=msg,
        callback=log_callback,
    )

    # update rules file
    rules_file = get_custom_rules_file(agent)
    files.write_file(rules_file, adjustments_merge)
    log_item.update(result="Behaviour updated")


def get_custom_rules_file(agent: Agent):
    """Gets the path to the custom rules file for the given agent.

    Args:
        agent: The agent.

    Returns:
        The path to the custom rules file.
    """
    return files.get_abs_path(memory.get_memory_subdir_abs(agent), "behaviour.md")


def read_rules(agent: Agent):
    """Reads the rules for the given agent.

    Args:
        agent: The agent.

    Returns:
        The rules for the agent.
    """
    rules_file = get_custom_rules_file(agent)
    if files.exists(rules_file):
        rules = files.read_prompt_file(rules_file)
        return agent.read_prompt("agent.system.behaviour.md", rules=rules)
    else:
        rules = agent.read_prompt("agent.system.behaviour_default.md")
        return agent.read_prompt("agent.system.behaviour.md", rules=rules)
