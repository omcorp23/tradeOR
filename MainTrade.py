import logging
from Market import Market
from Wallet import Wallet
import TradingWindow
import plotly.graph_objs as go
from plotly.offline import plot
from pyti.smoothed_moving_average import smoothed_moving_average as sma
import constant
import Funcs


# TODO General:
# 1) hold indicator for X time back - if the market is very high - don't buy - DONE
# 2) hold few open buys - DONE
# 3) add option to run in real-time
# 4) add support for more than 1000 candles - DONE
# 5) reorg + refactor code!! split code: functions for: strategy, plot etc... - DONE
# 6) add visual/other way to present how much did we earn
# 7) change small market because there is no BTC/USD
# 8) find the relevant coins to trade with, or make it generic after changing the small market
# 9) try different type of moving average
# 10) put all plot info in class - not sure it is necessary


'''
Plot the data
'''


def plot_data_for_prediction(big_market, small_market, gap, buy_signals, sell_signals, indicator_plot):

    # define small market candles for plotting
    candle = go.Candlestick(
        x=[small_market.exchange.iso8601(item[0]) for item in small_market.ohlcv],
        open=[item[1] - gap for item in small_market.ohlcv],
        close=[item[4] - gap for item in small_market.ohlcv],
        high=[item[2] - gap for item in small_market.ohlcv],
        low=[item[3] - gap for item in small_market.ohlcv],
        name="Candlesticks - small"
    )

    # define moving average for plotting
    fsma = go.Scatter(
        x=[big_market.exchange.iso8601(item[0]) for item in big_market.ohlcv],
        y=big_market.ma_fast,
        name="Fast SMA - big",
        line=dict(color=('rgba(102, 207, 255, 50)')))

    ssma = go.Scatter(
        x=[big_market.exchange.iso8601(item[0]) for item in big_market.ohlcv],
        y=big_market.ma_slow,
        name="Slow SMA - big",
        line=dict(color=('rgba(255, 207, 102, 50)')))

    # define buys and sells points for plotting
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
        y=[item[1] for item in sell_signals],
        name="Sell Signals",
        mode="markers",
        marker_size=10,
    )

    # define the indicator for plotting
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


'''
Strategy function
'''


def strategy(small_market, big_market, gap, num_of_buys=3):

    # init vars:
    small_candles = small_market.ohlcv
    difference = 1.2  # difference between big market's MA and small market in percentage
    buy_signals = []
    sell_signals = []
    indicator_plot = []
    peak_indicator = small_candles[1][4]
    indicator_plot.append([small_candles[1][0], small_candles[1][4]])
    above_ma = False
    open_buys = 0
    trade_id = 0
    trades = []
    open_buys_prices = Funcs.init_open_buys(num_of_buys)
    if big_market.ma_fast[0] < (small_candles[0][4] - gap):
        above_ma = True

    # strategy:
    for i in range(1, len(small_candles)):
        if i % 200 == 0:
            peak_indicator = (peak_indicator + small_candles[i][4]) / 2
            indicator_plot.append([small_candles[i][0], peak_indicator])
        if big_market.ma_fast[i] < (small_candles[i][4] - gap):
            if (not above_ma) and (open_buys < num_of_buys) and (small_candles[i][4] < peak_indicator):
                open_buys += 1
                trade_id += 1
                buy_signals.append([small_candles[i][0], small_candles[i][4]])
                Funcs.add_open_buy(small_candles[i][4], open_buys_prices, trade_id)
            above_ma = True
        elif big_market.ma_fast[i] > (small_candles[i][4] - gap):
            if above_ma and (open_buys > 0):
                id = Funcs.get_id_if_sell(small_candles[i][4], open_buys_prices, difference)
                if (id != -1):
                    matching_buy = Funcs.pop_buy(open_buys_prices, id)
                    trades.append([matching_buy, small_candles[i][4]])
                    open_buys -= 1
                    sell_signals.append([small_candles[i][0], small_candles[i][4]])
            above_ma = False
    Funcs.calculate_profit(trades)
    return buy_signals, sell_signals, indicator_plot


'''
Calculation of the moving average
'''


def calc_ma(big_market, ma_type):
    # calculate fast and slow simple moving averages of the big market
    if ma_type == constant.SIMPLE:
        big_market.ma_fast = sma([item[4] for item in big_market.ohlcv], 10)
        big_market.ma_slow = sma([item[4] for item in big_market.ohlcv], 30)
    elif ma_type == constant.EXPONENTIAL:
        print("Should add..")


'''
Find the gap of the currency value between the two markets.
'''


def calc_gap(small_market, big_market):
    small_open = [item[1] for item in small_market.ohlcv]
    big_open = [item[1] for item in big_market.ohlcv]
    sub = [small - big for small, big in zip(small_open, big_open)]
    gap = sum(sub) / len(sub)
    return gap

'''
Get candles of small and big markets.
'''


def get_candles(small_market, big_market, trading_window):
    for i in range(0, constant.WEEKS_NUM):
        # extract candles
        big_ohlcv = big_market.exchange.fetch_ohlcv('BTC/USDT', trading_window.candle_time_frame,
                                                    big_market.exchange.parse8601(trading_window.start_time),
                                                    constant.HOURS_IN_WEEK)
        small_ohlcv = small_market.exchange.fetch_ohlcv('BTC/USD', trading_window.candle_time_frame,
                                                        small_market.exchange.parse8601(trading_window.start_time),
                                                        constant.HOURS_IN_WEEK)
        # add that week to database
        for j in range(0, len(big_ohlcv)):
            big_market.ohlcv.append(big_ohlcv[j])
            small_market.ohlcv.append(small_ohlcv[j])
        # continue to the next week
        trading_window.add_week()


'''
The running function
'''


def run(wallet):

    # Initialize wallet and big and small markets
    wallet.add_asset('USD', 100)
    small_market = Market("bitfinex")
    big_market = Market("binance")

    # Set the trading window and candle times
    trading_window = TradingWindow.TradingWindow(start_time='2018-07-10 00:00:00', candle_time_frame='1h',
                                                 candles_num=1000)

    # Get attractive coins to trade with
    coins = ['BTC/USD']

    # Get candles of the two markets
    get_candles(small_market, big_market, trading_window)

    # Find the gap of the currency value between the two markets
    gap = calc_gap(small_market, big_market)

    # Calculate MA of the big market
    calc_ma(big_market, constant.SIMPLE)

    # Find buy and sell points
    buy_signals, sell_signals, indicator_plot = strategy(small_market, big_market, gap)

    # Plot data in graph
    plot_data_for_prediction(big_market, small_market, gap, buy_signals, sell_signals, indicator_plot)


'''
Main function
'''

if __name__ == "__main__":
    # create log
    logger = logging.basicConfig(filename='MainTrade.log', level=logging.DEBUG, filemode='w',
                                 format='%(asctime)s - %(levelname)s - %(message)s')

    # Wallet is a singleton - only instance is created here:
    wallet = Wallet()
    run(wallet)
