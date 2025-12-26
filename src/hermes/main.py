import asyncio

from prompt_toolkit.shortcuts import PromptSession

from hermes.options.main import parsing_options
from hermes.session.alpaca import start_stream
from hermes.session.main import get_trading_context
from hermes.trading.order_entry import handle_order_entry


async def main(ctx):
    asyncio.create_task(start_stream(ctx.is_paper))

    session_details = f"""
    Trading Mode: {ctx.is_paper}
    Risk Percentage: {ctx.risk_pct * 100}%
    Risk Reward: {ctx.risk_reward}
    Account Value: {ctx.account_value}
    Methods:
        * <orders> lists all standing orders
        * <positions> lists all positions
        * <AAPL buy 123> to buy AAPL with stop loss 123
        * <AAPL sell 123> to short AAPL with stop loss 123
        * <chain AAPL> to list option expiries and create an option order
        * <help> to list available methods
        * <exit> to leave
    """

    print("\033[2J\033[H", end="")  # Clear terminal
    print(
        f"""Creating session...
            {session_details}
        """
    )

    session = PromptSession()
    while True:
        input = await session.prompt_async("> ")

        if input == "orders":
            orders = ctx.client.get_orders()
            print(f"{orders}") if orders else print("No standing orders")
        elif input == "positions":
            positions = ctx.client.get_all_positions()
            print(f"{positions}") if positions else print("No standing orders")
        elif input == "help":
            print(f"{session_details}")
        elif input == "exit":
            print("Exiting...")
            break
        elif "chain" in input:
            try:
                option_symbol = await parsing_options(ctx, input)

                if option_symbol:
                    stop_input = await session.prompt_async("Stop price: ")
                    stop_price = float(stop_input)

                    print(
                        f"\nSubmitting order for {option_symbol} and stop price {stop_price}"
                    )
                    handle_order_entry(
                        ctx,
                        side="buy",
                        stop_loss_price=stop_price,
                        symbol=option_symbol,
                        is_options=True,
                    )
                else:
                    print("No option symbol found")
            except Exception as e:
                print(f"Error submitting order: {e}")

        else:
            symbol, side, stop_loss = input.split()
            if side.lower() not in ["buy", "sell"]:
                print("Side must be buy or sell")
                continue
            stop_loss_price = float(stop_loss)
            handle_order_entry(ctx, side, stop_loss_price, symbol, is_options=False)


def cli():
    ctx = get_trading_context()
    asyncio.run(main(ctx))


if __name__ == "__main__":
    cli()
