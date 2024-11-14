"""
Slim wrapper around ccxt's Precise (string math)
To have imports from freqtrade - and support float initializers
"""

from decimal import Decimal

from ccxt import Precise


class FtPrecise(Precise):
    def __init__(self, number, decimals=None):
        if not isinstance(number, str):
            number = str(number)
        super().__init__(number, decimals)


def get_profit(data: dict, default_value="0.0") -> Decimal:
    """
    Returns profit from the given data dictionary.
    """
    profit = Decimal(data.get("unrealizedPnl", 0))
    if not profit and data.get("unrealizedProfit", None):
        profit = Decimal(data["unrealizedProfit"])

    if not profit and isinstance(info := data.get("info", None), dict):
        profit = Decimal(info.get("unrealizedProfit", None))

    if not profit:
        return Decimal(default_value)

    return profit.quantize(Decimal('0.01'))
