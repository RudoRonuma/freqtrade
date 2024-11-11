"""
Shareholders plugin for freqtrade bot.
This plugin calculates shareholders statistics.
"""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from freqtrade.constants import Config
from freqtrade.util import normalize_money, str_to_decimal


DEFAULT_SHAREHOLDERS_FILE = "shareholders.json"


class ShareholderInfo:
    # Name of the shareholder
    name: str = ""

    # Balance of the shareholder
    balance: Decimal = Decimal("0.0")

    # Percentage of the shareholder of the total assets.
    # Between 0 and 1
    percentage: Decimal = Decimal("0.0")

    def __init__(self, name: str, balance: Decimal = None, percentage: Decimal = None) -> None:
        self.name = name
        self.balance = balance or Decimal("0.0")
        self.percentage = percentage or Decimal("0.0")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "balance": str(self.balance),
            "percentage": str(self.percentage),
        }

    @staticmethod
    def from_dict(data: dict) -> "ShareholderInfo":
        return ShareholderInfo(
            name=data.get("name", ""),
            balance=Decimal(data.get("balance", "0.0")),
            percentage=Decimal(data.get("percentage", "0.0")),
        )


class ShareholdersManager:
    # total available assets for shareholders.
    total_assets: Decimal = Decimal("0.0")

    total_platform_assets: Decimal = Decimal("0.0")

    reserves: Decimal = Decimal("0.0")

    shareholders: list[ShareholderInfo] = []

    last_updated_at: datetime = datetime.now()

    _header_comment: str = ""

    _config: Config = None

    _is_loaded: bool = False

    _reserve_percentage: Decimal = Decimal("0.05")

    def __init__(self, config: Config = None) -> None:
        self._config = config or Config()

        self._reserve_percentage = Decimal(self._config.get("reserve_percentage", "0.05"))

    def get_share_holder_by_name(self, name: str) -> ShareholderInfo:
        for shareholder in self.shareholders:
            if shareholder.name == name:
                return shareholder

        return None

    # Distributes the profit to the shareholders based on their percentage.
    def add_total_profit(self, amount: Decimal) -> None:
        self.total_platform_assets += amount
        reserve_amount = amount * self._reserve_percentage
        self.reserves += reserve_amount
        amount -= reserve_amount

        for shareholder in self.shareholders:
            shareholder.balance += shareholder.percentage * amount

        self.total_assets += amount
        self.save_to_file()

    # Allows the shareholder to withdraw their balance, updating their balance
    # and shareholding percentage.
    def withdraw_balance(self, shareholder_name: str, amount: Decimal) -> None:
        target_shareholder = self.get_share_holder_by_name(shareholder_name)
        if not target_shareholder:
            raise Exception(f"Shareholder {shareholder_name} not found.")

        target_shareholder.balance -= amount
        self.total_assets -= amount
        self.total_platform_assets -= amount
        self._update_shareholders_percentage()
        self.save_to_file()

    # Allows the shareholder to deposit money into their balance, updating their balance
    # and shareholding percentage.
    def deposit_balance(self, shareholder_name: str, amount: Decimal) -> None:
        target_shareholder = self.get_share_holder_by_name(shareholder_name)
        if not target_shareholder:
            raise Exception(f"Shareholder {shareholder_name} not found.")

        target_shareholder.balance += amount
        self.total_assets += amount
        self.total_platform_assets += amount
        self._update_shareholders_percentage()
        self.save_to_file()

    # Goes through the shareholders and updates their percentages based on their
    # current balance and the total assets.
    def _update_shareholders_percentage(self) -> None:
        for shareholder in self.shareholders:
            shareholder.percentage = shareholder.balance / self.total_assets

    def parse_shareholders(self, text: str) -> "ShareholdersManager":
        lines = text.split("\n")

        self.shareholders = []
        self.total_assets = Decimal("0.0")
        self.total_platform_assets = Decimal("0.0")
        self._header_comment = lines[0]
        loaded_shareholders = {}

        is_in_share_percentages = False
        is_in_shareholders_balance = False

        for line in lines[1:]:
            if not line or line.startswith("#"):
                continue

            normalized_line = line.strip().lower()

            if line.startswith("---"):
                # end of section
                is_in_share_percentages = False
                is_in_shareholders_balance = False
                continue

            if normalized_line.startswith("total assets"):
                self.total_assets = str_to_decimal(line.split(":")[1])
                continue

            if normalized_line.startswith("total platform assets"):
                self.total_platform_assets = str_to_decimal(line.split(":")[1])
                continue

            if normalized_line.startswith("share percentages"):
                is_in_share_percentages = True
                is_in_shareholders_balance = False
                continue

            if is_in_share_percentages:
                share_holder_strs = line.split(":")
                current_shareholder = ShareholderInfo(
                    name=share_holder_strs[0].strip(),
                    balance=Decimal("0.0"),  # will be calculated later
                    percentage=Decimal(share_holder_strs[1].strip()),
                )
                loaded_shareholders[current_shareholder.name] = current_shareholder
                self.shareholders.append(current_shareholder)

            if normalized_line.startswith("shareholders' balance"):
                is_in_share_percentages = False
                is_in_shareholders_balance = True
                continue

            if is_in_shareholders_balance:
                share_holder_strs = line.split(":")
                the_name = share_holder_strs[0].strip()
                current_shareholder = loaded_shareholders[the_name]
                if not isinstance(current_shareholder, ShareholderInfo):
                    raise Exception(f"Shareholder {the_name} not found.")

                current_shareholder.balance = Decimal(
                    share_holder_strs[1].strip().replace("$", "").replace(",", "")
                )

            if normalized_line.startswith("last updated at"):
                time_value = normalized_line.removeprefix("last updated at:").strip()
                self.last_updated_at = datetime.strptime(time_value, "%Y-%m-%d %H:%M:%S")

        self._is_loaded = True
        return self

    def __str__(self) -> str:
        result = self._header_comment + "\n"
        result += f"Total assets: ${self.total_assets}\n"
        result += f"Total platform assets: ${self.total_platform_assets}\n\n"
        result += "Share percentages:\n"
        for shareholder in self.shareholders:
            result += f"{shareholder.name}: {shareholder.percentage}\n"
        result += "---\n"
        result += "Shareholders' balance:\n"
        for shareholder in self.shareholders:
            result += f"{shareholder.name}: ${shareholder.balance}\n"
        result += "---\n"
        result += f"Last updated at: {self.last_updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        return result

    def to_markdown_str(self) -> str:
        result = "*Shareholders statistics:* (will get updated after each trade)\n\n"
        result += f"*Total assets*: {normalize_money(self.total_assets, decimal_points_limit=2)}\n"
        result += "*Total platform assets*: " + \
            f"{normalize_money(self.total_platform_assets, decimal_points_limit=2)}\n"
        result += f"*Reserves*: {normalize_money(self.reserves, decimal_points_limit=2)}\n\n"
        result += "------------------------------------\n\n"
        result += "*Share percentages*:\n"
        for shareholder in self.shareholders:
            result += f"*{shareholder.name}*: {shareholder.percentage.quantize(Decimal('0.01'))}\n"
        result += "------------------------------------\n\n"
        result += "*Shareholders' balance*:\n"
        for shareholder in self.shareholders:
            result += f"*{shareholder.name}*: " + \
                f"{normalize_money(shareholder.balance, decimal_points_limit=2)}\n"
        result += "------------------------------------\n\n"
        result += f"*Last updated at*: `{self.last_updated_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
        return result

    def to_dict(self) -> dict:
        return {
            "total_assets": str(self.total_assets),
            "total_platform_assets": str(self.total_platform_assets),
            "reserves": str(self.reserves),
            "shareholders": [shareholder.to_dict() for shareholder in self.shareholders],
            "last_updated_at": self.last_updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def from_dict(data: dict, config: Config = None) -> "ShareholdersManager":
        if not data:
            raise Exception("Data is empty.")

        manager = ShareholdersManager(config=config)
        manager.total_assets = Decimal(data.get("total_assets", "0.0"))
        manager.total_platform_assets = Decimal(data.get("total_platform_assets", "0.0"))
        manager.shareholders = [
            ShareholderInfo.from_dict(shareholder_data)
            for shareholder_data in data.get("shareholders", [])
        ]
        manager.last_updated_at = datetime.strptime(
            data.get("last_updated_at", ""), "%Y-%m-%d %H:%M:%S"
        )

        manager._is_loaded = True
        return manager

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def save_to_file(self, file_path: str = None) -> None:
        file_path = file_path or self._config["shareholders"].get(
            "file_path", DEFAULT_SHAREHOLDERS_FILE
        )

        self.last_updated_at = datetime.now()
        with Path(file_path).open("w") as file:
            file.write(self.to_json())

    @staticmethod
    def from_json_file(file_path: str, config: Config = None) -> "ShareholdersManager":
        with Path(file_path).open("r") as file:
            return ShareholdersManager.from_dict(json.load(file), config)
