from alpaca.trading.stream import TradingStream

trading_stream = TradingStream('api-key', 'secret-key', paper=True)

async def update_handler(data):
    # trade updates will arrive in our async handler
    print(data)

# subscribe to trade updates and supply the handler as a parameter
trading_stream.subscribe_trade_updates(update_handler)

# start our websocket streaming
trading_stream.run()