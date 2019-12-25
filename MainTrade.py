import ccxt
import logging
from Market import Market
from Wallet import Wallet
import TradingWindow
import plotly.graph_objs as go
from plotly.offline import plot
from pyti.smoothed_moving_average import smoothed_moving_average as sma

'''
Main function
'''

'''
def initMarkets():
    ccxt.exchanges
    small_market = Market("bitbay")
    big_market = Market("binance")
    return small_market, big_market
'''


def plot_data(big_market, small_market):
    small_candles = small_market.ohlcv
    candle  = go.Candlestick(
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


def run(wallet):
    # Initialize big and small markets
    small_market = Market("bitfinex")
    big_market = Market("binance")
    # Set the trading window and candle times
    trading_window = TradingWindow.TradingWindow()

    coins = ['BTC/USD'] # TODO: get all coins relevant for this
    # Extract candles
    big_market.ohlcv = big_market.exchange.fetch_ohlcv('BTC/USDT', trading_window.candle_time_frame,
                                                       big_market.exchange.parse8601(trading_window.start_time),
                                                       1000)
    print(big_market.ohlcv)

    small_market.ohlcv = small_market.exchange.fetch_ohlcv('BTC/USD', trading_window.candle_time_frame,
                                                       small_market.exchange.parse8601(trading_window.start_time),
                                                           1000)
    print(small_market.ohlcv)

    # TODO: Extract graph of the 2 markets
    plot_data(big_market, small_market)
    # TODO: check if there is a following pattern




if __name__ == "__main__":
    logger = logging.basicConfig(filename='MainTrade.log', level=logging.DEBUG, filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # Wallet is a singleton - only instance is created here:
    wallet = Wallet()
    run(wallet)