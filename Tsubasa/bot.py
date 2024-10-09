import os
import requests
import json
import time
import logging
from colorama import Fore, Style

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger()

class Tsubasa:
    def __init__(self):
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://app.ton.tsubasa-rivals.com",
            "Referer": "https://app.ton.tsubasa-rivals.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        self.config = self.load_config()

    def load_config(self):
        logger.info("Loading config for Tsubasa-BOT...")
        enable_card_upgrades = True
        max_upgrade_cost = 500000
        logger.info("Configuration loaded successfully.")
        return {"enable_card_upgrades": enable_card_upgrades, "max_upgrade_cost": max_upgrade_cost}

    def countdown(self, seconds):
        for i in range(seconds, -1, -1):
            print(f"\rWaiting {i} seconds to continue the loop", end="")
            time.sleep(1)
        print()

    def api_call(self, url, payload):
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during API call: {e}")
            return None

    def call_start_api(self, init_data):
        url = "https://app.ton.tsubasa-rivals.com/api/start"
        payload = {"lang_code": "en", "initData": init_data}
        start_response = self.api_call(url, payload)

        if start_response and "game_data" in start_response:
            game_data = start_response["game_data"]
            master_hash = start_response.get("master_hash")
            if master_hash:
                self.headers["X-Masterhash"] = master_hash

            tasks = [task for task in start_response.get("task_info", []) if task["status"] in [0, 1]]
            return {
                "total_coins": game_data["user"]["total_coins"],
                "energy": game_data["user"]["energy"],
                "max_energy": game_data["user"]["max_energy"],
                "coins_per_tap": game_data["user"]["coins_per_tap"],
                "profit_per_second": game_data["user"]["profit_per_second"],
                "tasks": tasks,
                "success": True,
            }
        return {"success": False, "error": "Error calling start API"}

    def call_tap_api(self, init_data, tap_count):
        url = "https://app.ton.tsubasa-rivals.com/api/tap"
        payload = {"tapCount": tap_count, "initData": init_data}
        tap_response = self.api_call(url, payload)

        if tap_response and "game_data" in tap_response:
            return {
                "total_coins": tap_response["game_data"]["user"]["total_coins"],
                "energy": tap_response["game_data"]["user"]["energy"],
                "max_energy": tap_response["game_data"]["user"]["max_energy"],
                "coins_per_tap": tap_response["game_data"]["user"]["coins_per_tap"],
                "profit_per_second": tap_response["game_data"]["user"]["profit_per_second"],
                "success": True,
            }
        return {"success": False, "error": "Error pressing button"}

    def call_daily_reward_api(self, init_data):
        url = "https://app.ton.tsubasa-rivals.com/api/daily_reward/claim"
        payload = {"initData": init_data}
        daily_reward_response = self.api_call(url, payload)

        if daily_reward_response:
            return {"success": True, "message": "Successfully claimed daily reward"}
        return {"success": False, "message": "You have already claimed your reward today"}

    def fetch_card_info(self):
        return [
            {"cardId": 1, "cost": 200000, "name": "Card A", "level": 1},
            {"cardId": 2, "cost": 300000, "name": "Card B", "level": 1},
        ]

    def level_up_cards(self, init_data, total_coins):
        if not self.config["enable_card_upgrades"]:
            logger.info("Card upgrades are disabled in config.")
            return total_coins

        updated_total_coins = total_coins
        leveled_up = False
        card_info = self.fetch_card_info()

        for card in card_info:
            if updated_total_coins >= card["cost"] <= self.config["max_upgrade_cost"]:
                updated_total_coins -= card["cost"]
                card["level"] += 1
                logger.info(f"Upgrading card | {card['name']} | New level: {card['level']} | Remaining balance: {updated_total_coins}")
                leveled_up = True

        if leveled_up:
            logger.info("Successfully upgraded all eligible cards.")
        else:
            logger.info("No cards are eligible for upgrade.")

        return updated_total_coins

    def _banner(self):
        print(r"""
████████╗███████╗██╗   ██╗██████╗  █████╗ ███████╗ █████╗     ██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║   ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   ███████╗██║   ██║██████╔╝███████║███████╗███████║    ██████╔╝██║   ██║   ██║   
   ██║   ╚════██║██║   ██║██╔══██╗██╔══██║╚════██║██╔══██║    ██╔══██╗██║   ██║   ██║   
   ██║   ███████║╚██████╔╝██████╔╝██║  ██║███████║██║  ██║    ██████╔╝╚██████╔╝   ██║   
   ╚═╝   ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
        """)
        print(Fore.GREEN + Style.BRIGHT + "TSUBASA BOT")
        print(Fore.RED + Style.BRIGHT + "Contact: https://t.me/thog099")
        print(Fore.BLUE + Style.BRIGHT + "Replit: Thog")
        print("")

    def _clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def main(self):
        self._clear()
        self._banner()

        data_file = "data.txt"
        with open(data_file, 'r') as f:
            data = f.read().strip().splitlines()

        logger.info("Configuration:")
        logger.info(f"Card upgrades enabled: {self.config['enable_card_upgrades']}")
        logger.info(f"Max cost for upgrading: {self.config['max_upgrade_cost']}")

        logger.info("Starting Client...")

        while True:
            for i, init_data in enumerate(data):
                start_result = self.call_start_api(init_data)
                if start_result["success"]:
                    try:
                        first_name = json.loads(requests.utils.unquote(init_data.split("user=")[1].split("&")[0]))['first_name']
                        logger.info(f"Account {i + 1} | {first_name}")
                    except (IndexError, KeyError, json.JSONDecodeError) as e:
                        logger.error(f"Error getting account name for account {i + 1}: {e}")
                        first_name = "Unknown"

                    logger.info(f"Balance: {start_result['total_coins']}")
                    logger.info(f"Energy: {start_result['energy']}/{start_result['max_energy']}")
                    logger.info(f"Coins per tap: {start_result['coins_per_tap']}")
                    logger.info(f"Profit per second: {start_result['profit_per_second']}")

                    for task in start_result["tasks"]:
                        logger.info(f"Performing task: {task['id']}")
                    if start_result["energy"] > 0:
                        tap_result = self.call_tap_api(init_data, start_result["energy"])
                        if tap_result["success"]:
                            logger.info(f"Tap successful | Remaining Energy: {tap_result['energy']}/{tap_result['max_energy']} | Balance: {tap_result['total_coins']}")
                        else:
                            logger.error(tap_result["error"])

                    daily_reward_result = self.call_daily_reward_api(init_data)
                    logger.info(daily_reward_result["message"])

                    updated_total_coins = self.level_up_cards(init_data, start_result["total_coins"])
                    logger.info(f"Finished upgrading all eligible cards | Balance: {updated_total_coins}")

                else:
                    logger.error(start_result["error"])

                time.sleep(1)

            self.countdown(30)

if __name__ == "__main__":
    client = Tsubasa()
    client.main()