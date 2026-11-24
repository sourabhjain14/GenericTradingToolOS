"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import numpy as np
import pandas as pd
import logging
import time
from threading import Thread
#!pip install sourcedefender
#!pip install pyotp
import sourcedefender


from ACCOUNT_DETAIL import ZERODHA_USER_ID,ZERODHA_PASSWORD,ZERODHA_TOTP
from kiteext_pro import KiteExt
from kiteext_pro import KiteTicker

import globalvar

def create_kite():
    kite = KiteExt()
    kite.login_with_credentials(userid=ZERODHA_USER_ID,password=ZERODHA_PASSWORD,twofa=ZERODHA_TOTP)
    globalvar.g_kite=kite
    return



def get_order_for_symbol(brokerapi, symbol):
    order_book = brokerapi.orders()
    for order in order_book:
        order_id = order['order_id']
        order_symbol = order['tradingsymbol']
        status = order['status']
        if order_symbol == symbol:
            if status=='OPEN':
                return order
    return None


def get_position_for_symbol(brokerapi, symbol):
    positions = kite.positions()
    if positions is None:
        return None
    for position in positions['net']:
        p_symbol = position['tradingsymbol']
        p_quantity = int(position['quantity'])
        #print(p_symbol, p_quantity)
        if p_symbol==symbol:
            if p_quantity>0:
                return position
    return None


def cancel_order_using_symbol(symbol):
    try:
        brokerapi = globalvar.g_kite
    except Exception as e:
        print(e)
        return
    order_book = brokerapi.orders()
    for order in order_book:
        order_id = order['order_id'] #from placeorder return value
        order_symbol = order['tradingsymbol']
        order_status = order['status']
        variety = order['variety']
        #print(order_id, status)
        order_open = (order_status != 'COMPLETE') and (order_status != 'CANCELLED') and (order_status != 'REJECTED')
        if order_open and order_symbol==symbol:
            ret = brokerapi.cancel_order(variety=variety, order_id=order_id)
            print(f"Canceled order: {ret}")
            return



def BUY_LIMIT(kite=None, symbol = 'RELIANCE', quantity = 0, price = None, stoploss=None,
              exchange = '',  order_type='', product='', variety='', tag=''):
    #print("BUY order")
    if quantity  < 1:
        print("Invalid Limit Order, buy quantity is less than 1")
        return -1
    if price is None:
        order_type=kite.ORDER_TYPE_MARKET
        #print("Invalid Limit Order. Price is not available")
        #return -1
    else:
        order_type=kite.ORDER_TYPE_LIMIT
        
    

    #if exchange=="NSE":
    #    kite.EXCHANGE_NSE
    if exchange=="NSE":
        segment = kite.EXCHANGE_NFO
    elif exchange=="BSE":
        segment = kite.EXCHANGE_BFO
    #order_type=kite.ORDER_TYPE_LIMIT
    product=kite.PRODUCT_NRML
    variety=kite.VARIETY_REGULAR
    
    
    try:
        if price is None:
            order_id = kite.place_order(tradingsymbol=symbol,
                                exchange=segment,
                                transaction_type=kite.TRANSACTION_TYPE_BUY,
                                quantity=quantity,
                                order_type=order_type,
                                product=product,variety=variety, tag=tag)
        else:
            ##price=price-10
            order_id = kite.place_order(tradingsymbol=symbol,
                                exchange=segment,
                                transaction_type=kite.TRANSACTION_TYPE_BUY,
                                quantity=quantity,
                                order_type=order_type,
                                price=price,
                                product=product,variety=variety, tag=tag)
        #stoploss=stoploss,
        order_thread = Thread(target=modify_order,args=(order_id,))
        order_thread.start()
        
        print("Order placed. ID is: {}".format(order_id))
        return order_id
    except Exception as e:
        print("Order placement failed: {}".format(e))
        return None


def SELL_LIMIT(kite=None, symbol = 'RELIANCE', quantity = 0, price = None, stoploss=None,
              exchange = '',  order_type='', product='', variety='', tag='', short_flag=0):
    if kite is None:
        print("Error: kite object is None")
        return -1
    if quantity < 1:
        print("Error: Invalid Order, sell quantity is less than 1")
        return -1
    if price is None:
        order_type=kite.ORDER_TYPE_MARKET
        #print("Invalid Limit Order. Price is not available")
        #return -1
    else:
        order_type=kite.ORDER_TYPE_LIMIT
    
    #segment = kite.EXCHANGE_NFO
    if exchange=="NSE":
        segment = kite.EXCHANGE_NFO
    elif exchange=="BSE":
        segment = kite.EXCHANGE_BFO
    #order_type=kite.ORDER_TYPE_LIMIT
    product=kite.PRODUCT_NRML
    variety=kite.VARIETY_REGULAR



    try:
        cancel_order_using_symbol(symbol)
    except Exception as e:
        print('sell limit: cancel open order using symbol error: ',e)
    
    
    # checking if sell quantity is less or equal to open positions
    check_=True
    if short_flag==0:
        print("sent quantity:",quantity)
        check_=False
        positions = kite.positions()
        if positions is None:
            print("No position found")
            return None
        #print("positions:")
        #print(positions)
        #if len(positions)
        for position in positions['net']:
            p_symbol = position['tradingsymbol']
            p_quantity = int(position['quantity'])
            print(p_symbol, p_quantity)
            if p_symbol==symbol:
                if p_quantity>=quantity:
                    check_=True
                else:
                    quantity = p_quantity
                    check_=True        
            if check_==True: break
        print("order quantity:",quantity)

    
    try:
        if check_==True:
            if price is None:
                order_id = kite.place_order(tradingsymbol=symbol,
                                    exchange=segment,
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=quantity,
                                    order_type=order_type,
                                    product=product,variety=variety, tag=tag)
            else:
                order_id = kite.place_order(tradingsymbol=symbol,
                                    exchange=segment,
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=quantity,
                                    order_type=order_type,
                                    price=price,
                                    product=product,variety=variety,tag=tag)
            #stoploss=stoploss,
            order_thread = Thread(target=modify_order,args=(order_id,))
            order_thread.start()
            
            print("Order placed. ID is: {}".format(order_id))
            return order_id
        return None
    except Exception as e:
        print("Order placement failed: {}".format(e))
        return None
    


def BUY_OCO(kite=None, symbol = 'RELIANCE', quantity = 0, price = None, target=None, stoploss=None, exchange = '',  order_type='', product='', variety=''):
    try:
        gtt_order = kite.place_gtt(
            trigger_type=kite.GTT_TYPE_OCO,
            tradingsymbol=symbol,  # Example trading symbol
            exchange="NFO",  # Exchange #transaction_type=kite.TRANSACTION_TYPE_BUY,  # BUY or SELL #quantity=quantity,  # Quantity to buy/sell
            last_price=price,  # Price at which to place the order
            trigger_values=[stoploss, target],  # Target and stop loss trigger prices
            orders=[
                {
                    "transaction_type": kite.TRANSACTION_TYPE_SELL,
                    "quantity": quantity,
                    "price": stoploss,  # Stop loss price 
                    "order_type": kite.ORDER_TYPE_LIMIT,
                    "product": kite.PRODUCT_NRML
                },
                {
                    "transaction_type": kite.TRANSACTION_TYPE_SELL,
                    "quantity": quantity,
                    "price": target, # Target price
                    "order_type": kite.ORDER_TYPE_LIMIT,
                    "product": kite.PRODUCT_NRML
                }
            ]
        )
        print("GTT OCO order placed. ID is:", gtt_order["trigger_id"])
    except Exception as e:
        print("Order placement failed:", str(e))

#holdings = kite.holdings()
#positions = kite.positions()
#print(holdings)
#for ele in holdings:
#    print(ele['tradingsymbol'])
#print(positions)

#kite.place_order("ACC",price=1460,variety= kite.VARIETY_BO,exchange=kite.EXCHANGE_NSE,transaction_type=kite.TRANSACTION_TYPE_SELL,
#uantity=50,squareoff=20,stoploss=10,order_type=kite.ORDER_TYPE_LIMIT,product=kite.PRODUCT_BO, trailing_stoploss=1)
#zerodha.place_bracket_order(kite=kite, symbol='NIFTY2491925400CE', quantity = 25, price = 60.0, target=100.0, stoploss=55.0)
def place_bracket_order(kite=None, symbol=None, quantity = 0, 
                        price = None, target=None, stoploss=None, 
                        exchange = '',  order_type='', product='', 
                        variety=''):
    BUY_LIMIT(kite=kite, symbol=symbol, quantity=quantity, price=None, stoploss=None, exchange = '',  order_type='', product='', variety='')
    BUY_OCO(kite=kite, symbol=symbol, quantity=quantity, price=price, target=target, stoploss=stoploss, exchange = '',  order_type='', product='', variety='')

def cancel_last_order(kite):
    # Fetch all orders
    order_list = kite.orders()
    print(order_list[-1])
    order_id = order_list[-1]['order_id']
    order_status = order_list[-1]['status']
    
    variety=kite.VARIETY_REGULAR
    
    if order_status == 'OPEN':
        cancel_ret = kite.cancel_order(variety=variety, order_id=order_id)
        

def get_order_trade(order_id):
    try:
        brokerapi = globalvar.g_kite
    except Exception as e:
        print(e)
        return None
    trades = brokerapi.order_trades(order_id)
    print("get_order_trade:", trades)
    if len(trades)>0:
        return trades[0]
    return None


def modify_order_OLD(order_id):
    try:
        kite = globalvar.g_kite
    except Exception as e:
        print(e)
        return None
    try:
        i=0
        while(i<10):
            time.sleep(2)
            i+=1
            order_list = kite.orders()
            for order in order_list:
                if order['order_id'] == order_id:
                    if order['status'] == 'OPEN':
                        symbol = order['tradingsymbol']
                        variety = order['variety']
                        dir = order['transaction_type']
                        price = order['price']
                        if dir=='BUY': best_price = price + 0.05
                        elif dir=='SELL': best_price = price - 0.05
                        order_id = kite.modify_order(variety=variety, order_id=order_id, price=best_price)
                    else:
                        return order_id
        return order_id
    except:
        return None


def modify_order(order_id):
    print("IN MODIFY ORDER")
    try:
        kite = globalvar.g_kite
    except Exception as e:
        print(e)
        return None
    
    #variety=kite.VARIETY_REGULAR
    try:
        i=0
        while(i<10):
            time.sleep(3)
            i+=1
            order = kite.order_history(order_id)[-1]
            print('modify order: ', order)
            order_status = order['status']
            order_open = (order_status != 'COMPLETE') and (order_status != 'CANCELLED') and (order_status != 'REJECTED')
            print('modify order open: ', order_open)
            if order_open:
                symbol = order['tradingsymbol']
                variety = order['variety']
                dir = order['transaction_type']
                price = order['price']
                exchange = order['exchange']
                
                qsymbol = exchange+":"+symbol
                quote = kite.quote(qsymbol)
                v = quote[qsymbol]
                ltp = v['last_price']
                #bid = v["depth"]["buy"][0]["price"]
                #ask = v["depth"]["sell"][0]["price"]
                try:
                    bid = v["depth"]["buy"][0]["price"]
                except:
                    bid = ltp
                try:
                    ask = v["depth"]["sell"][0]["price"]
                except:
                    ask = ltp
                
                if dir=='BUY': best_price =  ask
                elif dir=='SELL': best_price = bid
                ##best_price=best_price-10
                print("modifying order for ", symbol, ' having price ', price, ' with new price ', best_price)
                order_id = kite.modify_order(variety=variety, order_id=order_id, price=best_price)
            else:
                return order_id
        return order_id
    except Exception as e:
        print("zerodha modfiy order error:",e)
        return order_id
   

def cancel_all_orders():
    try:
        brokerapi = globalvar.g_kite
    except Exception as e:
        print(e)
        return
    order_book = brokerapi.orders()
    for order in order_book:
        order_id = order['order_id'] #from placeorder return value
        status = order['status']
        variety = order['variety']
        print(order_id, status)
        if status=='OPEN':
            ret = brokerapi.cancel_order(variety=variety, order_id=order_id)
            print(f"Canceled order: {ret}")


def liquidate(kite, tag, limit=0):
    try:
        print("---------------------------------orders-------------------------------------")
        # Fetch open orders
        orders = kite.orders()
        #print(orders)
        cancel_all_orders()
        # Fetch trades
        #trades = kite.trades()
        #print(trades)

        print("---------------------------------positions-------------------------------------")
        # Fetch positions
        positions = kite.positions()
        #print(positions)

        print("---------------------------------magic orders-------------------------------------")
        magic_positions_norenordno=[]
        magic_positions_dict = {}
        for order in orders:
            if 'tag' in order.keys():
                if order['tag']==tag:
                    oid = order['order_id']
                    qty = int(order['filled_quantity'])
                    sym = order['tradingsymbol']
                    trantype = order['transaction_type']
                    if sym not in magic_positions_dict.keys():
                        if trantype=='BUY':
                            magic_positions_dict[sym] = qty
                        elif trantype=='SELL':
                            magic_positions_dict[sym] = -qty
                    else:
                        if trantype=='BUY':
                            magic_positions_dict[sym] += qty
                        elif trantype=='SELL':
                            magic_positions_dict[sym] -= qty
                #magic_positions_norenordno.append(oid)
        print(magic_positions_dict)

        print("---------------------------------liquidating open positions-------------------------------------")
        # Loop through open positions and close those with the specified tag
        for position in positions['net']:
            check_=False
            symbol = position['tradingsymbol']
            quantity = int(position['quantity'])
            #last_price = round(position['last_price']-0.05,2)
            print(symbol, quantity)
            if symbol in magic_positions_dict.keys():
                if magic_positions_dict[symbol]>0 and quantity>0:
                    check_=True
            if check_==True:
                print("check_",symbol, quantity)
                
                dir = 'BUY' if quantity>0 else 'SELL'
                exchange = position['exchange']
                qsymbol = exchange+":"+symbol
                quote = kite.quote(qsymbol)
                v = quote[qsymbol]
                ltp = v['last_price']
                try:
                    bid = v["depth"]["buy"][0]["price"]
                except:
                    bid = ltp
                try:
                    ask = v["depth"]["sell"][0]["price"]
                except:
                    ask = ltp
                if dir=='BUY': last_price =  ask
                elif dir=='SELL': last_price = bid
                
                order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    exchange=position['exchange'],
                    tradingsymbol=position['tradingsymbol'],
                    transaction_type=kite.TRANSACTION_TYPE_SELL if position['quantity'] > 0 else kite.TRANSACTION_TYPE_BUY,
                    quantity=abs(position['quantity']),
                    order_type=kite.ORDER_TYPE_MARKET if limit==0 else kite.ORDER_TYPE_LIMIT,
                    product=kite.PRODUCT_NRML,
                    price=last_price,
                    tag=tag
                )
                print(f"Closed position: {position['tradingsymbol']} with order ID: {order_id}")
        #print("Completed closing positions with the specified tag.")
    except Exception as e:
        print(f"Error: {e}")






#ret = zerodha.get_margin(kite, symbol, "NSE", 25, 60.25)
def get_margin(symbol, exchange, quantity, price):   
    kite = globalvar.g_kite
    if exchange=="NSE":
        segment = "NFO"
    elif exchange=="BSE":
        segment = "BFO"
    order = {"exchange": segment,"tradingsymbol": symbol,"transaction_type": "SELL",
             "variety": "regular","product": "NRML","order_type":"MARKET",
             "quantity": quantity,"price":price}
    order_params = [order]
    try:
        margin_details = kite.order_margins(order_params)
        print(margin_details)
        margin = margin_details[0]['span'] + margin_details[0]['exposure']
        margin = round(margin,2)
        return margin
    except Exception as e:
        return 0

        

#from kitetick import kws_callbacks
#from kiteconnect import KiteTicker
def on_ticks(ws, ticks):
    # Callback to receive ticks.
    #global g_tick
    globalvar.g_tick = ticks
    #print(ticks)
    #logging.debug("Ticks: {}".format(ticks))
    
def on_connect(ws, response):
    token_list = globalvar.g_token_list
    print("kite ticker connect: ",token_list)
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe(token_list)
    #ws.set_mode(ws.MODE_FULL, token_list)
    ws.set_mode(ws.MODE_FULL, token_list)

def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()
    
def kws_callbacks(kws):    
    # Assign the callbacks.
    #global kws_ins_token_list
    #kws_ins_token_list = ins_token_list
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close

def create_stream(instrument_token_list):        
    globalvar.g_token_list += instrument_token_list
    #globalvar.g_token_list = instrument_token_list
    print("in create stream: ",globalvar.g_token_list)
    KEY = globalvar.g_kite.api_key
    access_token = globalvar.g_kite.access_token
    kws = KiteTicker(KEY, access_token)
    kws_callbacks(kws)#, [x for x in instrument_token_list])
    kws.connect(threaded=True)
    print("in create stream: ", kws.is_connected())
    globalvar.g_kiteticker = kws


def add_stream(instrument_token_list):
    globalvar.g_token_list += instrument_token_list
    globalvar.g_token_list = list(np.unique(globalvar.g_token_list))
    ws = globalvar.g_kiteticker
    ws.subscribe(instrument_token_list)
    #ws.set_mode(ws.MODE_FULL, instrument_token_list)


def get_account_info():
    try:
        brokerapi = globalvar.g_kite
        # Get account balance
        margins = brokerapi.margins()
        print("margins: ",margins)
        equity_balance = margins['equity']['available']['live_balance']
        #commodity_balance = margins['commodity']['available']['live_balance']
    
        # Get open positions
        positions = brokerapi.positions()
        open_positions = positions['net']
        #print("open_positions: ",open_positions)

        dfac = pd.DataFrame(open_positions)
        if len(open_positions)>0: dfac = dfac[dfac['quantity']!=0]
        #print("dfac:",dfac)
        print(equity_balance, dfac)
        #dfacshow = dfac[['tradingsymbol','quantity','average_price','last_price']]
        #display(dfacshow)
        #equity_balance_w.value = str(equity_balance)
        #positions_w.value = str(dfacshow)
        
    #account_vbox = VBox([equity_balance_w, positions_w])
    except Exception as e:
        #print("zerodha get account info error: ",e)
        return None, None
        #account_vbox = VBox([])
    return equity_balance, dfac#show#account_vbox
#END