import logging
from Market import Market
from Wallet import Wallet
import TradingWindow
import plotly.graph_objs as go
from plotly.offline import plot
from pyti.smoothed_moving_average import smoothed_moving_average as sma
import constant
import Funcs
from datetime import datetime, timedelta


def get_candle(small_market, big_market, trading_window):

    # extract candles
    big_ohlcv = big_market.exchange.fetch_ohlcv('BTC/USDT', trading_window.candle_time_frame,
                                                big_market.exchange.parse8601(trading_window.start_time), 1)
    small_ohlcv = small_market.exchange.fetch_ohlcv('BTC/USD', trading_window.candle_time_frame,
                                                    small_market.exchange.parse8601(trading_window.start_time), 1)
    # add that week to database
    for j in range(0, len(big_ohlcv)):
        big_market.ohlcv.append(big_ohlcv[j])
        small_market.ohlcv.append(small_ohlcv[j])


'''
Real time
'''


def real_time_trading(small_market, big_market):

    # first get some data: 10 days before for better moving average
    now_plus = datetime.now().replace(microsecond=0) - timedelta()
    trading_window = TradingWindow.TradingWindow(start_time=now_plus,
                                                 candle_time_frame='1h', candles_num=1)
    get_candle(small_market, big_market, trading_window)

    while True:
        now = datetime.now()
        # check if it is xx:00 o'clock
        if now.minute == 0:
            # get the candle of the last hour
            new_start_time = str(now.replace(hour=now.hour - 1, minute=0, second=0, microsecond=0))
            trading_window = TradingWindow.TradingWindow(start_time=new_start_time,
                                                         candle_time_frame='1h', candles_num=1)
            get_candle(small_market, big_market, trading_window)


def run_real_time():

    # Initialize wallet and big and small markets
    wallet = Wallet()
    wallet.add_asset('USD', 100)
    small_market = Market("bitfinex")
    big_market = Market("binance")

    # Set the trading window and candle times
    real_time_trading(small_market, big_market)


if __name__ == "__main__":
    run_real_time()