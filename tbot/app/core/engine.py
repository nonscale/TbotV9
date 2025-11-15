# tbot/app/core/engine.py
import asyncio
import pandas as pd
from typing import Dict, List, Set

from tbot.app.models.strategy import Strategy, GroupNode, Node
from tbot.app.core.brokers.base import BaseBroker
from tbot.app.core.brokers.upbit import UpbitBroker
from tbot.app.core.websocket_manager import manager
from tbot.app.core.logic_parser import logic_parser, LogicParserError

active_scans: Dict[int, asyncio.Task] = {}

def _extract_timeframes(node: Node) -> Set[str]:
    """Recursively find all unique timeframes mentioned in the rule tree."""
    if node.type == 'condition' and node.timeframe:
        return {node.timeframe}
    if node.type == 'group':
        timeframes = set()
        for child in node.children:
            timeframes.update(_extract_timeframes(child))
        return timeframes
    return set()

async def _evaluate_ticker_second_scan(ticker: str, broker: BaseBroker, second_scan_node: GroupNode) -> bool:
    """
    Evaluates a single ticker against the 2nd scan rules by fetching required OHLCV data.
    This is a simplified version for Phase 7. Indicator calculation and multi-timeframe
    logic parsing will be implemented in later phases.
    """
    required_timeframes = _extract_timeframes(second_scan_node)
    if not required_timeframes:
        return True # No 2nd scan rules with timeframes to evaluate

    # Fetch all necessary OHLCV data concurrently
    fetch_tasks = [broker.fetch_ohlcv(ticker, tf, 200) for tf in required_timeframes]

    ohlcv_results = await asyncio.gather(*fetch_tasks)

    # For now, just check if all required data was successfully fetched.
    # A real implementation would involve a more complex parser that can handle multiple dataframes.
    for df in ohlcv_results:
        if df.empty:
            print(f"[{ticker}] Could not fetch some required OHLCV data for 2nd scan. Skipping.")
            return False

    return True

async def _perform_scan(strategy: Strategy):
    await manager.broadcast("scan_status_update", {"strategy_id": strategy.id, "status": "RUNNING", "message": f"Scan for '{strategy.name}' started."})

    broker = UpbitBroker()
    first_scan_node = strategy.scan_rules.first_scan
    second_scan_node = strategy.scan_rules.second_scan

    while True:
        try:
            # --- 1st Scan ---
            tickers_df = await broker.fetch_tickers()
            if tickers_df.empty:
                await asyncio.sleep(10); continue

            first_pass_tickers_df = logic_parser.apply_tree(tickers_df, first_scan_node)

            # --- 2nd Scan ---
            final_pass_tickers_df = pd.DataFrame()
            if second_scan_node and not first_pass_tickers_df.empty:
                evaluation_tasks = []
                tickers_to_evaluate = list(first_pass_tickers_df.index)
                for ticker in tickers_to_evaluate:
                    evaluation_tasks.append(_evaluate_ticker_second_scan(ticker, broker, second_scan_node))

                results = await asyncio.gather(*evaluation_tasks)

                final_pass_mask = [res for res in results if res]
                final_pass_tickers_df = first_pass_tickers_df.loc[final_pass_mask]
            else:
                final_pass_tickers_df = first_pass_tickers_df

            # --- Broadcast results ---
            for ticker, data in final_pass_tickers_df.iterrows():
                await manager.broadcast("scan_result_found", {
                    "strategy_name": strategy.name, "ticker": ticker, "timestamp": pd.Timestamp.now().isoformat(),
                    "details": {"price": data.get('close', 0), "volume": data.get('volume', 0), "amount": data.get('amount', 0)}
                })

            await asyncio.sleep(60)

        except asyncio.CancelledError:
            break
        except Exception as e:
            await manager.broadcast("notification", {"level": "error", "message": f"Error in '{strategy.name}' scan: {e}"})
            await asyncio.sleep(30)

    await manager.broadcast("scan_status_update", {"strategy_id": strategy.id, "status": "STOPPED", "message": "Scan stopped."})

def start_scan(strategy: Strategy):
    if strategy.id in active_scans and not active_scans[strategy.id].done(): return
    task = asyncio.create_task(_perform_scan(strategy))
    active_scans[strategy.id] = task

def stop_scan(strategy_id: int):
    task = active_scans.get(strategy_id)
    if not task or task.done(): return
    task.cancel()
