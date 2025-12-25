from typing import List, Union

import questionary
from alpaca.trading.models import Order


def select_order(orders) -> str:
    choices = [f"{o.id}: {o.symbol} {o.side}" for o in orders]
    selected = questionary.select("Select order:", choices=choices).ask()
    return selected.split(":")[0]


def check_orders(ctx) -> Union[List[Order], bool]:
    orders = ctx.client.get_orders()
    return orders if orders else False
