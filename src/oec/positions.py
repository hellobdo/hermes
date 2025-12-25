from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

trading_client = TradingClient("api-key", "secret-key", paper=True)

# params to filter orders by
request_params = GetOrdersRequest(status=QueryOrderStatus.OPEN)

# orders that satisfy params
orders = trading_client.get_orders(filter=request_params)
positions = trading_client.get_all_positions()