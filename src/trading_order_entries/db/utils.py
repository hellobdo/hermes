import polars as pl
from alpaca.trading.models import Order

from trading_order_entries.context import TradingContext


def handle_inserting_stop_orders(ctx: TradingContext, stop_order: Order) -> None:
    order_dict = stop_order.model_dump()
    df = pl.DataFrame([order_dict])

    df = df.select(
        pl.col("id").alias("execution_id"),
        pl.col("created_at"),
        pl.col("stop_price"),
        pl.col("qty"),
        pl.col("status"),
        pl.col("symbol"),
        pl.col("side"),
        pl.col("type"),
        pl.lit(ctx.account_id).alias("account_id"),
    )

    ctx.db.log_stop_orders(df)
    print("Stop orders inserted in DB")
