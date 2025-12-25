import asyncio

from prompt_toolkit.shortcuts import PromptSession

from hermes.session.helpers import check_orders, select_order
from hermes.session.main import get_trading_context
from hermes.trading.order_entry import handle_order_entry


async def main(ctx):
    print(
        f"""Creating session...
        Trading Mode: {ctx.is_paper}
        Risk Percentage: {ctx.risk_pct * 100}%
        Risk Reward: {ctx.risk_reward}
        Account Value: {ctx.account_value}
        Methods:
            * <orders> to get open orders
            * <positions> to get open positions
            * <cancel order> to cancel a specific order
            * <cancel all orders> to cancel all open orders
            * <AAPL buy 123> to buy AAPL with stop loss 123
            * <AAPL sell 123> to short AAPL with stop loss 123
            * <exit> to leave
        """
    )

    session = PromptSession()
    while True:
        input = await session.prompt_async("> ")

        if input == "orders":
            print(ctx.client.get_orders())
        elif input == "positions":
            print(ctx.client.get_all_positions())
        elif input == "cancel order":
            orders = check_orders(ctx)
            if not orders:
                print("No open orders")
                continue
            order_id = select_order(orders)
            ctx.client.cancel_order_by_id(order_id)
        elif input == "cancel all orders":
            ctx.client.cancel_orders()
            orders = ctx.client.get_orders()
            if not orders:
                print("No open orders")
                continue
        elif input == "exit":
            ctx.stream_task.cancel()
            break
        else:
            symbol, side, stop_loss = input.split()
            if side.lower() not in ["buy", "sell"]:
                print("Side must be buy or sell")
                continue
            stop_loss_price = float(stop_loss)
            handle_order_entry(ctx, side, stop_loss_price, symbol)


def cli():
    ctx = get_trading_context()
    asyncio.run(main(ctx))


if __name__ == "__main__":
    cli()
