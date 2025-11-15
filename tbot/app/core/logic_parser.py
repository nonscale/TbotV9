# tbot/app/core/logic_parser.py
import pandas as pd
from typing import List
from tbot.app.models.strategy import GroupNode, ConditionNode, Node

class LogicParserError(ValueError):
    """Custom exception for parsing errors."""
    pass

class PandasLogicParser:
    """
    Parses a tree-like rule structure and converts it into a pandas query string.
    """
    FORBIDDEN_KEYWORDS: List[str] = [
        "__", "import", "eval", "exec", "lambda", "def",
        "os", "sys", "subprocess", "shutil", "glob"
    ]

    def _sanitize_condition(self, condition: str):
        """
        Performs a basic security check on an individual condition string.
        """
        condition_lower = condition.lower()
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in condition_lower:
                raise LogicParserError(f"Forbidden keyword '{keyword}' found in condition.")

    def _parse_node(self, node: Node) -> str:
        """
        Recursively traverses the node tree and builds a query string.
        """
        if node.type == 'condition':
            self._sanitize_condition(node.value)
            return f"({node.value})"

        if node.type == 'group':
            if not node.children:
                return "" # An empty group has no effect

            separator = f" {node.operator.lower()} "
            child_queries = [self._parse_node(child) for child in node.children if self._parse_node(child)]

            if not child_queries:
                return ""

            return f"({separator.join(child_queries)})"

        raise LogicParserError(f"Unknown node type: {getattr(node, 'type', 'N/A')}")

    def apply_tree(self, df: pd.DataFrame, root_node: GroupNode) -> pd.DataFrame:
        """
        Applies the parsed rule tree to the DataFrame.

        Args:
            df: The pandas DataFrame to filter.
            root_node: The root GroupNode of the rule tree.

        Returns:
            The filtered pandas DataFrame.

        Raises:
            LogicParserError: If the rule tree is invalid.
        """
        if not root_node or not root_node.children:
            return df # No rules to apply

        query_string = self._parse_node(root_node)

        if not query_string:
            return df

        try:
            return df.query(query_string, engine='python')
        except Exception as e:
            raise LogicParserError(f"Invalid query syntax generated from tree: {e}") from e

# Create a single instance for the application to use
logic_parser = PandasLogicParser()
