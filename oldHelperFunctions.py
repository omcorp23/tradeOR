"""
Helper functions
"""


def get_id_if_sell(price, open_buys_prices, difference):
    for i in range(0, len(open_buys_prices)):
        if (open_buys_prices[i][0] != -1) and (price > difference * open_buys_prices[i][0]):
            return open_buys_prices[i][1]
    return -1


def pop_buy(open_buys_prices, id):
    for i in range(0, len(open_buys_prices)):
        if open_buys_prices[i][1] == id:
            price = open_buys_prices[i][0]
            open_buys_prices[i] = [-1, 0]
    return price


def add_open_buy(price, open_buys_prices, trade_id):
    for j in range(0, len(open_buys_prices)):  # Insert buy to open_buys
        if open_buys_prices[j][0] == -1:
            open_buys_prices[j] = [price, trade_id]
            break


def init_open_buys(num_of_buys):
    a = []
    for j in range(0, num_of_buys):
        a.append([-1, 0])
    return a


def calculate_profit(trades):
    i = 0
    for trade in trades:
        percentage = ((trade[1] - trade[0]) / trade[0]) * 100
        print("sale: " + str(trade) + " profit in percentage: " + str(percentage))
        i += 1