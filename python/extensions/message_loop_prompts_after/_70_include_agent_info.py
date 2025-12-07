from python.helpers.extension import Extension
from agent import LoopData

class IncludeAgentInfo(Extension):
    """
    An extension that includes information about the agent, such as its number
    and profile, in the prompt context.
    """
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the extension to add agent information.

        This method reads a prompt template for agent info, formats it with the
        current agent's number and profile, and adds it to the temporary extras
        of the loop data.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        
        # read prompt
        agent_info_prompt = self.agent.read_prompt(
            "agent.extras.agent_info.md",
            number=self.agent.number,
            profile=self.agent.config.profile or "Default",
        )

        # add agent info to the prompt
        loop_data.extras_temporary["agent_info"] = agent_info_prompt
