import ccxt
import logging
import Market
import TradingWindow

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

def run():
    # Initialize big and small markets
    small_market = Market.Market("bitfinex")
    big_market = Market.Market("binance")
    # Set the trading window and candle times
    trading_window = TradingWindow.TradingWindow()

    coins = ['BTC/USD'] # TODO: get all coins relevant for this

    # Extract candles
    big_market.ohlcv = big_market.exchange.fetch_ohlcv('BTC/USDT', trading_window.candle_time_frame, big_market.exchange.parse8601(trading_window.start_time), trading_window.candles_num)
    print(big_market.ohlcv)

    small_market.ohlcv = small_market.exchange.fetch_ohlcv('BTC/USD', trading_window.candle_time_frame,
                                                       small_market.exchange.parse8601(trading_window.start_time), trading_window.candles_num)
    print(small_market.ohlcv)

    # TODO: Extract graph of the 2 markets

    # TODO: check if there is a following pattern



if __name__ == "__main__":
    logging.basicConfig(filename='MainTrade.log', level=logging.DEBUG, filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')
    run()