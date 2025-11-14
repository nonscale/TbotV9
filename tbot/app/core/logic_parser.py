# tbot/app/core/logic_parser.py
import pandas as pd
from typing import List

class LogicParserError(ValueError):
    """Custom exception for parsing errors."""
    pass

class PandasLogicParser:
    """
    Parses and applies a user-defined rule string to a pandas DataFrame.
    """
    FORBIDDEN_KEYWORDS: List[str] = [
        "__", "import", "eval", "exec", "lambda", "def",
        "os", "sys", "subprocess", "shutil", "glob"
    ]

    def _sanitize_rule(self, rule: str):
        """
        Performs a basic security check on the rule string.
        """
        rule_lower = rule.lower()
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in rule_lower:
                raise LogicParserError(f"Forbidden keyword '{keyword}' found in rule.")

        # Add more sophisticated checks here if needed in the future

    def apply(self, df: pd.DataFrame, rule: str) -> pd.DataFrame:
        """
        Applies the sanitized rule to the DataFrame using the `query` method.

        Args:
            df: The pandas DataFrame to filter.
            rule: A string containing the filter condition (e.g., "close > 1000 and amount > 100000").

        Returns:
            The filtered pandas DataFrame.

        Raises:
            LogicParserError: If the rule is invalid or contains forbidden keywords.
        """
        if not isinstance(rule, str) or not rule.strip():
            # If the rule is empty, return the original DataFrame
            return df

        self._sanitize_rule(rule)

        try:
            return df.query(rule, engine='python')
        except Exception as e:
            # Catch potential errors from pandas.query (e.g., syntax errors)
            raise LogicParserError(f"Invalid rule syntax: {e}") from e

# Create a single instance for the application to use
logic_parser = PandasLogicParser()
