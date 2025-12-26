from alpaca.data.models import Quote
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.enums import OrderClass, OrderSide, OrderType, TimeInForce
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


def get_side_object(side: str) -> OrderSide:
    return OrderSide.BUY if side == "buy" else OrderSide.SELL


def get_quote(ctx: TradingContext, symbol: str) -> Quote:
    return ctx.stock_data.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]


def get_latest_price(ctx: TradingContext, symbol: str, side: str) -> float:
    quote = get_quote(ctx, symbol)

    return quote.ask_price if side == "buy" else quote.bid_price


def handle_order_entry(
    ctx: TradingContext,
    side: str,
    stop_loss_price: float,
    symbol: str,
):
    try:
        entry_price = get_latest_price(ctx, symbol, side)
        validate_orders(side, entry_price, stop_loss_price)
        side = get_side_object(side)
        qty = set_qty(entry_price, stop_loss_price, ctx.risk_amount, symbol)
        take_profit_price = define_take_profit_price(
            ctx, entry_price, stop_loss_price, side
        )

        order = create_bracket_order(
            symbol, qty, side, take_profit_price, stop_loss_price
        )
        ctx.client.submit_order(order)
    except Exception as e:
        print(f"Error submitting order: {e}")


def create_bracket_order(
    symbol: str,
    qty: int,
    side: OrderSide,
    take_profit_price: float,
    stop_loss_price: float,
) -> OrderRequest:
    return OrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC,
        order_class=OrderClass.BRACKET,
        take_profit=TakeProfitRequest(limit_price=take_profit_price),
        stop_loss=StopLossRequest(stop_price=stop_loss_price),
    )
