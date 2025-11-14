# tbot/app/core/engine.py
import asyncio
from typing import Dict, Any
from fastapi import BackgroundTasks

from tbot.app.models.strategy import Strategy
from tbot.app.core.brokers.upbit import UpbitBroker # For now, we hardcode Upbit

# In-memory storage for active scan tasks.
# Key: strategy_id, Value: asyncio.Task
active_scans: Dict[int, asyncio.Task] = {}

async def _perform_scan(strategy: Strategy):
    """
    The actual scanning logic that runs in the background.
    """
    print(f"Starting scan for strategy: {strategy.name}")

    # 1. Initialize the appropriate broker
    # In the future, this will be dynamic based on strategy.broker
    broker = UpbitBroker()

    # Loop indefinitely until the task is cancelled
    while True:
        try:
            print(f"[{strategy.name}] Fetching tickers...")
            # 2. Fetch market data (1st phase scan)
            tickers_df = await broker.fetch_tickers()

            if tickers_df.empty:
                print(f"[{strategy.name}] No data fetched. Retrying in 10 seconds...")
                await asyncio.sleep(10)
                continue

            # 3. Apply 1st phase scan rules (currently simplified)
            # This is where the logic parser for scan_rules will be integrated.
            # For now, we'll just print the number of tickers found.
            print(f"[{strategy.name}] Found {len(tickers_df)} tickers.")

            # For demonstration, let's filter for tickers with close price > 1000
            scan_rules = strategy.scan_rules
            min_price = scan_rules.get("min_price", 0)

            filtered_df = tickers_df[tickers_df['close'] > min_price]
            print(f"[{strategy.name}] Found {len(filtered_df)} tickers with price > {min_price}")


            # Wait for a defined interval before the next scan
            # In the future, this will use strategy.cron_schedule
            await asyncio.sleep(60) # Scan every 60 seconds

        except asyncio.CancelledError:
            print(f"Scan for strategy '{strategy.name}' was cancelled.")
            break
        except Exception as e:
            print(f"An error occurred during scan for strategy '{strategy.name}': {e}")
            # Wait before retrying to avoid spamming in case of persistent errors
            await asyncio.sleep(30)


def start_scan(strategy: Strategy, background_tasks: BackgroundTasks):
    """
    Starts a new scan for the given strategy in the background.
    """
    if strategy.id in active_scans and not active_scans[strategy.id].done():
        print(f"Scan for strategy {strategy.id} is already running.")
        return

    task = asyncio.create_task(_perform_scan(strategy))
    active_scans[strategy.id] = task

    # We can use background_tasks to ensure the task runs even if the request connection closes
    # but for long-running scans, managing the task lifecycle with our dict is more robust.
    print(f"Scan for strategy {strategy.id} scheduled.")


def stop_scan(strategy_id: int):
    """
    Stops a running scan for the given strategy.
    """
    task = active_scans.get(strategy_id)
    if not task or task.done():
        print(f"No active scan found for strategy {strategy_id}.")
        return

    task.cancel()
    del active_scans[strategy_id]
    print(f"Scan for strategy {strategy_id} stopped.")
