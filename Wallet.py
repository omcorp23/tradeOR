import Keys
import ccxt
import logging
import datetime
import constant


class Wallet:
    def __init__(self):
        self.assets = {} # Dict of 'symbol' and amount - represent our assets
        self.fees = [] # Array of 'symbol', amount and time - represent the fees paid
        self.logger = logging.getLogger('MainTrade.log')
        self.logger.info("Wallet created empty")

    # TODO: Check that all times are synced
    def pay_fee(self, symbol, amount):
        am = self.assets[symbol]
        if am < amount: # This is not really possible - holier than the pope
            raise Exception("not enough money to pay fee")
        self.fees.append([symbol, amount, datetime.datetime.now()])
        self.logger.info("fee of " + str(amount) + " " + symbol + " paid")

    def add_asset(self, symbol, amount):
        am = 0
        if symbol in self.assets.keys():
            am = self.assets[symbol]
        self.assets[symbol] = am + amount
        self.logger.info("added " + str(amount) + " " + symbol + " to wallet")

    def subtract_asset(self, symbol, amount):
        am = 0
        if symbol in self.assets.keys():
            am = self.assets[symbol]
        self.assets[symbol] = am - amount
        self.logger.info("added " + str(amount) + " " + symbol + " to wallet")

    def transaction(self, base_id, quote_id, base_amount, ratio, fee_percentage=constant.FEE_PER):

        # sell all
        if base_amount == 'all':
            base_amount = self.assets[base_id] - self.assets[base_id]*fee_percentage - 0.01

        # check how much we have in base
        if base_id in self.assets.keys():
            am = self.assets[base_id]
            if base_amount + base_amount*fee_percentage > am:
                self.logger.info("Not enough " + str(base_id))
                raise Exception("Not enough " + str(base_id))
        else:
            self.logger.info("Symbol not exist")
            raise Exception("Symbol not exist")

        # sub the amount from base
        self.assets[base_id] = am - (base_amount + base_amount*fee_percentage)
        self.logger.info("subtracted " + str(base_amount) + " " + quote_id + " to wallet")

        # add the amount to quote
        # TODO - check the ratio
        am = 0
        if quote_id in self.assets.keys():
            am = self.assets[quote_id]

        amount_to_add = base_amount*ratio
        self.assets[quote_id] = am + amount_to_add
        self.logger.info("added " + str(amount_to_add) + " " + quote_id + " to wallet")

    def print_status(self):
        print(self.assets)
        print(self.fees)