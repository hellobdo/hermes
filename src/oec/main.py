import os
from dataclasses import dataclass

from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
from prompt_toolkit.shortcuts import radiolist_dialog

load_dotenv()

is_paper = radiolist_dialog(
    title="Trading Mode",
    text="Select trading mode:",
    values=[(True, "Paper"), (False, "Live")],
).run()

api_key = (
    os.environ["ALPACA_API_KEY_PAPER"]
    if is_paper
    else os.environ["ALPACA_API_KEY_LIVE"]
)
secret_key = (
    os.environ["ALPACA_SECRET_KEY_PAPER"]
    if is_paper
    else os.environ["ALPACA_SECRET_KEY_LIVE"]
)


@dataclass
class TradingContext:
    client: TradingClient
    risk_pct: float
    is_paper: bool


ctx = TradingContext(
    client=TradingClient(api_key, secret_key, paper=is_paper),
    risk_pct=0.025,
    is_paper=is_paper,
)
