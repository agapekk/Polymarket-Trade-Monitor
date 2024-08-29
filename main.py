import requests
import time
from datetime import datetime

# API Endpoint
BASE_URL = "https://data-api.polymarket.com/trades"
PROFIT_API_BASE_URL = "https://polymarket.com/api/profile/profit"

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "yourwebhookhere"

# Win rate threshold for a good wallet
PROFIT_THRESHOLD = 70  # You can change this value to the desired percentage

# Minimum number of tokens traded to evaluate wallet
MIN_TOKENS_TRADED = 3  # You can change this value to the desired minimum number of tokens

# Minimum profit to evaluate wallet
MIN_PROFIT = 1000.00  # You can change this value to the desired minimum profit


banner = '''

░       ░░░░      ░░░  ░░░░░░░░  ░░░░  ░░        ░░       ░░░░      ░░░░      ░░░  ░░░░  ░░        ░░       ░░
▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒▒  ▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒  ▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒
▓       ▓▓▓  ▓▓▓▓  ▓▓  ▓▓▓▓▓▓▓▓▓▓    ▓▓▓▓▓▓▓  ▓▓▓▓▓       ▓▓▓  ▓▓▓▓  ▓▓  ▓▓▓▓▓▓▓▓     ▓▓▓▓▓      ▓▓▓▓       ▓▓
█  ████████  ████  ██  ███████████  ████████  █████  ███  ███        ██  ████  ██  ███  ███  ████████  ███  ██
█  █████████      ███        █████  ████████  █████  ████  ██  ████  ███      ███  ████  ██        ██  ████  █
                                                                                                                                                 
'''
print(banner)
# Function to fetch new trades
def fetch_new_trades(limit=50, offset=0, takerOnly=True, filterType="CASH", filterAmount=1):
    url = f"{BASE_URL}?takerOnly={takerOnly}&limit={limit}&offset={offset}&filterType={filterType}&filterAmount={filterAmount}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Function to fetch positions
def fetch_positions(user):
    url = f"https://polymarket.com/api/profile/positions?user={user}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Function to fetch profit
def fetch_profit(user):
    url = f"{PROFIT_API_BASE_URL}?range=all&address={user}"
    response = requests.get(url)
    response.raise_for_status()
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to decode JSON for user {user}. Response: {response.text}")
        return None

# Function to evaluate the user's positions
def evaluate_positions(positions, threshold, min_tokens):
    total_positions = len(positions)
    profitable_positions = 0
    unprofitable_positions = 0
    total_trades = sum(position['totalBought'] for position in positions)

    if total_trades < min_tokens:
        return None, profitable_positions, unprofitable_positions, total_trades, total_positions

    for position in positions:
        if position['percentPnl'] > 0:
            profitable_positions += 1
        else:
            unprofitable_positions += 1

    if total_positions == 0:
        return False, 0, 0, total_trades, total_positions

    profit_ratio = profitable_positions / total_positions
    is_good_wallet = profit_ratio >= (threshold / 100)

    return is_good_wallet, profitable_positions, unprofitable_positions, total_trades, total_positions

# Function to format numbers with commas
def format_number_with_commas(number):
    return f"{number:,.2f}"

# Function to print evaluation result
def print_evaluation_result(user, threshold, min_tokens, min_profit, trade_details):
    positions = fetch_positions(user)
    profit_data = fetch_profit(user)
    
    if profit_data is None:
        print(f"Skipping evaluation for wallet {user} due to failed profit data fetch.")
        return
    
    total_profit = profit_data['amount']
    is_good_wallet, profitable_positions, unprofitable_positions, total_trades, total_positions = evaluate_positions(positions, threshold, min_tokens)

    if total_trades < min_tokens or total_profit < min_profit:
        print(f"The wallet {user} does not meet the required amount of {min_tokens} tokens traded or {min_profit} profit.")
        return

    print(f"Profitable trades: {profitable_positions}")
    print(f"Unprofitable trades: {unprofitable_positions}")

    if is_good_wallet is None:
        print(f"The wallet {user} does not meet the required amount of {min_tokens} tokens traded.")
    elif is_good_wallet:
        send_discord_notification(user, trade_details, (profitable_positions / total_positions) * 100, profitable_positions, unprofitable_positions, total_profit)
        print(f"The wallet {user} is a good wallet based on a {threshold}% threshold.")
    else:
        print(f"The wallet {user} is not a good wallet based on a {threshold}% threshold.")

def send_discord_notification(user, trade_details, win_rate, profitable_positions, unprofitable_positions, total_profit):
    price = trade_details.get('price', 0)
    total_worth = price * trade_details['size']
    embed = {
        "content": None,
        "embeds": [
            {
                "color": 20991,
                "fields": [
                    {
                        "name": "Event",
                        "value": trade_details['title'],
                        "inline": True
                    },
                    {
                        "name": "Bought",
                        "value": f"{trade_details['size']} SHARES @ ${price:.2f} each",
                        "inline": True
                    },
                    {
                        "name": "Total Worth",
                        "value": f"${format_number_with_commas(total_worth)}",
                        "inline": True
                    },
                    {
                        "name": "Wallet Details",
                        "value": f"Winrate: {win_rate:.2f}%\nProfitable trades: {profitable_positions}\nUnprofitable trades: {unprofitable_positions}\nTotal Profit: ${format_number_with_commas(total_profit)}"
                    }
                ],
                "author": {
                    "name": f"New Polymarket trade ({user})",
                    "url": f"https://polymarket.com/profile/{user}",
                    "icon_url": "https://images.crunchbase.com/image/upload/c_pad,f_auto,q_auto:eco,dpr_1/radxv99bd8jwiuqwxt95"
                }
            }
        ],
        "attachments": []
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=embed)
    response.raise_for_status()
    print(f"Notification sent for wallet: {user}")

# Function to monitor trades and evaluate wallet
def monitor_trades():
    seen_trades = set()
    while True:
        trades = fetch_new_trades()
        new_trades = [trade for trade in trades if trade['transactionHash'] not in seen_trades and trade['side'].lower() == 'buy']

        for trade in new_trades:
            user = trade['proxyWallet']
            print(f"New trade detected for wallet: {user}")
            print(f"Trade Details: {trade['side']} {trade['size']} of {trade['title']} @ {trade['price']} each (Transaction Hash: {trade['transactionHash']})")
            print_evaluation_result(user, PROFIT_THRESHOLD, MIN_TOKENS_TRADED, MIN_PROFIT, trade)
            seen_trades.add(trade['transactionHash'])

# Start monitoring
if __name__ == "__main__":
    monitor_trades()
