# tbot/app/core/brokers/base.py
from abc import ABC, abstractmethod
import pandas as pd

class BaseBroker(ABC):
    """
    Abstract base class for all brokers.
    Defines the common interface for market data operations.
    """

    @abstractmethod
    async def fetch_tickers(self) -> pd.DataFrame:
        """
        Fetches the latest ticker information for all symbols in the market.

        This method is intended for the 1st phase of the scan, providing a broad
        overview of the market's current state (OHLCV, volume, etc.).

        Returns:
            A pandas DataFrame containing the ticker information, indexed by symbol.
            The columns must be standardized according to the PRD's data column standards
            (e.g., 'open', 'high', 'low', 'close', 'volume', 'amount').
        """
        pass

    @abstractmethod
    async def fetch_ohlcv(self, ticker: str, timeframe: str, count: int) -> pd.DataFrame:
        """
        Fetches historical OHLCV data for a specific ticker.

        Args:
            ticker: The ticker symbol (e.g., "KRW-BTC").
            timeframe: The time interval (e.g., 'day', 'minute1', 'minute5').
            count: The number of data points to retrieve.

        Returns:
            A pandas DataFrame with OHLCV data, indexed by datetime.
        """
        pass
