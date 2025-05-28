import requests 
import json
from dotenv import load_dotenv
from os import getenv
import time

load_dotenv()
TG_TOKEN = getenv("TG_access_token")
TG_CHAT_ID = getenv("chat_id")

last_sent_message = None

def fetch_arb_opportunities():
    url = "https://uainvest.com.ua/api/arbitrage/offers?"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
    payload = {
        "type": "spread",
        "exchanges": "mexc_gate"
        }
    
    try:
        response = requests.get(url=url, headers=headers, params=payload)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Виникла помилка о {time.strftime('%b %d %H:%M:%S')}:\n{e}")
        data = {"data": []}

    # with open("data.json", "w", encoding="utf-8") as file:
    #     json.dump(data, file, indent=4)

    return data
    

def filter_opportunities(min_spread_threshold):
    data = fetch_arb_opportunities()

    filtered_opps = []

    for opportunity in data["data"]:
        try:
            spread = opportunity.get("open_spread_percentage")
            if spread >= min_spread_threshold:
                filtered_opps.append({
                    "ticker": opportunity["symbol"],
                    "long": opportunity["long"],
                    "short": opportunity["short"],
                    "spread": opportunity["open_spread_percentage"],
                    f"{opportunity["long_item"]["exchange"]}_volume": opportunity["long_item"]["24usdt"],
                    f"{opportunity["short_item"]["exchange"]}_volume": opportunity["short_item"]["24usdt"]       
                })
        except KeyError:
            continue

    # with open("filtered_data.json", "w", encoding="utf-8") as file_2:
    #     json.dump(filtered_opps, file_2, indent=4)

    if filtered_opps != []:
        send_telegram_message(filtered_opps)


def compile_message(opp):
    message = (
        f"<code>{opp['ticker']}</code>\n"
        f"Long: <i>{opp['long']}</i>\n"
        f"Short: <i>{opp['short']}</i>\n"
        f"Spread: <b>{opp['spread']:.2f}%</b>\n"
        f"Об'єм на {opp['long']}: <code>{opp[f'{opp['long']}_volume'] / 1000000:.2f}m$</code>\n"
        f"Об'єм на {opp['short']}: <code>{opp[f'{opp['short']}_volume'] / 1000000:.2f}m$</code>"
        )
    return message


def send_telegram_message(opps):
    global last_sent_message

    for opp in opps:
        message = compile_message(opp)

        if message == last_sent_message:
            continue

        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {
            "chat_id": TG_CHAT_ID,
            "text": message,
            "parse_mode": "HTML" 
        }
        
        response = requests.post(url, json=payload)

        if response.ok:
            last_sent_message = message


def main(spread=1):
    try:
        while True:
            filter_opportunities(min_spread_threshold=spread)
            time.sleep(15)
    except KeyboardInterrupt:
        print("Exit")

main(3)