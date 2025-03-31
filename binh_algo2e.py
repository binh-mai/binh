import signal
import requests
from operator import itemgetter
from time import sleep
import sys
import os
import json


class ApiException(Exception):
    pass

s = requests.Session()
API_key = 'L7F4EJ9X'  # TODO: change API_key
s.headers.update({'X-API-key': API_key})

################################# CONSTANTS ############################################
# if the overlimit fine is huge, pls help me reduce the gross_limit. thanks Izora <3

ORDER_SIZE = 2000
GROSS_LIMIT = 22000 # TODO:adjust between 19000 - 23000 (if too much fine)
SLEEP_TIME= 0.4

################################# HELPER FUNCTIONS ############################################
def get_tick():
    resp = s.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick'], case['status']
    raise ApiException('Authorization error. Please check API key.')


def get_bid_ask(ticker):
    payload = {'ticker': ticker}
    resp = s.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        best_bid_price = 0
        best_ask_price = 0
        if len(book['bids']) > 0:
            best_bid_price = book['bids'][0]['price']
        if len(book['asks']) > 0:
            best_ask_price = book['asks'][0]['price']
        return best_bid_price, best_ask_price
    raise ApiException('Authorization error. Please check API key.')
    

def get_position():
    resp = s.get('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        gross_position = abs(book[0]['position']) + abs(book[1]['position']) + abs(book[2]['position'])
        net_position = book[0]['position'] + book[1]['position']+ book[2]['position'] # net position is 2 stocks = 1 ETF
        return gross_position, net_position
    

def get_gross_position(ticker): # GROSS POSITION
    resp = s.get('http://localhost:9999/v1/securities')
    if resp.ok:
        securities = resp.json()
        for stock in securities:
            if stock['ticker'] == ticker:
                return int(stock['position'])  # Convert position to integer
        return 0  # Return 0 if the ticker is not found
    raise ApiException("Could not fetch positions.")


def get_open_orders(ticker):
    resp = s.get('http://localhost:9999/v1/orders')
    if resp.ok:
        orders = resp.json()
        # Filter orders to include only those with status 'OPEN'
        open_orders = [order for order in orders if order.get('status') == 'OPEN']
        
        return open_orders
    raise ApiException('Could not fetch active orders.')


def cancel_order(order_id):
    s.delete('http://localhost:9999/v1/orders/' + str(order_id))


def close_bad_orders(ticker):
    open_orders = get_open_orders(ticker)
    
    for order in open_orders:
        order_timestamp = order['tick']
        action = order['action']
        order_id = order['order_id']
        quantity_filled = order['quantity_filled']
        quantity = order['quantity']
        current_time, status = get_tick()  # Use tick as a proxy for time
        
        order_size = quantity - quantity_filled
        
        if current_time - order_timestamp > 2: # and quantity_filled == 0
            cancel_order(order_id)
  

# CLOSE POSITION WHERE LONG/SHORT POSITION IS TOO BIG
def too_much_position(ticker):
    gross_position = get_gross_position(ticker)
    best_bid_price, best_ask_price = get_bid_ask(ticker)

    # too large
    if gross_position >= 14999:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': 5000,
            'action': 'SELL'})
    
    if gross_position <= -14999:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': 5000,
            'action': 'BUY'})
            
    # large but not too large
    elif 9999 <= gross_position < 14999:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': 3500,
            'action': 'SELL'})
    
    elif -14999 < gross_position <= -9999:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': 3500,
            'action': 'BUY'})
            
    # 1000 but not too large
    elif 4999 <= gross_position < 9999:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': 2500,
            'price': best_ask_price,
            'action': 'SELL'})
    
    elif -9999 <= gross_position <= -4999:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': 2500,
            'price': best_bid_price,
            'action': 'BUY'})
            
    elif 2999 <= gross_position < 4999:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': 2000,
            'price': best_ask_price,
            'action': 'SELL'})
    
    elif -4999 <= gross_position <= -2999:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': 2000,
            'price': best_bid_price,
            'action': 'BUY'})


def trade_stock(ticker, order_type):
    gross_position, net_position = get_position()
    best_bid_price, best_ask_price = get_bid_ask(ticker)

    if (gross_position + ORDER_SIZE * 2) <= GROSS_LIMIT:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_bid_price - 0.01,
            'action': 'BUY'
        })

        # buy order 2 with less competitive price
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_bid_price - 0.03,
            'action': 'BUY'
        })
        
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_ask_price + 0.01,
            'action': 'SELL'
        })

        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_ask_price + 0.03,
            'action': 'SELL'
        })

        sleep(SLEEP_TIME)

    if (gross_position + ORDER_SIZE * 4) <= GROSS_LIMIT:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_bid_price - 0.01,
            'action': 'BUY'
        })

        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_ask_price + 0.01,
            'action': 'SELL'
        })

        # s.post('http://localhost:9999/v1/orders', params={
        #     'ticker': ticker,
        #     'type': order_type,
        #     'quantity': ORDER_SIZE,
        #     'price': best_bid_price - 0.02,
        #     'action': 'BUY'
        # })
        
        # s.post('http://localhost:9999/v1/orders', params={
        #     'ticker': ticker,
        #     'type': order_type,
        #     'quantity': ORDER_SIZE,
        #     'price': best_ask_price + 0.02,
        #     'action': 'SELL'
        # })
    if (gross_position + ORDER_SIZE * 5) <= GROSS_LIMIT:
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_bid_price + 0.01,
            'action': 'BUY'
        })

        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_bid_price - 0.04,
            'action': 'BUY'
        })

        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_ask_price - 0.01,
            'action': 'SELL'
        })

        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': order_type,
            'quantity': ORDER_SIZE,
            'price': best_ask_price + 0.04,
            'action': 'SELL'
        })

    #sleep(SLEEP_TIME)
        

################################# CLOSE ALL POSITIONS CODE #################################
def buy(volume, ticker):
    order = volume/ORDER_SIZE
    for i in range(round(order)):
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': ORDER_SIZE,
            'action': 'BUY'})
    
    if order != round(order):
        size = (order - round(order)) * ORDER_SIZE
        s.post('http://localhost:9999/v1/orders', params={
                'ticker': ticker,
                'type': 'MARKET',
                'quantity': size,
                'action': 'BUY'})
        
def sell(volume, ticker):
    order = volume/ORDER_SIZE
    for i in range(round(order)):
        s.post('http://localhost:9999/v1/orders', params={
            'ticker': ticker,
            'type': 'MARKET',
            'quantity': ORDER_SIZE,
            'action': 'SELL'})
    
    if order != round(volume/ORDER_SIZE):
        size = (order - round(order)) * ORDER_SIZE
        s.post('http://localhost:9999/v1/orders', params={
                'ticker': ticker,
                'type': 'MARKET',
                'quantity': size,
                'action': 'SELL'})

def close_all_position(ticker):
    current_position = get_gross_position(ticker)
    if current_position > 0:
        sell(current_position, ticker)
    elif current_position < 0:
        buy(abs(current_position), ticker)

def adjust_spread(ticker):
    #best_bid,best_ask = get_bid_ask(ticker)
    #spread = abs(best_bid - best_ask)

    if ticker =='RY':
        min_spread = 0.019
    
    elif ticker == 'CNR':
        min_spread = 0.032
    
    elif ticker == 'AC':
        min_spread = 0.03

    return min_spread

def trade_highest_stock(stock_configs):
        profits = {}

        for stock in stock_configs:
            ticker = stock['ticker']
            best_bid,best_ask = get_bid_ask(ticker)
            fee = stock['fee']
            profit = best_ask - best_bid - fee
            # min_spread = adjust_spread(ticker)

            profits[ticker] = profit

        # Find the stock ticker with the highest profit
        best_ticker = max(profits, key=profits.get)
        best_profit = profits[best_ticker]
        print(f"Highest profit is {best_profit} for {best_ticker}")

        min_spread = adjust_spread(best_ticker)
        
        if best_profit > min_spread:
            trade_stock(best_ticker, 'LIMIT')

###################################### MAIN LOGIC ###############################################
def main():
    stock_configs = [{"ticker": "RY", "fee": 0.0034, "order_type": "LIMIT"},
                {"ticker": "CNR", "fee": -0.005, "order_type": "LIMIT"},
                {"ticker": "AC", "fee": -0.0026, "order_type": "LIMIT"}]
    
    while True:
        tick, status = get_tick()

        if status !='ACTIVE': 
            print("Case inactive")
            sleep(1)

        elif status =='ACTIVE': 
            gross_position, net_position = get_position()

            print(f"===== TICK {tick}, gross position:{gross_position},net position:{net_position} =======")

            trade_highest_stock(stock_configs)

            # close_bad_orders(TICKER)
            # too_much_position(TICKER)
            # if current_position + ORDER_SIZE<= GROSS_LIMIT:
            #     trade_stock(TICKER, ORDER_TYPE, min_spread, FEE)
            
            # print(f"TICK:{tick} Current position:{current_position}")
            
            # sleep(SLEEP_TIME)
            close_bad_orders('CNR')
            close_bad_orders('RY')
            close_bad_orders('AC')

            too_much_position('CNR')
            too_much_position('RY')
            too_much_position('AC')
        
            if tick == 299:
                for stock in stock_configs:
                    ticker=stock['ticker']
                    close_all_position(ticker)


if __name__ == "__main__":
    main()

    # stock_configs = [
    #  {"ticker": "CROW", "fee": -0.03, "order_type": "LIMIT", "min_spread": 0.1},
    #  {"ticker": "OWL", "fee": 0.03, "order_type": "LIMIT", "min_spread": 0.25},
    # {"ticker": "DOVE", "fee": -0.04, "order_type": "LIMIT", "min_spread": 0.1}
