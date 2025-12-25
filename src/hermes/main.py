import asyncio
import os

import questionary
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
from dotenv import load_dotenv
from prompt_toolkit.shortcuts import prompt

from .context import TradingContext
from .info_methods import get_open_orders, get_open_positions
from .order_entry import handle_order_entry


async def start_stream(api_key, secret_key, is_paper):
    # trade updates will arrive in our async handler
    trading_stream = TradingStream(api_key, secret_key, paper=is_paper)

    async def update_handler(data):
        print(data)

    trading_stream.subscribe_trade_updates(update_handler)
    await trading_stream._run_forever()


def get_trading_mode():
    return (
        questionary.select("Select trading mode:", choices=["Paper", "Live"]).ask()
        == "Paper"
    )


def get_risk_pct():
    risk_pct_input = prompt("Risk Percentage (default: 0.25%).\n> ")
    risk_pct = float(risk_pct_input or "0.25") / 100
    print(f"Risk Percentage for the session is {risk_pct * 100}%")
    return risk_pct


async def main():
    load_dotenv()

    is_paper = get_trading_mode()
    risk_pct = get_risk_pct()
    risk_reward_input = prompt("Risk/Reward Ratio. (default: 5).\n> ")
    risk_reward = float(risk_reward_input or "5")
    print(f"Risk Reward for the session is {risk_reward}")

    api_key = (
        os.environ["ALPACA_API_KEY_PAPER"]
        if is_paper
        else os.environ["ALPACA_API_KEY_LIVE"]
    )
    secret_key = (
        os.environ["ALPACA_SECRET_KEY_PAPER"]
        if is_paper
        else os.environ["ALPACA_SECRET_KEY_LIVE"]
    )

    client = TradingClient(api_key, secret_key, paper=is_paper, raw_data=False)
    stock_data = StockHistoricalDataClient(api_key, secret_key)

    account_value = float(client.get_account().last_equity or 0)
    print(f"Account value for risk calculations today is {account_value}")

    ctx = TradingContext(
        client=client,
        stock_data=stock_data,
        risk_pct=risk_pct,
        is_paper=is_paper,
        account_value=account_value,
        risk_reward=risk_reward,
    )

    asyncio.create_task(start_stream(api_key, secret_key, is_paper))

    print(
        f"Creating session...\n Risk Percentage: {risk_pct} \n Risk Reward: {risk_reward} \n Account Value: {account_value}"
    )

    while True:
        input = prompt("> ")

        if input == "orders":
            print(get_open_orders(ctx))
        elif input == "positions":
            print(get_open_positions(ctx))
        else:
            symbol, side, stop_loss = input.split()
            if side.lower() not in ["buy", "sell"]:
                print("Side must be buy or sell")
                continue
            stop_loss_price = float(stop_loss)
            handle_order_entry(ctx, side, stop_loss_price, symbol)


if __name__ == "__main__":
    asyncio.run(main())
