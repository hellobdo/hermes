import polars as pl
from alpaca.trading.client import TradingClient

from trading_order_entries.context import TradingContext
from trading_order_entries.db.db import DuckDBConnector
from trading_order_entries.session.alpaca import get_account_value, get_alpaca_clients
from trading_order_entries.session.session import setup_session


def get_account_id(client: TradingClient, db: DuckDBConnector) -> int:
    account_nr = client.get_account().account_number
    db_accounts = db.get_account_ids()

    account_id = (
        db_accounts.filter(pl.col("account_number") == account_nr).select("id").item()
    )

    return account_id


def get_trading_context() -> TradingContext:
    is_paper, risk_pct, risk_reward = setup_session()
    client, stock_data, option_data = get_alpaca_clients(is_paper)
    account_value, account_currency = get_account_value(client)
    db = DuckDBConnector()
    account_id = get_account_id(client, db)

    session_type = "Paper" if is_paper else "Live"

    print(f"Starting a {session_type} session now... \n")

    return TradingContext(
        client=client,
        stock_data=stock_data,
        option_data=option_data,
        db=db,
        account_id=account_id,
        risk_pct=risk_pct,
        is_paper=is_paper,
        account_value=account_value,
        account_currency=account_currency,
        risk_reward=risk_reward,
        risk_amount=risk_pct * account_value,
    )
