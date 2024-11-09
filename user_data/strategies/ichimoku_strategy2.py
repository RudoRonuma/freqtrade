# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these imports ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
# from typing import Dict, Optional, Union, Tuple

from freqtrade.strategy import (
    IStrategy,
    Trade,
    Order,
    PairLocks,
    informative,  # @informative decorator
    # Hyperopt Parameters
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    RealParameter,
    # timeframe helpers
    timeframe_to_minutes,
    timeframe_to_next_date,
    timeframe_to_prev_date,
    # Strategy helper functions
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
)
import freqtrade.plot.sg_indicators as SGI

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
from technical import qtpylib

# taken from https://github.com/SG-SoftwareSolutions/freqtrade/blob/develop/user_data/strategies/ichimoku_strategy2.py

candle_count = 0


class IchimokuStrategy2(IStrategy):
    """
    This is a strategy template to get you started.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy.
    timeframe = "5m"

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {"30": 0.15}

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.08

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Strategy parameters
    buy_rsi = IntParameter(10, 40, default=30, space="buy")
    sell_rsi = IntParameter(60, 90, default=70, space="sell")  # Optional order type mapping.
    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    # Optional order time in force.
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    @property
    def plot_config(self):
        return {
            # Main plot indicators (Moving averages, ...)
            "main_plot": {
                "tema": {},
                "sar": {"color": "white"},
            },
            "subplots": {
                # Subplots - each dict defines one additional plot
                "MACD": {
                    "macd": {"color": "blue"},
                    "macdsignal": {"color": "orange"},
                },
                "RSI": {
                    "rsi": {"color": "red"},
                },
            },
        }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """
        # Momentum Indicators
        # ------------------------------------

        # RSI
        dataframe["rsi"] = ta.RSI(dataframe)

        # MACD
        # macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        # dataframe["macd"] = macd["macd"]
        # dataframe["macdsignal"] = macd["macdsignal"]
        # dataframe["macdhist"] = macd["macdhist"]

        # Custom ICHIMOKU

        ichimoku = SGI.ICHIMOKU(dataframe, 9, 26)
        dataframe["tenkan_sen"] = ichimoku["tenkan_sen"]
        dataframe["kijun_sen"] = ichimoku["kijun_sen"]
        dataframe["senkou_span_a"] = ichimoku["senkou_span_a"]
        dataframe["senkou_span_b"] = ichimoku["senkou_span_b"]
        dataframe["senkou_span_b_kp"] = ichimoku["senkou_span_b_kp"]

        dataframe["chikou_span"] = ichimoku["chikou_span"]
        dataframe["tenkan_minus_kijun"] = ichimoku["tenkan_sen"] - ichimoku["kijun_sen"]
        dataframe["prev_tenkan_minus_kijun"] = ichimoku["tenkan_minus_kijun"].shift(1)

        # EMA - Exponential Moving Average
        dataframe["ema100"] = ta.EMA(dataframe, timeperiod=100)

        """
        # first check if dataprovider is available
        if self.dp:
            if self.dp.runmode.value in ("live", "dry_run"):
                ob = self.dp.orderbook(metadata["pair"], 1)
                dataframe["best_bid"] = ob["bids"][0][0]
                dataframe["best_ask"] = ob["asks"][0][0]
        """

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe["chikou_span"], dataframe["senkou_span_b_kp"]))
                # & (dataframe["tenkan_minus_kijun"] > 0)
                # & (dataframe["rsi"] < 65)
                # & (dataframe["close"] > dataframe["senkou_span_a"])
                & (dataframe["volume"] > 0)
                # & (qtpylib.crossed_above(dataframe["close"], dataframe["ema200"]))
                # Make sure Volume is not 0
            ),
            "enter_long",
        ] = 1

        # print(dataframe)

        # Uncomment to use shorts (Only used in futures/margin mode.
        # Check the documentation for more info)
        """
        dataframe.loc[
            (
                # Signal: RSI crosses above sell_rsi
                (qtpylib.crossed_above(dataframe["rsi"], self.sell_rsi.value)) &
                (dataframe["tema"] > dataframe["bb_middleband"]) &  # Guard: tema above BB middle
                (dataframe["tema"] < dataframe["tema"].shift(1)) &  # Guard: tema is falling
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'enter_short'] = 1
        """

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """

        dataframe.loc[
            (
                # (dataframe["macd"] < dataframe["macdsignal"])
                # & (dataframe["macd"].shift(1) >= dataframe["macdsignal"]).shift(1)
                # Make sure Volume is not 0 senkou_span_b_kp
                (qtpylib.crossed_above(dataframe["senkou_span_b_kp"], dataframe["chikou_span"]))
                & (dataframe["volume"] > 0)
                # (dataframe["ema100"] > dataframe["close"])
            ),  # Make sure Volume is not 0
            "exit_long",
        ] = 1
        # Uncomment to use shorts (Only used in futures/margin mode.
        # Check the documentation for more info)
        """
        dataframe.loc[
            (
             # Signal: RSI crosses above buy_rsi
                (qtpylib.crossed_above(dataframe["rsi"], self.buy_rsi.value)) &
                (dataframe["tema"] <= dataframe["bb_middleband"]) &  # Guard: tema below BB middle
                (dataframe["tema"] > dataframe["tema"].shift(1)) &  # Guard: tema is raising
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'exit_short'] = 1
        """
        return dataframe
