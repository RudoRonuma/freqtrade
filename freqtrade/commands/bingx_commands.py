import asyncio
import logging
from typing import Any


logger = logging.getLogger(__name__)

async def run_bingx_ultra_tests(args: dict[str, Any]) -> None:
    """
    Run BingX tests
    """

    print(args)


def start_test_bingx_ultra(args: dict[str, Any]) -> None:
    """
    Test BingX configuration
    """
    asyncio.run(run_bingx_ultra_tests(args=args))
    print("done")
