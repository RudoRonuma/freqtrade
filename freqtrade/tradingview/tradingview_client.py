


import json
from typing import Optional

from .tradingview_types import CoinScanInfo


class TradingViewClient:
    """TradingViewClient class to interact with TradingView API."""


    def __init__(self) -> None:
        pass

    async def get_coin_scan(self,
                            coin_filter: Optional[str] = None,
                            limit: int = 200,
                            offset: int = 0) -> list['CoinScanInfo']:
        import httpx
        cookies = {
            'cookiesSettings': '{"analytics":true,"advertising":true}',
            'cookiePrivacyPreferenceBannerProduction': 'accepted',
        }

        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://www.tradingview.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.tradingview.com/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                '(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'),
        }

        params = {
            'label-product': 'screener-coin',
        }

        data = {
            "columns": [
                "base_currency",
                "base_currency_desc",
                "base_currency_logoid",
                "update_mode",
                "type",
                "typespecs",
                "exchange",
                "crypto_total_rank",
                "Recommend.All",
                "Recommend.MA",
                "Recommend.Other",
                "RSI",
                "Mom",
                "pricescale",
                "minmov",
                "fractional",
                "minmove2",
                "AO",
                "CCI20",
                "Stoch.K",
                "Stoch.D",
                "profit_addresses_percentage",
                "sentiment",
                "socialdominance",
                "galaxyscore",
                "social_volume_24h",
                "altrank",
                "large_tx_count",
                "close",
                "currency",
                "change_abs",
                "Volatility.D",
            ],
            "ignore_unknown_fields": False,
            "options": {
                "lang": "en"
            },
            "range":[
                offset,
                offset + limit,
            ],
            "sort": {
                "sortBy": "crypto_total_rank",
                "sortOrder": "asc"
            },
            "symbols": {},
            "markets": ["coin"]
        }

        if coin_filter:
            data["filter"] = [
                {
                    "left": "base_currency,base_currency_desc",
                    "operation": "match",
                    "right": f"{coin_filter}"
                }
            ]
        data = json.dumps(data)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://scanner.tradingview.com/coin/scan',
                params=params,
                cookies=cookies,
                headers=headers,
                data=data,
            )

        j_result = response.json()
        if not isinstance(j_result, dict) or not j_result.get("data", None):
            raise Exception("No data found")

        j_data = j_result["data"]
        all_infos = []
        for current_data in j_data:
            if not isinstance(current_data, dict):
                continue
            all_infos.append(CoinScanInfo._parse(current_data.get("d", [])))

        return all_infos
