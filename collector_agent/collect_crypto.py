import requests

# building my api url and fetching + processing the data i retrieve 
def fetch_crypto_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    data = response.json()
    # check if market_data is present in the response
    if "market_data" not in data:
        print("market_data key missing in response")
        return {
            "price_usd": None,
            "market_cap_usd": None,
            "volume_24h_usd": None,
            "price_change_percentage_24h": None
        }
    return {
        "price_usd": data["market_data"]["current_price"].get("usd", None),
        "market_cap_usd": data["market_data"]["market_cap"].get("usd", None),
        "volume_24h_usd": data["market_data"]["total_volume"].get("usd", None),
        "price_change_percentage_24h": data["market_data"].get("price_change_percentage_24h", None)
    }

# fetches metrics for coin_id = "bitcoin" and "ethereum"
def fetch_bitcoin_and_ethereum():
    bitcoin_data = fetch_crypto_data("bitcoin")
    ethereum_data = fetch_crypto_data("ethereum")
    
    return {
        "bitcoin": bitcoin_data,
        "ethereum": ethereum_data,
    }