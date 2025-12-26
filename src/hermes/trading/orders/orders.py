from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    TimeInForce,
)
from alpaca.trading.requests import (
    LimitOrderRequest,
    MarketOrderRequest,
    StopLossRequest,
    StopOrderRequest,
)


def create_entry_order(
    symbol: str,
    qty: int,
    side: OrderSide,
) -> MarketOrderRequest:
    return MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.GTC,
    )


def create_limit_order_with_stop(
    symbol: str,
    qty: int,
    side: OrderSide,
    stop_loss_price: float,
    take_profit_price: float,
) -> LimitOrderRequest:
    return LimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        limit_price=take_profit_price,
        time_in_force=TimeInForce.GTC,
        order_class=OrderClass.OCO,
        stop_loss=StopLossRequest(stop_price=stop_loss_price),
    )


def create_stop_order(
    symbol: str, qty: int, side: OrderSide, stop_loss_price: float
) -> StopOrderRequest:
    return StopOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.GTC,
        stop_price=stop_loss_price,
    )
