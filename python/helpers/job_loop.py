import asyncio
from datetime import datetime
import time
from python.helpers.task_scheduler import TaskScheduler
from python.helpers.print_style import PrintStyle
from python.helpers import errors
from python.helpers import runtime


SLEEP_TIME = 60

keep_running = True
pause_time = 0


async def run_loop():
    global pause_time, keep_running

    while True:
        if runtime.is_development():
            # Signal to container that the job loop should be paused
            # if we are runing a development instance to avoid duble-running the jobs
            try:
                await runtime.call_development_function(pause_loop)
            except Exception as e:
                msg = errors.error_text(e)
                # Connection errors are expected when no separate development instance is running;
                # log them at lower severity to avoid noisy error output during normal local runs.
                if "Cannot connect to host" in msg or "Connect call failed" in msg:
                    PrintStyle().debug(
                        "No development instance available to pause job loop; continuing locally: "
                        + msg
                    )
                elif "Invalid RFC hash" in msg:
                    # Auth mismatch with development instance; continue running jobs locally.
                    PrintStyle().debug(
                        "Development instance RFC auth failed when pausing job loop; continuing locally: "
                        + msg
                    )
                else:
                    PrintStyle().error(
                        "Failed to pause job loop by development instance: " + msg
                    )
        if not keep_running and (time.time() - pause_time) > (SLEEP_TIME * 2):
            resume_loop()
        if keep_running:
            try:
                await scheduler_tick()
            except Exception as e:
                PrintStyle().error(errors.format_error(e))
        await asyncio.sleep(SLEEP_TIME)  # TODO! - if we lower it under 1min, it can run a 5min job multiple times in it's target minute


async def scheduler_tick():
    # Get the task scheduler instance and print detailed debug info
    scheduler = TaskScheduler.get()
    # Run the scheduler tick
    await scheduler.tick()


def pause_loop():
    global keep_running, pause_time
    keep_running = False
    pause_time = time.time()


def resume_loop():
    global keep_running, pause_time
    keep_running = True
    pause_time = 0
