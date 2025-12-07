from datetime import datetime
from python.helpers.extension import Extension
from agent import Agent, LoopData
from python.helpers import files, memory


class BehaviourPrompt(Extension):
    """
    An extension that injects behavioral rules into the system prompt. It can
    load custom rules from a 'behaviour.md' file or use a default set.
    """

    async def execute(self, system_prompt: list[str]=[], loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the behavior prompt extension.

        This method reads the applicable behavioral rules and inserts them at the
        beginning of the system prompt list.

        Args:
            system_prompt: The list of system prompt components.
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        prompt = read_rules(self.agent)
        system_prompt.insert(0, prompt) #.append(prompt)

def get_custom_rules_file(agent: Agent):
    """
    Gets the absolute path to the custom 'behaviour.md' file for the agent.

    Args:
        agent: The agent instance.

    Returns:
        The absolute path to the behavior file.
    """
    return files.get_abs_path(memory.get_memory_subdir_abs(agent), "behaviour.md")

def read_rules(agent: Agent):
    """
    Reads the behavioral rules for the agent.

    It first checks for a custom 'behaviour.md' file in the agent's memory
    directory. If it exists, those rules are used. Otherwise, it falls back
    to the default behavioral rules.

    Args:
        agent: The agent instance.

    Returns:
        A formatted string containing the behavioral rules.
    """
    rules_file = get_custom_rules_file(agent)
    if files.exists(rules_file):
        rules = files.read_file(rules_file) # no includes and vars here, that could crash
        return agent.read_prompt("agent.system.behaviour.md", rules=rules)
    else:
        rules = agent.read_prompt("agent.system.behaviour_default.md")
        return agent.read_prompt("agent.system.behaviour.md", rules=rules)
  