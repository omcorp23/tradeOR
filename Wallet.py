import Keys
import ccxt
import logging
import datetime

class Wallet:
    def __init__(self):
        self.assets = {} # Dict of 'symbol' and amount - represent our assets
        self.fees = [] # Array of 'symbol', amount and time - represent the fees paid
        self.logger = logging.getLogger('MainTrade.log')
        self.logger.info("Wallet created empty")

    # TODO: Check that all times are synced
    def pay_fee(self, symbol, amount):
        [am, tm] = self.assets[symbol]
        if am < amount: # This is not really possible - holier than the pope
            raise Exception("not enough money to pay fee")
        self.fees.append([symbol, amount, datetime.datetime.now()])
        self.logger.info("fee of " + str(amount) + " " + symbol +" paid")

    def add_asset(self, symbol, amount):
        [am, tm] = self.assets[symbol]
        self.assets[symbol] = [am + amount, datetime.datetime.now()]
        self.logger.info("added " + str(amount) + " " + symbol + " to wallet")