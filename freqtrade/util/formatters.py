from decimal import Decimal

from freqtrade.constants import DECIMAL_PER_COIN_FALLBACK, DECIMALS_PER_COIN


def decimals_per_coin(coin: str):
    """
    Helper method getting decimal amount for this coin
    example usage: f".{decimals_per_coin('USD')}f"
    :param coin: Which coin are we printing the price / value for
    """
    return DECIMALS_PER_COIN.get(coin, DECIMAL_PER_COIN_FALLBACK)


def strip_trailing_zeros(value: str) -> str:
    """
    Strip trailing zeros from a string
    :param value: Value to be stripped
    :return: Stripped value
    """
    return value.rstrip("0").rstrip(".")


def round_value(value: float, decimals: int, keep_trailing_zeros=False) -> str:
    """
    Round value to given decimals
    :param value: Value to be rounded
    :param decimals: Number of decimals to round to
    :param keep_trailing_zeros: Keep trailing zeros "222.200" vs. "222.2"
    :return: Rounded value as string
    """
    val = f"{value:.{decimals}f}"
    if not keep_trailing_zeros:
        val = strip_trailing_zeros(val)
    return val


def fmt_coin(value: float, coin: str, show_coin_name=True, keep_trailing_zeros=False) -> str:
    """
    Format price value for this coin
    :param value: Value to be printed
    :param coin: Which coin are we printing the price / value for
    :param show_coin_name: Return string in format: "222.22 USDT" or "222.22"
    :param keep_trailing_zeros: Keep trailing zeros "222.200" vs. "222.2"
    :return: Formatted / rounded value (with or without coin name)
    """
    val = round_value(value, decimals_per_coin(coin), keep_trailing_zeros)
    if show_coin_name:
        val = f"{val} {coin}"

    return val


def normalize_money(
    value: Decimal, decimal_points_limit: int = None, currency_sign: str = "$"
) -> str:
    """
    Format a Decimal value with thousands separators.

    Args:
        value (Decimal): The Decimal value to format.

    Returns:
        str: The formatted string representation.
    """
    # Split the number into integer and decimal parts
    integer_part, decimal_part = str(value).split(".")

    # Add thousands separators to the integer part
    formatted_integer = f"{int(integer_part):,}"

    # if decimal_part only has 0, put 1 zero only
    if decimal_part != "0" and int(decimal_part) == 0:
        decimal_part = "0"

    # decimal parts should only show 2 decimal places
    if decimal_points_limit and len(decimal_part) > decimal_points_limit:
        decimal_part = decimal_part[:decimal_points_limit]

    # Combine the formatted integer part with the decimal part
    return f"{formatted_integer}.{decimal_part}{currency_sign}"


def str_to_decimal(money_str: str) -> Decimal:
    """
    Convert a human-readable money string to a Decimal object.

    Supports formats like:
    120$, 120.5$, 120, 120,3456345$, 156, 654, 780$

    Args:
        money_str (str): The money string to convert.

    Returns:
        Decimal: The converted Decimal value.

    Raises:
        ValueError: If the input string cannot be parsed as a valid money amount.
    """
    # Remove currency symbol and whitespace
    cleaned_str = money_str.replace("$", "").replace(", ", "").replace(" ", "")

    # Remove commas, but only if they're used as thousand separators
    if "," in cleaned_str:
        parts = cleaned_str.split(".")
        if len(parts) == 1 or (len(parts) == 2 and len(parts[1]) <= 3):
            cleaned_str = cleaned_str.replace(",", "")

    # Convert to Decimal
    return Decimal(cleaned_str)
