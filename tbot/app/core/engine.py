# tbot/app/core/engine.py
import asyncio
import pandas as pd
from typing import Dict, Any

from tbot.app.models.strategy import Strategy, GroupNode
from tbot.app.core.brokers.upbit import UpbitBroker
from tbot.app.core.websocket_manager import manager
from tbot.app.core.logic_parser import logic_parser, LogicParserError

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
    first_scan_root_node = strategy.scan_rules.first_scan

    while True:
        try:
            tickers_df = await broker.fetch_tickers()

            if tickers_df.empty:
                await asyncio.sleep(10)
                continue

            # Apply the dynamic 1st phase scan rule from the tree structure
            try:
                filtered_df = logic_parser.apply_tree(tickers_df, first_scan_root_node)
            except LogicParserError as e:
                await manager.broadcast("notification", {
                    "level": "error",
                    "message": f"Invalid rule in '{strategy.name}': {e}"
                })
                # Stop the scan if the rule is fundamentally flawed
                break

            # Broadcast each found ticker
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
            break # Exit the loop cleanly on cancellation
        except Exception as e:
            await manager.broadcast("notification", {
                "level": "error",
                "message": f"An error occurred in '{strategy.name}' scan: {e}"
            })
            await asyncio.sleep(30)

    await manager.broadcast("scan_status_update", {
        "strategy_id": strategy.id,
        "status": "STOPPED",
        "message": f"Scan for '{strategy.name}' was stopped or encountered a fatal error."
    })


def start_scan(strategy: Strategy):
    if strategy.id in active_scans and not active_scans[strategy.id].done():
        return

    task = asyncio.create_task(_perform_scan(strategy))
    active_scans[strategy.id] = task

def stop_scan(strategy_id: int):
    task = active_scans.get(strategy_id)
    if not task or task.done():
        return

    task.cancel()
