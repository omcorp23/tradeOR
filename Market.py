import Keys
import ccxt


class Market(object):
    def __init__(self, name):
        self.name = name
        exchange_class = getattr(ccxt, self.name)
        try:
            if name not in Keys.myKeys:
                raise ccxt.ExchangeNotAvailable("doesn't have keys for this market")
            self.exchange = exchange_class({
                'apiKey': Keys.myKeys[name]['API_key'],
                'secret': Keys.myKeys[name]['API_secret'],
                'timeout': 30000,
                'enableRateLimit': True,
            })
        except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
            print('Got an error while creating Market', type(error).__name__, error.args)
        self.ohlcv = []
        self.indicator_arr = None
        self.indicator_counter = 0
        self.rates = None
        self.ma_fast = None
        self.ma_slow = None
        self.ma_curve = None
