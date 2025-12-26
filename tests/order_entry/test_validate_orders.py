from hermes.trading.orders.utils import validate_orders
import pytest

def test_validate_buy_valid():
    assert validate_orders(side="buy", entry_price=100, stop_loss_price=95)

def test_validate_buy_invalid():
    assert not validate_orders(side="buy", entry_price=100, stop_loss_price=105)

def test_validate_sell_valid():
    assert validate_orders(side="sell", entry_price=100, stop_loss_price=105)

def test_validate_sell_invalid():
    assert not validate_orders(side="sell", entry_price=100, stop_loss_price=95)

def test_validate_invalid_side():
    with pytest.raises(ValueError, match="Side needs to be buy or sell"):
        validate_orders(side="invalid", entry_price=100, stop_loss_price=95)
