from datetime import datetime, timezone
from python.helpers.extension import Extension
from agent import LoopData
from python.helpers.localization import Localization


class IncludeCurrentDatetime(Extension):
    """
    An extension that includes the current date and time in the agent's context
    for each message loop.
    """
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the extension to add the current datetime.

        This method gets the current localized time, formats it into a prompt,
        and adds it to the temporary extras of the loop data.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        # get current datetime
        current_datetime = Localization.get().utc_dt_to_localtime_str(
            datetime.now(timezone.utc), sep=" ", timespec="seconds"
        )
        # remove timezone offset
        if current_datetime and "+" in current_datetime:
            current_datetime = current_datetime.split("+")[0]

        # read prompt
        datetime_prompt = self.agent.read_prompt(
            "agent.system.datetime.md", date_time=current_datetime
        )

        # add current datetime to the loop data
        loop_data.extras_temporary["current_datetime"] = datetime_prompt
