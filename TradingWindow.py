from datetime import datetime, timedelta
import dateutil.parser


class TradingWindow(object):
    def __init__(self, start_time='2019-11-05 00:00:00', end_time='2019-12-21 00:00:00', candle_time_frame='1m',
                 candles_num=1000):
        self.start_time = start_time
        self.end_time = end_time
        self.candle_time_frame = candle_time_frame
        self.candles_num = candles_num

    def add_week(self):
        yourdate = dateutil.parser.parse(self.start_time)
        yourdate = yourdate + timedelta(weeks=1)
        self.start_time = yourdate.isoformat()

    def add_day(self):
        yourdate = dateutil.parser.parse(self.start_time)
        yourdate = yourdate + timedelta(days=1)
        self.start_time = yourdate.isoformat()

    def add_hour(self):
        yourdate = dateutil.parser.parse(self.start_time)
        yourdate = yourdate + timedelta(hours=1)
        self.start_time = yourdate.isoformat()


    def set_start_time(self, new_start_time):
        self.start_time = new_start_time

    def set_candles_num(self, new_candles_num):
        self.candles_num = new_candles_num

