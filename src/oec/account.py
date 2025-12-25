from alpaca.trading.client import TradingClient

def get_account_size() -> float:
    
    
    


def define_account_type(type: bool) -> TradingClient:
    return TradingClient('api-key', 'secret-key', paper=type)