'''
Binanace triangular arbitrage trader
Based on some scripts
'''


from binance.client import Client
from BinanceKeys import projectBinanceKey
from datetime import datetime
import time
from collections import defaultdict
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import logging, traceback



'''
Main function
'''


def run():
    # Set Binance time - TODO

    # Define client
    api_key = projectBinanceKey['api_key']
    api_secret = projectBinanceKey['api_secret']
    try:
        client = Client(api_key, api_secret)

        # Initialize Arbitrage Binance Bot
        arb_triangles, conversion_to_index, conversions = initialize_arb(client)

    except Exception: # TODO : handle Exceptions better
        traceback.print_exc()  # Prints error to console
        logging.exception("Caught an error:")  # Write error to log

        # Perform Arbitrage Function - TODO - this function is not ready yet
    while(1):
        try:
            find_best_arbitrages(arb_triangles, conversion_to_index, client)
        except Exception:
            print("\nCaught an error:\n" + str(traceback.print_exc()))  # Prints error to console
            logging.exception("Caught an error:")  # Write error to log
            time.sleep(1)

    # Data Output (log) in a text file - keep track of start/end time, trades, balance

    # Plot some outputs

    pass


'''
Initialize the arbitrage: build coins data structure
'''


def initialize_arb(client):

    welcome_message = "Welcome to the Binance Arbitrage Crypto Trader Bot Python Script!\n"
    bot_start_time = str(datetime.now())
    welcome_message += "Bot Start Time: {}\n\n".format(bot_start_time)
    print(welcome_message)
    logging.info(welcome_message)
    time.sleep(1)

    # Get dictionary of all optional prices
    conversions = client.get_orderbook_tickers()
    conversion_to_index = get_symbol_to_index(conversions)
    symbol_list = conversion_to_index.keys()
    arb_triangles = get_potential_arbitrages(symbol_list, conversions)

    return arb_triangles, conversion_to_index, conversions


'''
Build map of coins and their index
'''


def get_symbol_to_index(tickers):
    map_symbol_to_index = {}
    for i in range(0, len(tickers)):
        map_symbol_to_index[tickers[i]['symbol']] = i
    return map_symbol_to_index


'''
Build data structure of all potential triangle coins
'''


def get_potential_arbitrages(symbols, tickers):
    triangles = []

    seen_currencies = set()
    starting_currency = 'LTC'
    queue = deque([starting_currency])

    while len(queue) > 0:
        current_currency = queue.popleft()
        seen_currencies.add(current_currency)
        out_currencies = []

        for ticker in tickers:
            if ticker['symbol'].startswith(current_currency):
                out_currency = ticker['symbol'][len(current_currency):]
                out_currencies.append(out_currency)
                if out_currency not in seen_currencies:
                    queue.append(out_currency)

        for i in range(0, len(out_currencies)):
            for j in range(i+1, len(out_currencies)):
                forward_edge = out_currencies[i]+out_currencies[j]
                backward_edge = out_currencies[j]+out_currencies[i]

                if forward_edge in symbols:
                    triangle = [current_currency+out_currencies[j], current_currency+out_currencies[i], forward_edge]
                elif backward_edge in symbols:
                    triangle = [current_currency+out_currencies[i], current_currency+out_currencies[j], backward_edge]

                triangles.append(triangle)

    return triangles


'''
Find the arbitrage triangular coins that have profit
TODO - should change this function according to 'BinanceTriArbTrader.py' script
'''


def find_best_arbitrages(triangles, index_map, client):
    transaction_fee = 0.1
    max_return_list = np.array([])
    time_list = np.array([])
    iteration = 0
    matplotlib.interactive(True)
    while True:
        tickers = client.get_orderbook_tickers()
        for triangle in triangles:
            rate1 = float(tickers[index_map[triangle[0]]]['askPrice'])
            rate2 = float(tickers[index_map[triangle[1]]]['bidPrice'])*float(tickers[index_map[triangle[2]]]['bidPrice'])
            if round(rate1, 7) == 0:
                continue
            return_rate = (rate2-rate1)/(rate1)*100.0 - transaction_fee*3

            if return_rate > 0:
                print("Arbitrage is possible: " + str(return_rate) + "% arbitrage from " + triangle[1] + "->" + triangle[2])
                max_return_list = np.append(max_return_list, return_rate)
                time_list = np.append(time_list, iteration)
                iteration += 1

                plt.plot(time_list, max_return_list, 'b-*')
                plt.xlabel("Time (Seconds)", fontweight="bold")
                plt.ylabel("Return Rate (%)", fontweight="bold")
                plt.title("Triangular Arbitrage Live Return Rate", fontweight="bold")
                plt.show()
                plt.pause(0.0001)
                time.sleep(1)


'''
Get the prices of each two optional coins - maybe we will not use it
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



def animate(xs, ys, ax1):
    ax1.clear()
    ax1.plot(xs, ys)


if __name__ == "__main__":
    logging.basicConfig(filename='Trader.log', level=logging.DEBUG, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
    run()