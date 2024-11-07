"""BingxUltra exchange subclass"""

import logging

import httpx

from freqtrade.exchange import Exchange
from freqtrade.exchange.exchange_types import FtHas


logger = logging.getLogger(__name__)


class BingxUltra(Exchange):
    """
    BingxUltra exchange class. Contains adjustments needed for Freqtrade to work
    with this exchange.
    """


class BingXUltraBaseAPI:
    we_api_base_host: str = 'api-app.we-api.com'
    we_api_base_url: str = 'https://api-app.we-api.com/api'

    def __init__(self):
        pass

    async def get_hot_search(self):
        async with httpx.AsyncClient(verify=False) as client:
            headers = {
                'Host': self.we_api_base_host,
                'Content-Type': 'application/json',
                'Mainappid': '10009',
                'Accept': 'application/json',
                'Traceid': '9a0c85ccd3894e59abfa484f87133ed9',
                'App_version': '4.28.3',
                'Platformid': '10',
                'Install-Channel': 'officialAPK',
                'Device_id': '3f29262226184e9e8a2cb6337900d281##',
                'Os_version': '7.1.2',
                'Device_brand': 'SM-N976N',
                'Channel': 'officialAPK',
                'Appid': '30004',
                'Trade_env': 'real',
                'Timezone': '3',
                'Lang': 'en',
                'Syslang': 'en',
                'Only_one_position': '0',
                'Sign': '62CB93EB3BAB11810C6D8B38B9310A991195E40DEC41C881FFA201D2DE584ECA',
                'Timestamp': '1730951169453',
                # 'Accept-Encoding': 'gzip, deflate',
                'User-Agent': 'okhttp/4.12.0',
                'Connection': 'close',
            }
            params = {
                'bizType': '30',
            }
            response = await client.get(
                f'{self.we_api_base_url}/coin/v1/quotation/hot-search',
                headers=headers,
                params=params,
            )
        return response.json()



