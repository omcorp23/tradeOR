"""
define constants
"""
import datetime

# time for candles
WEEKS_NUM = 36
HOURS_IN_WEEK = 168
HOURS_IN_DAY = 24
DATE_START_TRADE = datetime.datetime(2020, 1, 1)

# moving average types
SMOOTHED = 1
SIMPLE = 2
EXPONENTIAL = 3

# fees
FEE_PER = 0.001

# Profit
PROFIT_PREC = 1.05