api_key = "0j8EtlQ1cdhm31H1BCWpCix7OaXGou1snrPjssBr515TOF5vhfDINNxjRN4qblox"
api_secret = "qoVISOWPsyChAEukRo42T4ARGmEcNGUCzFGOp3rZIexIzBzbduTvNjZu0R2zD1MZ"

import datetime
from time import sleep
from binance.client import Client

client = Client(api_key, api_secret)

symbol= 'BTCUSDT'
quantity= '0.05'

order= False
while order==False:
    BTC= client.get_historical_klines(symbol=symbol, interval='30m', start_str="1 hour ago UTC")
    print(BTC[-1][4])
    print(BTC[-2][4])
    if (float(BTC[-1][4])-float(BTC[-2][4])) > 5:
        print ('Buyyy')
        #client.order_market_buy(symbol= symbol, quantity= quantity)
        #order= True
    elif (float(BTC[-1][4])-float(BTC[-2][4])) < -5:
        print ('Sellll')
        #client.order_market_buy(symbol= symbol , quantity= quantity)
        #order= True
    else:
        print ('Do nothing')
    sleep(10)