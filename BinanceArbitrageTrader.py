'''
Binanace triangular arbitrage trader
Based on some scripts
'''

from binance.client import Client
from BinanceKeys import projectBinanceKey
from datetime import datetime
import time
from collections import defaultdict

'''
Main function
'''
def run():
    # Set Binance time - TODO

    # Define client
    api_key = projectBinanceKey['api_key']
    api_secret = projectBinanceKey['api_secret']
    client = Client(api_key, api_secret)

    # Initialize Arbitrage Binance Bot
    initializeArb(client)

    # Perform Arbitrage Function

    # Data Output (log) in a text file - keep track of start/end time, trades, balance

    # Plot some outputs

    pass


'''
Initialize the arbitrage: build coins data structure, 
'''
def initializeArb(client):

    welcome_message = "Welcome to the Binance Arbitrage Crypto Trader Bot Python Script!\n"
    bot_start_time = str(datetime.now())
    welcome_message += "Bot Start Time: {}\n\n".format(bot_start_time)
    print(welcome_message)
    write_to_log_file(welcome_message)
    time.sleep(1)

    # Define coins to start with
    primary = "BTC" # we can put all coins here. now we start from BTC only - TODO

    # Get dictionary of all optional prices
    prices = get_prices(primary)

    # Get all tickers
    market_tickers = client.get_all_tickers()
    print(market_tickers)
    tickers = []
    for ticker in market_tickers:
        tickers.append(ticker["symbol"])

    return prices, tickers


'''
Get the prices of each two optional coins
'''
def get_prices(primary):
    client = Client(None, None)
    prices = client.get_orderbook_tickers()
    prepared = defaultdict(dict)
    for ticker in prices:
        pair = ticker['symbol']
        ask = float(ticker['askPrice'])
        bid = float(ticker['bidPrice'])
        if ask == 0.0:
            continue
        #for primary in primary_list: - TODO
        if pair.endswith(primary):
            secondary = pair[:-len(primary)]
            prepared[primary][secondary] = 1/ask
            prepared[secondary][primary] = bid
    return prepared


'''
Write message to log file
'''
def write_to_log_file(message):
    with open('CryptoTriArbBot_DataLog.txt', 'a+') as f:
        f.write(message)


if __name__ == "__main__":
    run()