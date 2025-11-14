# tbot/app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from tbot.app.models.strategy import Strategy
from tbot.app.core import engine

scheduler = AsyncIOScheduler()

def schedule_strategy(strategy: Strategy):
    """
    Schedules a strategy to run based on its cron schedule.
    Removes any existing job for this strategy before creating a new one.
    """
    job_id = f"strategy_{strategy.id}"

    # Remove existing job if it exists, to prevent duplicates
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    if strategy.is_active and strategy.cron_schedule:
        try:
            scheduler.add_job(
                engine.start_scan,
                trigger=CronTrigger.from_crontab(strategy.cron_schedule),
                args=[strategy],
                id=job_id,
                name=f"Scan for {strategy.name}",
                replace_existing=True,
            )
            print(f"Strategy '{strategy.name}' scheduled with cron: {strategy.cron_schedule}")
        except Exception as e:
            print(f"Error scheduling strategy '{strategy.name}': {e}")


def unschedule_strategy(strategy_id: int):
    """
    Removes a scheduled job for a given strategy.
    """
    job_id = f"strategy_{strategy_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        print(f"Unscheduled job for strategy ID {strategy_id}.")
