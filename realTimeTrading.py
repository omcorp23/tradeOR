import logging
from Market import Market
from Wallet import Wallet
import TradingWindow
import plotly.graph_objs as go
from plotly.offline import plot
from pyti.smoothed_moving_average import smoothed_moving_average as sma
import constant
import helperFunctions
from datetime import datetime, timedelta
from pyti.simple_moving_average import simple_moving_average as simple_ma
from pyti.smoothed_moving_average import smoothed_moving_average as smoothed_ma
from pyti.exponential_moving_average import exponential_moving_average as exponential_ma
import numpy as np
import helperFunctions as funcs
import time



# TODO General:
# 1) now it is only simple ma, should add all of them
# 2) build peak indicator with the previous data we collect before the algo
# 3) fix "if big_market.ma_curve[0] < (small_candles[0][4] - gap):" because first 20 elem are nan
# 4) fix the algo to fit to real time

'''
Plot the data
'''


def plot_data(big_market, small_market, gap, buy_signals, sell_signals):

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
    ma_curve = go.Scatter(
        x=[big_market.exchange.iso8601(item[0]) for item in big_market.ohlcv],
        y=big_market.ma_curve,
        name="Fast SMA - big",
        line=dict(color=('rgba(102, 207, 255, 50)')))

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
        x=[item[0] for item in small_market.indicator_arr],
        y=[item[1] for item in small_market.indicator_arr],
        name="indicator",
        line=dict(color=('rgba(34, 90, 200, 50)')),
    )

    # style and display
    data = [candle, ma_curve, buys, sells, indicator]
    layout = go.Layout(title='BTC/USD')
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename='plotData.html')


'''
Strategy function
'''


def trade_from_ob(wallet_ob, small_market, amount_to_sell,buy):
    order_book = small_market.exchange.fetch_order_book('BTC/USD', 20)

    # Buy signal:
    asks = order_book['asks']
    bids = order_book['bids']
    quantity_bought = 0
    if buy:
        money_left = constant.MAX_BUDGET_PER_BUY
        cash = wallet_ob.assets['USD']
        for i in range(0, constant.ORDER_BOOK_DEPTH):
            price = asks[i][0] * asks[i][1]
            if price <= money_left and price < cash:
                logging.info("ratio: " + str(asks[i][0]) + " and price: " + str(price))
                wallet_ob.transaction(base_id='USD', quote_id='BTC', base_amount=price, ratio=1 / asks[i][0])
                money_left -= price
                quantity_bought += asks[i][1]
        logging.info("total spent on this buy point: " + str(constant.MAX_BUDGET_PER_BUY - money_left))
    else:
        money_left = amount_to_sell
        cash = wallet_ob.assets['BTC']
        for i in range(0, constant.ORDER_BOOK_DEPTH):
            price = bids[i][0] * bids[i][1]
            if bids[i][1] <= money_left and bids[i][1] <= cash:
                logging.info("ratio: " + str(bids[i][0]) + " and price: " + str(price))
                wallet_ob.transaction(base_id='BTC', quote_id='USD', base_amount=bids[i][1], ratio=1 / bids[i][0])
                money_left -= bids[i][1]
        logging.info("total sold: " + str(amount_to_sell - money_left))
    return quantity_bought





def strategy(small_market, big_market, gap, wallet, wallet_ob):

    # init vars:
    small_market.indicator_counter += 1
    small_candles = small_market.ohlcv
    buy_signals = []
    sell_signals = []
    above_ma = False
    open_buys = 0
    trade_id = 0
    trades = []
    open_buys_prices = funcs.init_open_buys(constant.NUM_OF_BUYS)
    if big_market.ma_fast[0] < (small_candles[0][4] - gap):
        above_ma = True

    # strategy:
    for i in range(len(small_candles) - 1, len(small_candles)):
        if small_market.indicator_counter % constant.INDICATOR_SENSITIVITY == 0:
            peak_indicator = (small_market.indicator_arr[-1][1] + small_candles[i][4]) / 2
            small_market.indicator_arr.append([small_candles[i][0], peak_indicator])
        if True or big_market.ma_curve[i] < (small_candles[i][4] - gap):
            if True or ((not above_ma) and (open_buys < constant.NUM_OF_BUYS) and (small_candles[i][4] < small_market.indicator_arr[-1][1])):
                # Buy!
                open_buys += 1
                trade_id += 1
                buy_signals.append([small_candles[i][0], small_candles[i][4]])
                # perform transaction
                wallet.transaction(base_id='USD', quote_id='BTC', base_amount=100, ratio=1 / small_candles[i][4])
                wallet.print_status()
                amount_bought = trade_from_ob(wallet_ob, small_market,amount_to_sell=0, buy=True)
                funcs.add_open_buy(small_candles[i][4], open_buys_prices, amount_bought, trade_id)
            above_ma = True
        elif True or big_market.ma_curve[i] > (small_candles[i][4] - gap):
            if True or (above_ma and (open_buys > 0)):
                id = funcs.get_id_if_sell(small_candles[i][4], open_buys_prices, constant.PROFIT_PREC)
                if (id != -1):
                    # Sell!
                    matching_buy = funcs.pop_buy(open_buys_prices, id)
                    trades.append([matching_buy[0], small_candles[i][4]])
                    amount_to_sell = 100 / matching_buy
                    open_buys -= 1
                    sell_signals.append([small_candles[i][0], small_candles[i][4]])
                    trade_from_ob(wallet_ob, small_market, matching_buy[2], buy=False)
                    # perform transaction
                    wallet.transaction(base_id='BTC', quote_id='USD', base_amount=amount_to_sell,
                                       ratio=small_candles[i][4])
                    wallet.print_status()
            above_ma = False
    funcs.calculate_profit(trades)
    return buy_signals, sell_signals


'''
Real time trading function
'''


def init_indicator(small_market):
    # init vars:
    small_candles = small_market.ohlcv
    indicator_plot = []
    peak_indicator = small_candles[1][4]
    indicator_plot.append([small_candles[1][0], small_candles[1][4]])

    # strategy:
    for i in range(1, len(small_candles)):
        if i % 200 == 0:
            peak_indicator = (peak_indicator + small_candles[i][4]) / 2
            indicator_plot.append([small_candles[i][0], peak_indicator])
    small_market.indicator_counter = len(small_candles)
    small_market.indicator_arr = indicator_plot


def real_time_trading(small_market, big_market, trading_window, gap, wallet, wallet_ob):

    print("started real time loop")
    while True:
        now = datetime.utcnow().replace(second=0, microsecond=0)
        # if it is xx:00 o'clock, get the last candle
        #if True:
        if now.minute == 49:

            # get the candle of the last hour
            new_start_time = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            print("current time is: " + str(datetime.utcnow().replace(microsecond=0)) + ". start real time for " + str(new_start_time))
            trading_window.set_start_time(new_start_time=str(new_start_time))

            # add candle of this point
            get_candles(small_market, big_market, trading_window)

            # calculate the moving average of this point
            add_ma_point(big_market, constant.SIMPLE)

            # activate the algorithm
            buy_signals, sell_signals = strategy(small_market, big_market, gap, wallet, wallet_ob)

            # Plot:
            plot_data(big_market, small_market, gap, buy_signals, sell_signals)

            print("end real time at: " + str(datetime.utcnow().replace(microsecond=0)) + ". go to sleep for 58 minutes")
            time.sleep(3480)
            print("woke up from sleep in: " + str(datetime.utcnow().replace(microsecond=0)))

'''
Get candles
'''


def get_candles(small_market, big_market, trading_window):

    # extract candles
    big_ohlcv = big_market.exchange.fetch_ohlcv('BTC/USDT', trading_window.candle_time_frame,
                                                big_market.exchange.parse8601(trading_window.start_time),
                                                trading_window.candles_num)
    small_ohlcv = small_market.exchange.fetch_ohlcv('BTC/USD', trading_window.candle_time_frame,
                                                    small_market.exchange.parse8601(trading_window.start_time),
                                                    trading_window.candles_num)
    # add the candles to database
    for j in range(0, len(big_ohlcv)):
        big_market.ohlcv.append(big_ohlcv[j])
        small_market.ohlcv.append(small_ohlcv[j])




'''
Calculation of the moving average
'''


def calc_ma(big_market, ma_type, ma_speed=100):
    # calculate fast and slow simple moving averages of the big market
    if ma_type == constant.SMOOTHED:
        big_market.ma_fast = smoothed_ma([item[4] for item in big_market.ohlcv], ma_speed)
    elif ma_type == constant.SIMPLE:
        big_market.ma_fast = simple_ma([item[4] for item in big_market.ohlcv], ma_speed)
        big_market.ma_curve = simple_ma([item[4] for item in big_market.ohlcv], ma_speed)
    elif ma_type == constant.EXPONENTIAL:
        big_market.ma_fast = exponential_ma([item[4] for item in big_market.ohlcv], ma_speed)


def add_ma_point(big_market, ma_type, ma_speed=100):
    # calculate fast and slow simple moving averages of the big market
    if ma_type == constant.SIMPLE:
        ma_tmp = simple_ma([item[4] for item in big_market.ohlcv[-ma_speed:]], ma_speed)
        big_market.ma_curve = np.append(big_market.ma_curve, ma_tmp[-1])


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
Get data of the last 10 days for moving average curve
Get the gap between the two markets
'''


def get_previous_data(small_market, big_market, weeks_num=15):

    # set trading window
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    now_minus = now - timedelta(weeks=weeks_num)
    trading_window = TradingWindow.TradingWindow(start_time=str(now_minus),
                                                 candle_time_frame='1h', candles_num=constant.HOURS_IN_WEEK)
    print(trading_window.start_time)
    for i in range(0, weeks_num):
        get_candles(small_market, big_market, trading_window)
        # continue to the next week
        trading_window.add_week()
        print(trading_window.start_time)

    # debug prints
    print("Collecting data starting from: " + small_market.exchange.iso8601(big_market.ohlcv[0][0]))
    print("Until: " + small_market.exchange.iso8601(big_market.ohlcv[-1][0]))

    # get candle of the last hour
    trading_window.set_candles_num(new_candles_num=1)
    #get_candles(small_market, big_market, trading_window)

    # debug prints
    print("Collecting data starting from: " + small_market.exchange.iso8601(big_market.ohlcv[0][0]))
    print("Until: " + small_market.exchange.iso8601(big_market.ohlcv[-1][0]))

    # calculate the gap for accurate results
    gap = calc_gap(small_market, big_market)

    # calculate moving average for plotting
    calc_ma(big_market, constant.SIMPLE)
    #plot_data(big_market, small_market, gap)

    # set trading window to single candle
    init_indicator(small_market)
    return trading_window, gap


'''
Main function
'''


def run_real_time():
    logging.basicConfig(filename='transaction.log', level=logging.DEBUG, filemode='w',
                                 format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize wallet
    wallet = Wallet()
    wallet.add_asset('USD', constant.MAX_BUDGET_PER_BUY * constant.NUM_OF_BUYS)
    wallet.add_asset('BTC', constant.BITCOIN_FOR_FEES)

    wallet_ob = Wallet()
    wallet_ob.add_asset('USD', constant.MAX_BUDGET_PER_BUY * constant.NUM_OF_BUYS)
    wallet_ob.add_asset('BTC', constant.BITCOIN_FOR_FEES)

    # Initialize big and small markets
    small_market = Market("bitfinex")
    big_market = Market("binance")

    '''
    #### test for order book trading ####

    now = datetime.utcnow().replace(second=0, microsecond=0)
    new_start_time = now.replace(second=0, microsecond=0) - timedelta(hours=1)
    trading_window = TradingWindow.TradingWindow(start_time=str(new_start_time),
                                                 candle_time_frame='1h', candles_num=1)

    print("current time is: " + str(datetime.utcnow().replace(microsecond=0)) + ". start real time for " + str(
        new_start_time))
    trading_window.set_start_time(new_start_time=str(new_start_time))
    get_candles(small_market, big_market, trading_window)
    order_book = small_market.exchange.fetch_order_book('BTC/USD', 20)

    # Buy signal:
    asks = order_book['asks']
    cash = wallet.assets['USD']
    price = 0
    money_left = constant.MAX_BUDGET_PER_BUY
    for i in range(0, constant.ORDER_BOOK_DEPTH):
        price = asks[i][0]*asks[i][1]
        if price <= money_left and price < cash:
            logging.info("ratio: " + asks[i][0] + " and price: " + price)
            wallet_ob.transaction(base_id='USD', quote_id='BTC', base_amount=price, ratio=1/asks[i][0])
            money_left -= price
    logging.info("total spent on this buy point: " + constant.MAX_BUDGET_PER_BUY - money_left)
'''






    # Get data of the last 10 days for moving average curve
    print("get previous data STARTS at: " + str(datetime.utcnow().replace(microsecond=0)))
    trading_window, gap = get_previous_data(small_market, big_market)
    print("get previous data ENDS at: " + str(datetime.utcnow().replace(microsecond=0)))
    # Perform real time trading
    real_time_trading(small_market, big_market, trading_window, gap, wallet, wallet_ob)


if __name__ == "__main__":
    run_real_time()

