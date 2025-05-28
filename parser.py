import requests 
import json
import time
import config

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
    
def read_spread_file():
    try:
        with open(config.spread_threshold_config_file, "r") as f:
            min_spread_data = json.load(f)
            return min_spread_data["spread_threshold"]
    except Exception:
        return 3
    

def filter_opportunities():
    min_spread_threshold = read_spread_file()
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

    with open(config.arbitrage_opportunities_file, "w", encoding="utf-8") as file_2:
        json.dump(filtered_opps, file_2, indent=4)

    return filtered_opps



