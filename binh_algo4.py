import requests
import numpy as np
from time import sleep
import multiprocessing

import pandas as pd
import pandas_ta as ta

s = requests.Session()
s.headers.update({'X-API-key': 'L7F4EJ9X'}) # TODO: update API Key

############################################ Constants ############################################
MAX_NET_LIMIT = 7000
MAX_EXPOSURE_GROSS = 100000 
CONVERTER_LIMIT = 100000

ORDER_LIMIT = 4000
ORDER_LIMIT_2 = 2000 
CASH_LIMIT_GROSS = 10000000
ETF_REDEMPTION_COST = 0.0375
MARKET_ORDER_FEE = 0.01
LIMIT_ORDER_REBATE = -0.0025
ETF_LIMIT_REBATE = -0.0075
ETF_ORDER_FEE = 0.009

MIN_PROFIT = 0.05 # TODO: these profit numbers
HI_MIN_PROFIT = 0.1
SUPER_HI_PROFIT = 0.24

MIN_SPREAD = 0.04

SLEEP_TIME = 1.9
SLEEP_TIME_2 = 2.1

############################################ HELPER FUNCTIONS ############################################
def get_tick():
    resp = s.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick'], case['status']

def get_ticker_position(ticker):
    resp = s.get('http://localhost:9999/v1/securities')
    if resp.ok:
        positions = resp.json()
        if ticker == 'CAD':
            return positions[0]['position']
        
        elif ticker == 'RGLD':
            return positions[1]['position']
        
        elif ticker == 'RFIN':
            return positions[2]['position']
        
        elif ticker == 'INDX':
            return positions[3]['position']

def get_bid_ask(ticker):
    payload = {'ticker': ticker}
    resp = s.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        best_bid_price = book['bids'][0]['price']
        best_ask_price = book['asks'][0]['price']
        return best_bid_price, best_ask_price

def get_position():
    resp = s.get('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        gross_position = abs(book[1]['position']) + abs(book[2]['position']) + 2 * abs(book[3]['position'])
        net_position = book[1]['position'] + book[2]['position']+ 2 * book[3]['position'] # net position is 2 stocks = 1 ETF
        return gross_position, net_position

def place_order(ticker, action, quantity, order_type='MARKET', price=None):
    params = {
        'ticker': ticker,
        'type': order_type,
        'quantity': quantity,
        'action': action
    }
    if price:
        params['price'] = price
    s.post('http://localhost:9999/v1/orders', params=params)

############################################ STRATEGY 1: ETF ARBITRADGE ############################################
def etf_arbitrage_strategy():
    
    def get_leases_id():
        resp = s.get('http://localhost:9999/v1/leases')
        if resp.ok:
            leases = resp.json()
            creation_id = [lease['id'] for lease in leases if lease['ticker'] == 'ETF-Creation']
            redemption_id = [lease['id'] for lease in leases if lease['ticker'] == 'ETF-Redemption']
            return creation_id, redemption_id

    # to use lease
    def use_lease():
        creation_id, redemption_id = get_leases_id()
        
        indx_pos = get_ticker_position('INDX')
        rgld_pos = get_ticker_position('RGLD')
        rfin_pos = get_ticker_position('RFIN')
        
        if indx_pos < 0:
            id = str(creation_id[0])
            quantity = min(min(abs(rgld_pos), abs(rfin_pos)), 100000)
            s.post('http://localhost:9999/v1/leases/' + str(id), params = {'from1':
            'RGLD', 'quantity1': quantity, 'from2': 'RFIN', 'quantity2': quantity})
        
        elif indx_pos > 0:
            id = str(redemption_id[0])
            quantity = min(abs(indx_pos), 100000)
            s.post('http://localhost:9999/v1/leases/' + str(id), params = {'from1':
            'INDX', 'quantity1': quantity, 'from2': 'CAD', 'quantity2': quantity * ETF_REDEMPTION_COST})

    # redeeming: sell stocks, buy ETFs
    def sell_stocks_buy_etf():
        place_order('RGLD', 'SELL', ORDER_LIMIT)
        place_order('RFIN', 'SELL', ORDER_LIMIT)
        place_order('INDX', 'BUY', ORDER_LIMIT)

    # convertiing: buy stocks, sell ETFs
    def buy_stocks_sell_etf():
        place_order('RGLD', 'BUY', ORDER_LIMIT)
        place_order('RFIN', 'BUY', ORDER_LIMIT)
        place_order('INDX', 'SELL', ORDER_LIMIT)

    ticker_list = ['RGLD', 'RFIN', 'INDX']
    market_prices = np.zeros((3, 2))
    #tick_to_close = 0

    # start creation lease
    s.post('http://localhost:9999/v1/leases', params = {'ticker': 'ETF-Creation'})

    # start redemption lease
    s.post('http://localhost:9999/v1/leases', params = {'ticker': 'ETF-Redemption'})

    # create a text file to log trades
    # generate a random number to name the text file 
    num = np.random.randint(1000)
    f = open(f'etf_arbitradge_trades_log_{num}.txt', 'w')

    while True:
        tick, status = get_tick()
        #news_tick, content = get_news()

        if status != 'ACTIVE':
            print("Case Inactive")

        elif status == 'ACTIVE':
            for i, ticker in enumerate(ticker_list):
                market_prices[i, 0], market_prices[i, 1] = get_bid_ask(ticker)

            gross_position, net_position = get_position()

            fee = MARKET_ORDER_FEE * 2 + ETF_ORDER_FEE 
            
            redeem_profit = (market_prices[0, 0] + market_prices[1, 0] - fee - ETF_REDEMPTION_COST) - market_prices[2, 1]
            convert_profit = (market_prices[2, 0] - fee) - (market_prices[0, 1] + market_prices[1, 1])

            print(f"===== TICK: {tick} =======")
            print(f"gross position: {gross_position}, net position: {net_position} =====")
            print(f"===== RGLD: {market_prices[0]}, RFIN: {market_prices[1]}, INDX: {market_prices[2]} =====")
            print(f"===== redeem profit: {redeem_profit}, convert profit: {convert_profit} =====")
            
            # add to log file
            f.write(f"===== TICK: {tick} ======= \n")
            f.write(f"===== gross position: {gross_position}, net position: {net_position} =====\n")
            f.write(f"===== RGLD: {market_prices[0]}, RFIN: {market_prices[1]}, INDX: {market_prices[2]} =====\n")
            f.write(f"===== redeem profit: {redeem_profit}, convert profit: {convert_profit} =====\n")


            if gross_position < MAX_EXPOSURE_GROSS:
                # TODO: adjust order limit * # (order limit amount)
                # TODO: adjust range(#) - look at whether over or under utilize gross pos

                # ETF redemption
                order_range = int(CONVERTER_LIMIT / ORDER_LIMIT)
                
                if redeem_profit > SUPER_HI_PROFIT:
                    for i in range (order_range + 3):
                        sell_stocks_buy_etf()
                    use_lease()

                    print(f"=== profits: {redeem_profit}, quantity: {(order_range + 5) * ORDER_LIMIT}, action: sell stocks buy etf ===")
                    # add to log file 
                    f.write(f"=== profits: {redeem_profit}, quantity: {(order_range + 5) * ORDER_LIMIT}, action: sell stocks buy etf ===\n")
                    
                    sleep(SLEEP_TIME)
                    
                elif SUPER_HI_PROFIT > redeem_profit > HI_MIN_PROFIT:
                    for i in range (order_range + 2):
                        sell_stocks_buy_etf()
                    use_lease()
                    
                    print(f"=== profits: {redeem_profit}, quantity: {(order_range + 3) * ORDER_LIMIT}, action: sell stocks buy etf ===")
                    # add to log file 
                    f.write(f"=== profits: {redeem_profit}, quantity: {(order_range + 3) * ORDER_LIMIT}, action: sell stocks buy etf ===\n")
                    
                    sleep(SLEEP_TIME)
                    
                elif HI_MIN_PROFIT > redeem_profit > MIN_PROFIT:
                    for i in range (order_range):
                        sell_stocks_buy_etf()

                    use_lease()

                    print(f"=== profits: {redeem_profit}, quantity: {order_range * ORDER_LIMIT}, action: sell stocks buy etf ===")
                    # add to log file
                    f.write(f"=== profits: {redeem_profit}, quantity: {order_range * ORDER_LIMIT}, action: sell stocks buy etf ===\n")
                    
                    sleep(SLEEP_TIME)

            
                # ETF creation
                if convert_profit > SUPER_HI_PROFIT:
                    for i in range (order_range + 3):
                        buy_stocks_sell_etf()
                    use_lease()

                    print(f"=== profits: {convert_profit}, quantity: {(order_range + 5) * ORDER_LIMIT}, action: buy stocks sell etf ===")
                    # add to log file
                    f.write(f"=== profits: {convert_profit}, quantity: {(order_range + 5) * ORDER_LIMIT}, action: buy stocks sell etf ===\n")
                    
                    sleep(SLEEP_TIME)
                    
                elif SUPER_HI_PROFIT > convert_profit > HI_MIN_PROFIT:
                    for i in range(order_range + 2):
                        buy_stocks_sell_etf()
                    use_lease()

                    print(f"=== profits: {convert_profit}, quantity: {(order_range + 3) * ORDER_LIMIT}, action: buy stocks sell etf ===")
                    # add to log file
                    f.write(f"=== profits: {convert_profit}, quantity: {(order_range + 3) * ORDER_LIMIT}, action: buy stocks sell etf ===\n")
                    
                    sleep(SLEEP_TIME)
                        
                elif HI_MIN_PROFIT > convert_profit > MIN_PROFIT:
                    for i in range(order_range):
                        buy_stocks_sell_etf()
                    use_lease()

                    print(f"=== profits: {convert_profit}, quantity: {order_range * ORDER_LIMIT}, action: buy stocks sell etf ===")
                    # add to log file
                    f.write(f"=== profits: {convert_profit}, quantity: {order_range * ORDER_LIMIT}, action: buy stocks sell etf ===\n")
                    
                    sleep(SLEEP_TIME)
                
                
            if gross_position > 60000: 
                use_lease() 
                sleep(SLEEP_TIME)
                
                print(f"===== no trades, run lease to close position, position: {gross_position} =======")
                # add to log file 
                f.write(f"===== no trades, run lease to close position, position: {gross_position} =======")

############################################ STRATEGY 2: MOVING AVERAGE ############################################
def moving_average_strategy():

    LONG_MA = 35
    SHORT_MA = 5
    
    def get_history(ticker):
        payload = {'ticker': ticker}
        resp = s.get('http://localhost:9999/v1/securities/history', params=payload)
        if resp.ok:
            stock_history = resp.json()
            return stock_history

    def close_price(stock_history, ticker):
        stock_history = get_history(ticker)
        df = pd.DataFrame(stock_history)[['tick', 'close']]
        df_sorted = df.sort_values(by='tick', ascending=True)
        
        closing_price = df_sorted['close']

        return closing_price

    def get_sma(closing_price, ticker, length):
        stock_history = get_history(ticker)
        closing_price = close_price(stock_history, ticker) # CHANGE IF USE OPEN_PRICE
        sma = ta.sma(closing_price, length)
        return sma

    def get_momentum(ticker):
        stock_history = get_history(ticker)
        closing_price = close_price(stock_history, ticker)

        sma_short = get_sma(closing_price, ticker, SHORT_MA)
        sma_long = get_sma(closing_price, ticker, LONG_MA)

        sma_short_list = sma_short.to_list()
        sma_long_list = sma_long.to_list()

        momentum = ''
        
        if (sma_short_list[-1] > (sma_long_list[-1] + 0.1)):
            momentum = 'up'
        
        if ((sma_short_list[-1] + 0.1) < sma_long_list[-1]):
            momentum = 'down'
            
        return momentum


    def trade_stock(ticker):
        gross_position, net_position = get_position()
        momentum = get_momentum(ticker)
        
        if momentum == 'up' and (net_position + ORDER_LIMIT_2) <= MAX_NET_LIMIT:
            s.post('http://localhost:9999/v1/orders', params={
                'ticker': ticker,
                'type': 'MARKET',
                'quantity': ORDER_LIMIT_2,
                'action': 'BUY'
            })
            print(f"UP momentum, BUY {ticker}")

        elif momentum == 'down'and (net_position - ORDER_LIMIT_2) >= -MAX_NET_LIMIT:
            s.post('http://localhost:9999/v1/orders', params={
                'ticker': ticker,
                'type': 'MARKET',
                'quantity': ORDER_LIMIT_2,
                'action': 'SELL'
            })
            print(f"DOWN momentum, SELL {ticker}")

    while True:
        tick, status = get_tick()
        gross_position, net_position = get_position()
        stock_configs = [{"ticker": "RGLD", "fee": MARKET_ORDER_FEE, "order_type": "MARKET"}, 
                         {"ticker": "RFIN", "fee": MARKET_ORDER_FEE, "order_type": "MARKET"},
                         {"ticker": "INDX", "fee": ETF_ORDER_FEE, "order_type": "MARKET"}]
        
        if status != 'ACTIVE':
            print("Case Inactive")

        if 60 > tick > LONG_MA or tick > 290: 
            print(f"============= MA TICK {tick} =============")
            print(f"gross position: {gross_position}, net position: {net_position} =====")
            for config in stock_configs:
                ticker = config['ticker']
                stock_history = get_history(ticker) #keep updating the stock history
                
                stock = close_price(stock_history, ticker) #dataframe form
                
                trade_stock(ticker)
            
            sleep(SLEEP_TIME_2)
        

####################################### MULTIPROCESSING ###############################
if __name__ == '__main__':
    # Create process objects for each strategy
    process_etf = multiprocessing.Process(target=etf_arbitrage_strategy)
    #process_ma = multiprocessing.Process(target=moving_average_strategy)

    # Start processes
    process_etf.start()
    #process_ma.start()

    # Optionally, wait for both processes to finish
    process_etf.join()
    #process_ma.join()
