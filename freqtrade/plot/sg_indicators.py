import pandas as pd


# The ICHIMOKU function adds several columns to the input DataFrame,
# each representing a component of the Ichimoku Kinko Hyo indicator.
def ICHIMOKU(df: pd.DataFrame, tenkan_period: int, kijun_period: int) -> pd:
    # Tenkan Sen : Short-term signal line
    df["rolling_min_tenkan"] = df["low"].rolling(window=tenkan_period).min()
    df["rolling_max_tenkan"] = df["high"].rolling(window=tenkan_period).max()

    df["tenkan_sen"] = (df["rolling_max_tenkan"] + df["rolling_min_tenkan"]) / 2

    df.drop(["rolling_min_tenkan", "rolling_max_tenkan"], axis=1, inplace=True)

    # Kijun Sen : Long-term signal line
    df["rolling_min_kijun"] = df["low"].rolling(window=kijun_period).min()
    df["rolling_max_kijun"] = df["high"].rolling(window=kijun_period).max()

    df["kijun_sen"] = (df["rolling_max_kijun"] + df["rolling_min_kijun"]) / 2

    df.drop(["rolling_min_kijun", "rolling_max_kijun"], axis=1, inplace=True)

    # Senkou Span A

    df["senkou_span_a"] = ((df["tenkan_sen"] + df["kijun_sen"]) / 2).shift(kijun_period)

    # Senkou Span B

    df["rolling_min_senkou"] = df["low"].rolling(window=kijun_period * 2).min()
    df["rolling_max_senkou"] = df["high"].rolling(window=kijun_period * 2).max()

    df["senkou_span_b"] = ((df["rolling_max_senkou"] + df["rolling_min_senkou"]) / 2).shift(
        kijun_period
    )

    df.drop(["rolling_min_senkou", "rolling_max_senkou"], axis=1, inplace=True)
    # Chikou Span : Confirmation Line

    df["chikou_span"] = df["close"].shift(-kijun_period)

    df["senkou_span_b_kp"] = df["senkou_span_b"].shift(kijun_period)

    return df


# The VWAP function calculates the Volume Weighted Average Price for a
# given DataFrame of stock data over a specified rolling window period.
# It adds the calculated VWAP values as a new column to the DataFrame
# and returns it.
def VWAP(df: pd.DataFrame, cumulative_period: int = 20) -> pd:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    volume = df["volume"]
    df = df.dropna(subset=["high", "low", "close", "volume"])
    typical_price = (high + low + close) / 3
    df["Typical_Price_Volume"] = typical_price * volume
    cumulative_typical_price_volume = (
        df["Typical_Price_Volume"].rolling(window=cumulative_period).sum()
    )
    cumulative_volume = df["volume"].rolling(window=cumulative_period).sum()
    vwap = cumulative_typical_price_volume / cumulative_volume.where(
        cumulative_volume != 0, other=pd.NA
    )
    df["VWAP"] = vwap
    return df


# Summary
# The back_candles function uses the VWAP function to calculate the VWAP for a given DataFrame.
# It then checks if the closing prices for the last back_candles periods are consistently above
# the VWAP and marks such periods in a new column back_candles.
# This can be useful for identifying trends or patterns in stock price movements.
def back_candles(df: pd.DataFrame, back_candles: int = 16) -> pd:
    vwap = VWAP(df)
    df["VWAP"] = vwap["VWAP"]

    df["back_candles"] = False

    if len(df) < back_candles:
        df["back_candles"] = False
        return df

    for i in range(back_candles, len(df)):
        previous_close = df["close"][i - back_candles : i]

        previous_vwap = df["VWAP"][i - back_candles : i]

        if all(previous_close > previous_vwap):
            df.at[i, "back_candles"] = True

    return df
