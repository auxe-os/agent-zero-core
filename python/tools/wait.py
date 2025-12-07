import asyncio
from datetime import datetime, timedelta, timezone
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.wait import managed_wait
from python.helpers.localization import Localization

class WaitTool(Tool):
    """
    A tool that pauses the agent's execution for a specified duration or until
    a specific timestamp.
    """

    async def execute(self, **kwargs) -> Response:
        """
        Executes the wait tool.

        The agent can wait for a duration specified in days, hours, minutes, and
        seconds, or until a specific ISO 8601 timestamp.

        Args:
            **kwargs: Arbitrary keyword arguments. Can include 'seconds',
                      'minutes', 'hours', 'days', or 'until'.

        Returns:
            A Response object with a message indicating that the wait is complete.
        """
        await self.agent.handle_intervention()

        seconds = self.args.get("seconds", 0)
        minutes = self.args.get("minutes", 0)
        hours = self.args.get("hours", 0)
        days = self.args.get("days", 0)
        until_timestamp_str = self.args.get("until")

        is_duration_wait = not bool(until_timestamp_str)

        now = datetime.now(timezone.utc)
        target_time = None

        if until_timestamp_str:
            try:
                target_time = Localization.get().localtime_str_to_utc_dt(until_timestamp_str)
                if not target_time:
                    raise ValueError(f"Invalid timestamp format: {until_timestamp_str}")
            except ValueError as e:
                return Response(
                    message=str(e),
                    break_loop=False,
                )
        else:
            wait_duration = timedelta(
                days=int(days),
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds),
            )
            if wait_duration.total_seconds() <= 0:
                return Response(
                    message="Wait duration must be positive.",
                    break_loop=False,
                )
            target_time = now + wait_duration
        
        if target_time <= now:
            return Response(
                message=f"Target time {target_time.isoformat()} is in the past.",
                break_loop=False,
            )

        PrintStyle.info(f"Waiting until {target_time.isoformat()}...")

        target_time = await managed_wait(
            agent=self.agent,
            target_time=target_time,
            is_duration_wait=is_duration_wait,
            log=self.log,
            get_heading_callback=self.get_heading
        )

        if self.log:
            self.log.update(heading=self.get_heading("Done", done=True))

        message = self.agent.read_prompt(
            "fw.wait_complete.md",
            target_time=target_time.isoformat()
        )

        return Response(
            message=message,
            break_loop=False,
        )

    def get_log_object(self):
        """
        Creates a log object for the wait tool.

        Returns:
            A log object of type 'progress' for tracking the wait.
        """
        return self.agent.context.log.log(
            type="progress",
            heading=self.get_heading(),
            content="",
            kvps=self.args,
        )

    def get_heading(self, text: str = "", done: bool = False):
        """
        Generates a heading for the log output.

        Args:
            text: Optional text to include in the heading.
            done: If True, adds a 'done' icon to the heading.

        Returns:
            A formatted string for the log heading.
        """
        done_icon = " icon://done_all" if done else ""
        if not text:
            text = f"Waiting..."
        return f"icon://timer Wait: {text}{done_icon}"
