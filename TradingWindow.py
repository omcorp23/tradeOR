import time


class TradingWindow(object):
    def __init__(self, start_time='2019-11-05 00:00:00', end_time='2019-12-21 00:00:00', candle_time_frame='1m', candles_num=1000):
        self.start_time = start_time
        self.end_time = end_time
        self.candle_time_frame = candle_time_frame
        self.candles_num = candles_num