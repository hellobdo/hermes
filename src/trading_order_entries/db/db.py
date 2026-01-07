import os

import duckdb
import polars as pl
from dotenv import load_dotenv

load_dotenv()


class DuckDBConnector:
    def __init__(self):
        self._setup_motherduck_token()
        self.conn = duckdb.connect("md:stocksdb")

    def __enter__(self):
        self.conn.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()
        return False

    def _setup_motherduck_token(self) -> None:
        """Set up MotherDuck token if available."""
        token = os.getenv("MOTHERDUCK_TOKEN")
        if token:
            os.environ["motherduck_token"] = token

    def log_stop_orders(self, df: pl.DataFrame) -> None:
        """
        Add stop orders to the database.
        """

        self.conn.execute(
            """INSERT INTO stop_orders (
                execution_id,
                created_at,
                stop_price,
                qty,
                status,
                symbol,
                side,
                type,
                account_id
            )
            SELECT * FROM df ON CONFLICT (execution_id) DO NOTHING
            """
        )

    def get_account_ids(self) -> pl.DataFrame:
        """
        Get executions.
        """

        return self.conn.execute(
            """
            SELECT id, account_number
            FROM accounts
            """
        ).pl()
