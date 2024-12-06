
from typing import Optional


class CoinScanInfo:
    base_currency: str = ""
    base_currency_desc: str = ""
    base_currency_logoid: str = ""
    update_mode: str = ""
    type: str = ""
    typespecs: str = ""
    exchange: str = ""
    crypto_total_rank: Optional[int] = None
    recommend_all: Optional[float] = None
    recommend_ma: Optional[float] = None
    recommend_other: Optional[float] = None
    RSI: Optional[float] = None
    Mom: Optional[float] = None
    pricescale: Optional[int] = None
    minmov: Optional[int] = None
    fractional: Optional[bool] = None
    minmove2: Optional[int] = None
    AO: Optional[float] = None
    CCI20: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    profit_addresses_percentage: Optional[float] = None
    sentiment: Optional[float] = None
    socialdominance: Optional[float] = None
    galaxyscore: Optional[int] = None
    social_volume_24h: Optional[int] = None
    altrank: Optional[int] = None
    large_tx_count: Optional[int] = None
    close_price: Optional[float] = None
    currency: Optional[str] = None
    change_abs: Optional[float] = None
    volatility_d: Optional[float] = None

    def get_tech_rating_str(self) -> str:
        if self.recommend_all is None:
            return "N/A"

        is_negative = False
        emoji = "🟢"
        if self.recommend_all < 0:
            is_negative = True
            self.recommend_all = abs(self.recommend_all)
            emoji = "🔴"

        if self.recommend_all > 0.5:
            return f"{emoji} Strong {'Sell' if is_negative else 'Buy'}"

        if self.recommend_all > 0.1:
            return f"{emoji} {'Sell' if is_negative else 'Buy'}"

        return "Neutral"

    def get_ma_rating_str(self) -> str:
        if self.recommend_ma is None:
            return "N/A"

        is_negative = False
        emoji = "🟢"
        if self.recommend_ma < 0:
            is_negative = True
            self.recommend_ma = abs(self.recommend_ma)
            emoji = "🔴"

        if self.recommend_ma > 0.5:
            return f"{emoji} Strong {'Sell' if is_negative else 'Buy'}"

        if self.recommend_ma > 0.1:
            return f"{emoji} {'Sell' if is_negative else 'Buy'}"

        return "Neutral"

    def get_os_rating_str(self) -> str:
        if self.recommend_other is None:
            return "N/A"

        is_negative = False
        emoji = "🟢"
        if self.recommend_other < 0:
            is_negative = True
            self.recommend_other = abs(self.recommend_other)
            emoji = "🔴"

        if self.recommend_other > 0.5:
            return f"{emoji} Strong {'Sell' if is_negative else 'Buy'}"

        if self.recommend_other > 0.1:
            return f"{emoji} {'Sell' if is_negative else 'Buy'}"

        return "Neutral"

    def get_addresses_in_profit_str(self) -> str:
        if self.profit_addresses_percentage is None:
            return "N/A"
        return f"{self.profit_addresses_percentage:.2f}%"

    def get_sentiment_str(self) -> str:
        if self.sentiment is None:
            return "N/A"
        return f"{self.sentiment:.2f}%"

    def get_socialdominance_str(self) -> str:
        if self.socialdominance is None:
            return "N/A"
        return f"{self.socialdominance:.2f}%"


    def parse_as_markdown(self) -> str:
        text = f"*{self.crypto_total_rank}. {self.base_currency_desc} ({self.base_currency})*:\n"
        text += f"  *• Tech Rating:* {self.get_tech_rating_str()}\n"
        text += f"  *• MA Rating:* {self.get_ma_rating_str()}\n"
        text += f"  *• Os Rating:* {self.get_os_rating_str()}\n"

        if self.profit_addresses_percentage:
            text += f"  *• In Profit:* {self.get_addresses_in_profit_str()}\n"

        if self.sentiment:
            text += f"  *• Sentiment:* {self.get_sentiment_str()}\n"

        if self.socialdominance:
            text += f"  *• Social Dominance:* {self.get_socialdominance_str()}\n"

        if self.galaxyscore:
            text += f"  *• Galaxy Score:* {self.galaxyscore}\n"

        if self.social_volume_24h:
            text += f"  *• Social Volume 24h:* {self.social_volume_24h}\n"

        if self.altrank:
            text += f"  *• AltRank:* {self.altrank}\n"

        if self.large_tx_count:
            text += f"  *• Large TX Count:* {self.large_tx_count}\n"

        if self.close_price and self.currency:
            text += f"  *• Price:* `{self.close_price} {self.currency}`"
            text += f" (`{self.change_abs:+.2f}`)\n"

        if self.volatility_d:
            text += f"  *• Volatility:* {self.volatility_d:.2f}%\n"

        return text


    @staticmethod
    def _parse(data: list) -> "CoinScanInfo":
        instance = CoinScanInfo()
        instance.base_currency = data[0]
        instance.base_currency_desc = data[1]
        instance.base_currency_logoid = data[2]
        instance.update_mode = data[3]
        instance.type = data[4]
        instance.typespecs = data[5]
        instance.exchange = data[6]
        instance.crypto_total_rank = data[7]
        instance.recommend_all = data[8]
        instance.recommend_ma = data[9]
        instance.recommend_other = data[10]
        instance.RSI = data[11]
        instance.Mom = data[12]
        instance.pricescale = data[13]
        instance.minmov = data[14]
        instance.fractional = data[15]
        instance.minmove2 = data[16]
        instance.AO = data[17]
        instance.CCI20 = data[18]
        instance.stoch_k = data[19]
        instance.stoch_d = data[20]
        instance.profit_addresses_percentage = data[21]
        instance.sentiment = data[22]
        instance.socialdominance = data[23]
        instance.galaxyscore = int(data[24] or 0)
        instance.social_volume_24h = int(data[25] or 0)
        instance.altrank = int(data[26] or 0)
        instance.large_tx_count = int(data[27] or 0)
        instance.close_price = data[28]
        instance.currency = data[29]
        instance.change_abs = data[30]
        instance.volatility_d = data[31]

        return instance
