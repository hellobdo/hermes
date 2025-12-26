import json

from hermes.context import TradingContext
from hermes.trading.orders.orders import (
    create_entry_order,
    create_limit_order_with_stop,
    create_stop_order,
)
from hermes.trading.orders.utils import (
    get_entry_side_object,
    get_exit_side_object,
    get_latest_price,
    get_qty_split,
    validate_orders,
)
from hermes.trading.risk_manager import (
    define_take_profit_price,
    set_qty,
)


def handle_exit_orders(
    ctx: TradingContext,
    side: str,
    symbol: str,
    qty: int,
    stop_loss_price: float,
    take_profit_price: float,
):
    qty_partial_fills, remaining_qty = get_qty_split(qty)
    side = get_exit_side_object(side)

    order_partial_fills_one = create_limit_order_with_stop(
        symbol, qty_partial_fills, side, stop_loss_price, take_profit_price
    )
    order_remaining_stop = create_stop_order(
        symbol, remaining_qty, side, stop_loss_price
    )

    ctx.client.submit_order(order_partial_fills_one)
    ctx.client.submit_order(order_remaining_stop)


def handle_order_entry(
    ctx: TradingContext,
    side: str,
    stop_loss_price: float,
    symbol: str,
    is_options: bool,
):
    try:
        entry_price = get_latest_price(ctx, symbol, side)
        print(f"Entry price is {entry_price}")
        validate_orders(side, entry_price, stop_loss_price)
        side = get_entry_side_object(side)
        qty = set_qty(entry_price, stop_loss_price, ctx.risk_amount, is_options)
        take_profit_price = define_take_profit_price(
            ctx, entry_price, stop_loss_price, side
        )

        order = create_entry_order(symbol, qty, side)
        response = ctx.client.submit_order(order)

        ctx.pending_orders[response.id] = {
            "side": side,
            "symbol": symbol,
            "qty": qty,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
        }

    except Exception as e:
        try:
            error_data = json.loads(str(e))
            print(f"Error submitting order: {error_data['message']}")
        except Exception:
            print(f"Error submitting order: {e}")
