import json
from dataclasses import dataclass
from typing import Any, List


@dataclass
class Data:
    result: List['HostSearchResult']
    hintAbTest: bool
    pageId: int
    total: int

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        _result = [HostSearchResult.from_dict(y) for y in obj.get("result")]
        _hintAbTest = bool(obj.get("hintAbTest"))
        _pageId = int(obj.get("pageId"))
        _total = int(obj.get("total"))
        return Data(_result, _hintAbTest, _pageId, _total)

@dataclass
class HostSearchResult:
    symbol: str
    coinName: str
    valCoinName: str
    weight: int

    @staticmethod
    def from_dict(obj: Any) -> 'HostSearchResult':
        _symbol = str(obj.get("symbol"))
        _coinName = str(obj.get("coinName"))
        _valCoinName = str(obj.get("valCoinName"))
        _weight = int(obj.get("weight"))
        return HostSearchResult(_symbol, _coinName, _valCoinName, _weight)

@dataclass
class HotSearchRoot:
    code: int
    timestamp: float
    data: Data

    @staticmethod
    def from_dict(obj: Any) -> 'HotSearchRoot':
        _code = int(obj.get("code"))
        _timestamp = float(obj.get("timestamp"))
        _data = Data.from_dict(obj.get("data"))
        return HotSearchRoot(_code, _timestamp, _data)

