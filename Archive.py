# imports
import plotly.graph_objs as go
from plotly.offline import plot
from pyti.smoothed_moving_average import smoothed_moving_average as sma
import itertools

'''
function for plotting the candles of the two markets. for showing the process
'''


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
?
'''


def flatten(ohlcv):
    return list(itertools.chain.from_iterable(ohlcv))