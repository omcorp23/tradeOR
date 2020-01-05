import ccxt
import logging
from Market import Market
from Wallet import Wallet
import TradingWindow
import plotly.graph_objs as go
from plotly.offline import plot
from pyti.smoothed_moving_average import smoothed_moving_average as sma
import itertools


def get_id_if_sell(price, open_buys_prices, difference):
    for i in range(0, len(open_buys_prices)):
        if (open_buys_prices[i][0] != -1) and (price > difference*open_buys_prices[i][0]):
            return open_buys_prices[i][1]
    return -1


def pop_buy(open_buys_prices, id):
    for i in range(0, len(open_buys_prices)):
        if open_buys_prices[i][1] == id:
            price = open_buys_prices[i][0]
            open_buys_prices[i] = [-1, 0]
    return  price


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
        precentage = ((trade[1] - trade[0])/trade[0])*100
        print("sale: "+ str(trade) + " profit in precentage: " + str(precentage))
        i += 1


def strategy(small_candles, big_market, gap, num_of_buys=3):
    # Init vars:
    difference = 1.2  # difference between big market's MA and small market in percentage
    buy_signals = []
    sell_signals = []
    indicator_plot = []
    peak_indicator = small_candles[1][4]
    indicator_plot.append([small_candles[1][0], small_candles[1][4]])
    above_ma = False
    distance_buy_counter = 0
    open_buys = 0
    trade_id = 0
    trades = []
    open_buys_prices = init_open_buys(num_of_buys)
    if big_market.ma_fast[0] < (small_candles[0][4] - gap):
        above_ma = True

    # Strategy:
    for i in range(1, len(small_candles)):
        if i % 200 == 0:
            peak_indicator = (peak_indicator + small_candles[i][4]) / 2
            indicator_plot.append([small_candles[i][0], peak_indicator])
        if big_market.ma_fast[i] < (small_candles[i][4] - gap):
            if (not above_ma) and (open_buys < num_of_buys) and (small_candles[i][4] < peak_indicator):
                if distance_buy_counter != 0 :
                    distance_buy_counter -= 1
                    continue
                distance_buy_counter = 4
                open_buys += 1
                trade_id += 1
                buy_signals.append([small_candles[i][0], small_candles[i][4]])
                add_open_buy(small_candles[i][4], open_buys_prices, trade_id)
            above_ma = True
        elif big_market.ma_fast[i] > (small_candles[i][4] - gap):
            if above_ma and (open_buys > 0):
                id = get_id_if_sell(small_candles[i][4], open_buys_prices, difference)
                if (id != -1):
                    matching_buy = pop_buy(open_buys_prices, id)
                    trades.append([matching_buy, small_candles[i][4]])
                    open_buys -= 1
                    sell_signals.append([small_candles[i][0], small_candles[i][4]])
            above_ma = False
    calculate_profit(trades)
    return buy_signals, sell_signals, indicator_plot


def plot_data_for_prediction(big_market, small_market):

    # define candles and find the gap
    small_candles = small_market.ohlcv
    big_candles = big_market.ohlcv
    small_open = [item[1] for item in small_candles]
    big_open = [item[1] for item in big_candles]
    sub = [small-big for small, big in zip(small_open, big_open)]
    gap = sum(sub)/len(sub)

    # candles of the small market
    candle = go.Candlestick(
        x=[small_market.exchange.iso8601(item[0]) for item in small_candles],
        open=[item[1]-gap for item in small_candles],
        close=[item[4]-gap for item in small_candles],
        high=[item[2]-gap for item in small_candles],
        low=[item[3]-gap for item in small_candles],
        name="Candlesticks - small"
    )

    # moving averages of the big market
    big_market.ma_fast = sma([item[4] for item in big_candles], 10)
    big_market.ma_slow = sma([item[4] for item in big_candles], 30)

    fsma = go.Scatter(
        x=[big_market.exchange.iso8601(item[0]) for item in big_candles],
        y=big_market.ma_fast,
        name="Fast SMA - big",
        line=dict(color=('rgba(102, 207, 255, 50)')))

    ssma = go.Scatter(
        x=[big_market.exchange.iso8601(item[0]) for item in big_candles],
        y=big_market.ma_slow,
        name="Slow SMA - big",
        line=dict(color=('rgba(255, 207, 102, 50)')))

    buy_signals, sell_signals, indicator_plot = strategy(small_candles, big_market, gap, 6)

    # TODO: Move to other funtion\ class\ whatever
    buys = go.Scatter(
        x=[item[0] for item in buy_signals],
        y=[item[1] for item in buy_signals],
        name="Buy Signals",
        mode="markers",
        marker_size=10,
        marker_color='rgba(247, 202, 24, 1)',
    )
    sells = go.Scatter(
        x=[item[0] for item in sell_signals],
        y=[item[1]  for item in sell_signals],
        name="Sell Signals",
        mode="markers",
        marker_size=10,
    )

    indicator = go.Scatter(
        x=[item[0] for item in indicator_plot],
        y=[item[1] for item in indicator_plot],
        name="indicator",
        line=dict(color=('rgba(34, 90, 200, 50)')),
    )

    # style and display
    data = [candle, fsma, buys, sells, indicator]
    layout = go.Layout(title='BTC/USD')
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename='predictingMarket.html')


def plot_data(big_market, small_market):
    small_candles = small_market.ohlcv
    candle = go.Candlestick(
        x=[small_market.exchange.iso8601(item[0]) for item in small_candles],
        open=[item[1] for item in small_candles],
        close=[item[4] for item in small_candles],
        high=[item[2] for item in small_candles],
        low=[item[3] for item in small_candles],
        name="Candlesticks - small"
    )

    # For Debug:
    big_candles = big_market.ohlcv
    candle2 = go.Candlestick(
        x=[big_market.exchange.iso8601(item[0]) for item in big_candles],
        open=[item[1] for item in big_candles],
        close=[item[4] for item in big_candles],
        high=[item[2] for item in big_candles],
        low=[item[3] for item in big_candles],
        increasing=dict(line=dict(color='#17BECF')),
        decreasing=dict(line=dict(color='#7F7F7F')),
        name="Candlesticks - big"
    )
    #################

    big_candles = big_market.ohlcv
    # add the moving averages TODO: Move to the market class
    big_market.ma_fast = sma([item[4] for item in big_candles], 10)
    big_market.ma_slow = sma([item[4] for item in big_candles], 30)
    # plot MAs
    fsma = go.Scatter(
        x=[big_market.exchange.iso8601(item[0]) for item in big_candles],
        y=big_market.ma_fast,
        name="Fast SMA",
        line=dict(color=('rgba(102, 207, 255, 50)')))

    ssma = go.Scatter(
        x=[big_market.exchange.iso8601(item[0]) for item in big_candles],
        y=big_market.ma_slow,
        name="Slow SMA",
        line=dict(color=('rgba(255, 207, 102, 50)')))

    data = [candle, candle2, ssma, fsma]
    # style and display
    layout = go.Layout(title='BTCUSD')
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename='tmp.html')


'''
The algorithm
'''
# TODO General:
# 1) hold indicator for X time back - if the market is very high - don't buy - DONE
# 2) hold few open buys - DONE
# 3) add option to run in real-time
# 4) add support for more than 1000 candles - DONE
# 5) reorg + refactor code!! split code: functions for: strategy, plot etc...
# 6) add visual/other way to present how much did we earn
# 7) add mechanism to distance buys - DONE (4 candles diff)

def flatten(ohlcv):
    return list(itertools.chain.from_iterable(ohlcv))


def run(wallet):

    # Initialize big and small markets
    wallet.add_asset('USD', 100)
    small_market = Market("bitfinex")
    big_market = Market("binance")

    # Set the trading window and candle times
    trading_window = TradingWindow.TradingWindow(start_time='2018-04-10 00:00:00', candle_time_frame='1h', candles_num=1000)

    #small_market.rates = small_market.exchange.fetch_ticker()
    #print(small_market.rates)
    # TODO: get all coins relevant for this
    coins = ['BTC/USD']

    #First week:
    big_market.ohlcv = big_market.exchange.fetch_ohlcv('BTC/USDT', trading_window.candle_time_frame,
                                                        big_market.exchange.parse8601(trading_window.start_time),
                                                            168)
    small_market.ohlcv = small_market.exchange.fetch_ohlcv('BTC/USD', trading_window.candle_time_frame,
                                                        small_market.exchange.parse8601(trading_window.start_time),
                                                            168)
    trading_window.add_week()
    num_of_weeks = 80
    for i in range(1,num_of_weeks):
    # Extract candles
        big_ohlcv = big_market.exchange.fetch_ohlcv('BTC/USDT', trading_window.candle_time_frame,
                                                        big_market.exchange.parse8601(trading_window.start_time),
                                                            168)
        small_ohlcv = small_market.exchange.fetch_ohlcv('BTC/USD', trading_window.candle_time_frame,
                                                        small_market.exchange.parse8601(trading_window.start_time),
                                                            168)
        for j in range(0,len(big_ohlcv)):
            big_market.ohlcv.append(big_ohlcv[j])
            small_market.ohlcv.append(small_ohlcv[j])
        trading_window.add_week()
    #big_market.ohlcv = big_ohlcv
    #small_market.ohlcv = small_ohlcv
    # TODO: Extract graph of the 2 markets
    #plot_data(big_market, small_market)
    plot_data_for_prediction(big_market, small_market)

    # TODO: check if there is a following pattern


'''
Main function
'''


if __name__ == "__main__":
    logger = logging.basicConfig(filename='MainTrade.log', level=logging.DEBUG, filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # Wallet is a singleton - only instance is created here:
    wallet = Wallet()
    run(wallet)