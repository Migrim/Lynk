import requests
from datetime import datetime, timedelta

def get_crypto_prices():
    api_url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana",
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        crypto_prices = {
            "current_btc_price": data.get("bitcoin", {}).get("usd", 0),
            "current_eth_price": data.get("ethereum", {}).get("usd", 0),
            "current_sol_price": data.get("solana", {}).get("usd", 0)
        }
        return crypto_prices
    except requests.RequestException as e:
        print(f"Error fetching cryptocurrency prices: {e}")
        return {
            "current_btc_price": 0,
            "current_eth_price": 0,
            "current_sol_price": 0
        }

def get_historical_data(coin_id):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    api_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": 7,
        "interval": "daily"
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        prices = data.get("prices", [])
        historical_prices = [{"timestamp": price[0], "price": price[1]} for price in prices]
        return historical_prices
    except requests.RequestException as e:
        print(f"Error fetching historical data for {coin_id}: {e}")
        return []