import asyncio
import logging
from typing import Any

import rapidjson

from freqtrade.enums import RunMode
from freqtrade.exchange.bingx_ultra import BingXUltraBaseAPI


logger = logging.getLogger(__name__)

async def run_bingx_ultra_tests(args: dict[str, Any]) -> None:
    """
    Run BingX tests
    """
    my_base_api = BingXUltraBaseAPI()
    result = await my_base_api.get_hot_search()
    print(result)
    print(args)


def start_test_bingx_ultra(args: dict[str, Any]) -> None:
    """
    Test BingX configuration
    """
    asyncio.run(run_bingx_ultra_tests(args=args))
    print("done")
