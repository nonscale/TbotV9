# tbot/app/core/engine.py
import asyncio
import pandas as pd
from typing import Dict, Any
from fastapi import BackgroundTasks
import time

from tbot.app.models.strategy import Strategy
from tbot.app.core.brokers.upbit import UpbitBroker
from tbot.app.core.websocket_manager import manager # Import the manager

# In-memory storage for active scan tasks.
active_scans: Dict[int, asyncio.Task] = {}

async def _perform_scan(strategy: Strategy):
    """
    The actual scanning logic that runs in the background.
    """
    await manager.broadcast("scan_status_update", {
        "strategy_id": strategy.id,
        "status": "RUNNING",
        "message": f"Scan for '{strategy.name}' has started."
    })

    broker = UpbitBroker()

    while True:
        try:
            tickers_df = await broker.fetch_tickers()

            if tickers_df.empty:
                await asyncio.sleep(10)
                continue

            scan_rules = strategy.scan_rules
            min_price = scan_rules.get("min_price", 0)

            filtered_df = tickers_df[tickers_df['close'] > min_price]

            # Instead of printing, broadcast each found ticker
            for ticker, data in filtered_df.iterrows():
                await manager.broadcast("scan_result_found", {
                    "strategy_name": strategy.name,
                    "ticker": ticker,
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "details": {
                        "price": data.get('close', 0),
                        "volume": data.get('volume', 0),
                        "amount": data.get('amount', 0)
                    }
                })

            await asyncio.sleep(60)

        except asyncio.CancelledError:
            await manager.broadcast("scan_status_update", {
                "strategy_id": strategy.id,
                "status": "STOPPED",
                "message": f"Scan for '{strategy.name}' was stopped."
            })
            break
        except Exception as e:
            await manager.broadcast("notification", {
                "level": "error",
                "message": f"Error in '{strategy.name}' scan: {e}"
            })
            await asyncio.sleep(30)


def start_scan(strategy: Strategy, background_tasks: BackgroundTasks):
    if strategy.id in active_scans and not active_scans[strategy.id].done():
        return

    task = asyncio.create_task(_perform_scan(strategy))
    active_scans[strategy.id] = task

def stop_scan(strategy_id: int):
    task = active_scans.get(strategy_id)
    if not task or task.done():
        return

    task.cancel()
    if strategy_id in active_scans:
        del active_scans[strategy_id]
