from datetime import datetime, timezone
from random import randint
from unittest.mock import MagicMock, PropertyMock

import ccxt
import pytest

from freqtrade.enums import CandleType, MarginMode, TradingMode
from freqtrade.exceptions import DependencyException, InvalidOrderException, OperationalException
from freqtrade.persistence import Trade
from tests.conftest import EXMS, get_mock_coro, get_patched_exchange, log_has_re
from tests.exchange.test_exchange import ccxt_exceptionhandlers


@pytest.mark.parametrize("candle_type", [CandleType.MARK, ""])
async def test__async_get_historic_ohlcv_binance(default_conf, mocker, caplog, candle_type):
    print("hello world")
    pass
