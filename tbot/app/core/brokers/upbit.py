# tbot/app/core/brokers/upbit.py
import pyupbit
import pandas as pd
from typing import Dict
import asyncio

from tbot.app.core.brokers.base import BaseBroker

class UpbitBroker(BaseBroker):
    """
    Upbit broker implementation.
    """
    # pyupbit returns columns in Korean or specific names.
    # This map standardizes them according to the PRD.
    COLUMN_MAP: Dict[str, str] = {
        "opening_price": "open",
        "high_price": "high",
        "low_price": "low",
        "trade_price": "close",
        "acc_trade_volume": "volume",
        "acc_trade_price": "amount",
    }

    async def fetch_tickers(self) -> pd.DataFrame:
        """
        Fetches the latest ticker information for all KRW market symbols from Upbit.
        """
        # pyupbit is a synchronous library, so we run it in a thread pool
        # to avoid blocking the asyncio event loop.
        loop = asyncio.get_running_loop()
        tickers_data = await loop.run_in_executor(
            None, pyupbit.get_current_price, "KRW"
        )

        if not isinstance(tickers_data, dict):
             # In case of API error, it might not return a dict
            return pd.DataFrame()

        # pyupbit.get_current_price returns a dictionary of dictionaries.
        # We convert it to a DataFrame.
        df = pd.DataFrame.from_dict(tickers_data, orient="index")

        # Standardize column names
        df.rename(columns=self.COLUMN_MAP, inplace=True)

        # Ensure all standard columns exist, filling missing ones with 0
        for col in self.COLUMN_MAP.values():
            if col not in df.columns:
                df[col] = 0

        return df
