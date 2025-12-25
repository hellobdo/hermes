import asyncio

from hermes.context import TradingContext
from hermes.session.alpaca import get_account_value, get_alpaca_clients, start_stream
from hermes.session.session import setup_session


def get_trading_context() -> TradingContext:
    is_paper, risk_pct, risk_reward = setup_session()
    client, stock_data = get_alpaca_clients(is_paper)
    account_value = get_account_value(client)
    stream_task = asyncio.create_task(start_stream(is_paper))

    return TradingContext(
        client=client,
        stock_data=stock_data,
        risk_pct=risk_pct,
        is_paper=is_paper,
        account_value=account_value,
        risk_reward=risk_reward,
        stream_task=stream_task,
    )
