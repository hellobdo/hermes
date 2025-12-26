import json
from typing import Tuple

from alpaca.data.models import Quote
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    OrderType,
    PositionIntent,
    TimeInForce,
)
from alpaca.trading.requests import OrderRequest, StopLossRequest, TakeProfitRequest

from hermes.context import TradingContext
from hermes.trading.risk_manager import (
    define_take_profit_price,
    set_qty,
)


def validate_orders(side: str, entry_price: float, stop_loss_price: float) -> bool:
    if side == "buy":
        return False if entry_price < stop_loss_price else True
    elif side == "sell":
        return False if entry_price > stop_loss_price else True
    else:
        raise ValueError("Side needs to be buy or sell")


def get_entry_side_object(side: str) -> OrderSide:
    return OrderSide.BUY if side == "buy" else OrderSide.SELL


def get_exit_side_object(side: str) -> OrderSide:
    return OrderSide.SELL if side == "buy" else OrderSide.BUY


def get_quote(ctx: TradingContext, symbol: str) -> Quote:
    return ctx.stock_data.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]


def get_latest_price(ctx: TradingContext, symbol: str, side: str) -> float:
    quote = get_quote(ctx, symbol)

    return quote.ask_price if side == "buy" else quote.bid_price


def get_qty_split(qty: int) -> Tuple:
    qty_partial_fills = int(round(qty * 0.5))
    remaining_qty = qty - qty_partial_fills

    return qty_partial_fills, remaining_qty


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

    order_partial_fills_one = create_exit_order(
        symbol, qty_partial_fills, side, stop_loss_price, take_profit_price
    )
    order_remaining_stop = create_exit_order(
        symbol, remaining_qty, side, stop_loss_price, take_profit_price
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


def create_entry_order(
    symbol: str,
    qty: int,
    side: OrderSide,
) -> OrderRequest:
    return OrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC,
    )


def create_exit_order(
    symbol: str,
    qty: int,
    side: OrderSide,
    stop_loss_price: float,
    take_profit_price: float,
) -> OrderRequest:
    return OrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
        order_class=OrderClass.OCO,
        take_profit=TakeProfitRequest(limit_price=take_profit_price),
        stop_loss=StopLossRequest(stop_price=stop_loss_price),
        position_intent=PositionIntent.SELL_TO_CLOSE
        if side == OrderSide.SELL
        else PositionIntent.BUY_TO_CLOSE,
    )
