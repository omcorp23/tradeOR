"""
define constants
"""
import datetime

# time for candles
WEEKS_NUM = 80
HOURS_IN_WEEK = 168
HOURS_IN_DAY = 24
DATE_START_TRADE = datetime.datetime(2018, 1, 1)

# moving average types
SMOOTHED = 1
SIMPLE = 2
EXPONENTIAL = 3

# fees
FEE_PER = 0.001

# Profit
PROFIT_PREC = 1.10
INDICATOR_SENSITIVITY = 200 #(smaller - more sensitive)

# Order Book:
MAX_BUDGET_PER_BUY = 600
ORDER_BOOK_DEPTH = 20
NUM_OF_BUYS = 7
BITCOIN_FOR_FEES = 0.01