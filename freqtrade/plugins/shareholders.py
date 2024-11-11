"""
Shareholders plugin for freqtrade bot.
This plugin calculates shareholders statistics.
"""

from datetime import datetime


class ShareholderInfo:
    # Name of the shareholder
    name: str = ""

    # Balance of the shareholder
    balance: float = 0.0

    # Percentage of the shareholder of the total assets.
    # Between 0 and 1
    percentage: float = 0.0


    def __init__(self, name: str, balance: float = 0.0, percentage: float = 0.0) -> None:
        self.name = name
        self.balance = balance
        self.percentage = percentage


class ShareholdersManager:
    # total available assets
    total_assets: float = 0

    shareholders: list[ShareholderInfo] = []

    last_updated_at: datetime = datetime.now()

    _header_comment: str = ""

    # Distributes the profit to the shareholders based on their percentage.
    def add_total_profit(self, amount: float) -> None:
        for shareholder in self.shareholders:
            shareholder.balance += shareholder.percentage * amount

        self.total_assets += amount

    # Allows the shareholder to withdraw their balance, updating their balance
    # and shareholding percentage.
    def withdraw_balance(self, shareholder_name: str, amount: float) -> None:
        target_shareholder: ShareholderInfo = None
        for shareholder in self.shareholders:
            if shareholder.name != shareholder_name:
                continue

            target_shareholder = shareholder
            break

        if not target_shareholder:
            raise Exception(f"Shareholder {shareholder_name} not found.")

        target_shareholder.balance -= amount
        self.total_assets -= amount
        self._update_shareholders_percentage()

    def deposit_balance(self, shareholder_name: str, amount: float) -> None:
        target_shareholder: ShareholderInfo = None
        for shareholder in self.shareholders:
            if shareholder.name != shareholder_name:
                continue

            target_shareholder = shareholder
            break

        if not target_shareholder:
            raise Exception(f"Shareholder {shareholder_name} not found.")

        target_shareholder.balance += amount
        self.total_assets += amount
        self._update_shareholders_percentage()

    # Goes through the shareholders and updates their percentages based on their
    # current balance and the total assets.
    def _update_shareholders_percentage(self) -> None:
        for shareholder in self.shareholders:
            shareholder.percentage = shareholder.balance / self.total_assets

    @staticmethod
    def parse_shareholders(text: str) -> 'ShareholdersManager':
        lines = text.split("\n")

        manager = ShareholdersManager()
        manager._header_comment = lines[0]
        loaded_shareholders = {}

        is_in_share_percentages = False
        is_in_shareholders_balance = False

        for line in lines[1:]:
            if not line or line.startswith("#"):
                continue

            if line.startswith("---"):
                # end of section
                is_in_share_percentages = False
                is_in_shareholders_balance = False
                continue

            if line.lower().startswith("total assets"):
                manager.total_assets = float(line.split(":")[1])
                continue

            if line.lower().startswith("share percentages"):
                is_in_share_percentages = True
                is_in_shareholders_balance = False
                continue

            if is_in_share_percentages:
                share_holder_strs = line.split(":")
                current_shareholder = ShareholderInfo(
                    name=share_holder_strs[0].strip(),
                    balance=0.0, # will be calculated later
                    percentage=float(share_holder_strs[1].strip())
                )
                loaded_shareholders[current_shareholder.name] = current_shareholder
                manager.shareholders.append(current_shareholder)

            if line.lower().startswith("shareholders' balance"):
                is_in_share_percentages = False
                is_in_shareholders_balance = True
                continue

            if is_in_shareholders_balance:
                share_holder_strs = line.split(":")
                the_name = share_holder_strs[0].strip()
                current_shareholder = loaded_shareholders[the_name]
                if not isinstance(current_shareholder, ShareholderInfo):
                    raise Exception(f"Shareholder {the_name} not found.")

                current_shareholder.balance = float(
                    share_holder_strs[1].strip().replace("$", "").replace(",", ""))

            if line.lower().startswith("last updated at"):
                manager.last_updated_at = datetime.strptime(
                    line.split(":")[1].strip(), "%Y-%m-%d %H:%M:%S")

        return manager

    def __str__(self) -> str:
        result = self._header_comment + "\n"
        result += f"Total assets: ${self.total_assets}\n"
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
        result = f"*{self._header_comment}*\n"
        result += f"*Total assets*: ${self.total_assets}\n\n"
        result += "*Share percentages*:\n"
        for shareholder in self.shareholders:
            result += f"*{shareholder.name}*: {shareholder.percentage}\n"
        result += "------------------------------------\n"
        result += "*Shareholders' balance*:\n"
        for shareholder in self.shareholders:
            result += f"*{shareholder.name}*: ${shareholder.balance}\n"
        result += "------------------------------------\n"
        result += f"*Last updated at*: `{self.last_updated_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
        return result
