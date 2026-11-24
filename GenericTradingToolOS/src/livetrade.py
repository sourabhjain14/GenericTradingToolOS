"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import math
import time
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from pandas.tseries.offsets import BDay
#import ast
#from enum import Enum
import pytz
from threading import Thread
import asyncio
import importlib
import copy
import glob
import traceback
import functools
import re
import gc
import concurrent.futures
from IPython.display import display
import psutil, os
import sys
#import objgraph
#from collections import Counter
#from collections import defaultdict


#from termcolor import colored

#from account import API_KEY, ACCOUNT_ID, REFRESH_TOKEN
#from account import get_access_token

from initialize import g_tick_dict, g_param, g_security_dict
from initialize import g_streamer_connection
#from initialize import g_bar_dict
import globalvar

#import plotly.graph_objects as go 
#import matplotlib.pyplot as plt
#pip install https://github.com/matplotlib/mpl_finance/archive/master.zip
#from mpl_finance import candlestick_ohlc
#import matplotlib.dates as mdates
#from matplotlib.ticker import FuncFormatter
#from matplotlib.ticker import Formatter
#from matplotlib.dates import bytespdate2num, num2date
import matplotlib
#from matplotlib.widgets import Slider
#matplotlib.use('Qt4Agg')
#from plotly import __version__
#print (__version__) # requires version >= 1.9.0
#from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#import plotly.graph_objs as go


import datahandler
importlib.reload(datahandler)
#from datahandler import get_backdata
from datahandler import create_candle#, update_candles
#from datahandler import get_backdata_index_zerodha#(index, param, candles_dict, timeframe):
#from datahandler import check_strike_filter

import strategylib
#importlib.reload(strategylib)
from strategylib import run_live, run_backtest_OHLC_symbol#, create_signal_portfolio

from ordermanager import place_buy, place_sell

#import plotting
#from plotting import plot_backtest_charts

from techlib import calc_atr

from initialize import SUMMARYPATH, ANALYSISPATH, PLOTPATH

#import widget_lib 
from widget_lib import item_set_value
from widget_lib import add_global_trade_item_row


import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
import json



from strategy.eventmanager import add_sell_order
from strategy.eventmanager import build_trade_table
from strategy.eventmanager import calc_runtime_summary, update_security, update_signal_list

import zerodha
import finvasia



def on_close_trade_button_clicked_thread(b, candle, security, param, symbol, portfolio, portfolio_dict):
    add_sell_order(candle, security, param, 0, ":Manual Close", symbol, portfolio)
    order_placement(param, portfolio_dict)



def initialize_symbol_portfolio(portfolio_dict, portfolio, symbol):
    portfolio_dict[portfolio][symbol] = {}
    security = portfolio_dict[portfolio][symbol]
    security['price'] = 0.0        
    security['index'] = -1
    security['trade_in'] = 0
    security['inTrade'] = 0
    security['intradecount'] = 0
    security['position'] = 0
    security['tradeposition'] = 0
    security['entryprice'] = 0.0
    security['exitprice'] = 0.0
    security['cumPnL'] = 0.0
    
    security['holdingvalue'] = 0.0
    security['averageprice'] = 0.0
    
    
    security['tradeprice'] = 0.0
    security['stoplossprice'] = 0.0
    security['takeprofitprice'] = 0.0
    security['takeprofitprice2'] = 0.0
    security['TSLPrice'] = 0.0
    security['signal'] = []
    
    security['liveentryprice'] = 0.0
    security['liveexitprice'] = 0.0
    security['livecumPnL'] = 0.0
    
    security['long_signal_fired'] = 0
    security['close_long_signal_fired'] = 0
    security['short_signal_fired'] = 0
    security['close_short_signal_fired'] = 0
    
    security['trade_in_time'] = 0
    security['trade_today'] = 0
    security['available_capital'] = 0#param['account_capital']  
    
    security['runningpnl'] = 0.0
    security['backdata'] = []
    security['totalpnl'] = 0.0
    
    
    security['option'] = {}
    security['collateral'] = {}
    
    security['optionATM'] = []
    security['optionITMcall'] = []
    security['optionOTMcall'] = []
    security['optionITMput'] = []
    security['optionOTMput'] = []
    
    security['martingale'] = 0
    security['X2count'] = 0





def extract_initial_letters(s):
    match = re.match(r'^[A-Za-z]+', s)
    if match:
        return match.group(0)
    return ''



def get_mtf_data(param, mtfcandles_dict, symbol, interval):
    #print("PRE mtfcandles_dict: ",symbol, mtfcandles_dict)
    
    if symbol not in mtfcandles_dict.keys():
        mtfcandles_dict[symbol] = {}
    mtfcandles = mtfcandles_dict[symbol]
    
    
    if interval not in mtfcandles.keys():
        mtfcandles[interval] = {}
    candles = mtfcandles[interval]
    
    
    if len(candles)>0: return 
    #else:
    #    mtfcandles[interval] = {}
    #    candles = mtfcandles[interval]
    temp_candles = {}
    #candles = 
    datahandler.get_backdata_symbol(symbol, temp_candles, param, interval=interval, numDays=10, instrument_type="EQ")
    mtfcandles_dict[symbol][interval] = temp_candles[symbol]
    #print(symbol)
    #print(symbol,candles)
    #print("POST mtfcandles_dict: ",symbol, mtfcandles_dict)
    
    print("IN MTF feature:",symbol, datetime.now())
    calc_mtf_feature(param, mtfcandles_dict, symbol, interval)
    print("OUT MTF feature:",symbol, datetime.now())
    

def calc_mtf_feature(param, mtfcandles_dict, symbol, interval):
    mtfcandles = mtfcandles_dict[symbol]
    candles = mtfcandles[interval]
    #indices = param['instrument_index_list'][0]
    #atr_timeframe = str(param["index_atr_timeframe_hour"])+"H"
    #indices_candles =  globalvar.g_market_dict["INDEX"][indices][atr_timeframe] #candles_dict[indices]
    indices_index = len(candles) - 1
    atr_period = param['index_atr_period']
    for i in range(len(candles)):
        #print(i)
        #print(indices_candles[i])
        candles[i]['atr'] = calc_atr(candles, i, atr_period)
        #print(indices_candles[i])
        iatr = candles[i]['atr']
        #print(iatr)
        inum = param["index_atr_timeframe_hour"]*60
        itflower = inum / param['index_atr_lowertimeframe']
        iatrlower = iatr / itflower
        brick_size = iatrlower
        candles[i]['brick_size'] = brick_size



def build_scanner_data_symbol(symbol, portfolio, strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict):
    dbg=False
    if symbol not in candles_dict.keys():
        if symbol not in globalvar.g_instrument_dict.keys():
            globalvar.g_instrument_dict[symbol] = {}
        globalvar.g_instrument_dict[symbol]['backdata_ready'] = False
            #globalvar.g_instrument_dict[symbol]['underlying'] = extract_initial_letters(symbol)
        
        

        if dbg:print("IN getbackdata:",symbol, datetime.now())
        ret = datahandler.get_backdata_symbol(symbol, candles_dict, param)
        if dbg:print("OUT getbackdata:",symbol, datetime.now())
        
        if ret is None: return 0
        
        #initialize_symbol_portfolio(portfolio_dict, portfolio, symbol)
        renko_dict[symbol] = []
        mtfcandles_dict[symbol] = {}
        
        for candle_ in candles_dict[symbol]:
            candle_ = create_candle(candle_)


        if param['renko_brick_type']=='Calculation':
            #minute day 3minute 5minute 10minute 15minute 30minute 60minute
            underlying = globalvar.g_instrument_dict[symbol]['name']
            underlying_interval = "day"
            
            if dbg:print("IN MTF getbackdata:",underlying, datetime.now())
            get_mtf_data(param, mtfcandles_dict, underlying, underlying_interval)
            if dbg:print("OUT MTF getbackdata:",underlying, datetime.now())
    
            #print("IN MTF feature:",underlying, datetime.now())
            #calc_mtf_feature(param, mtfcandles_dict, underlying, underlying_interval)
            #print("OUT MTF feature:",underlying, datetime.now())
        
        
        if dbg:print("IN backtest:",symbol, datetime.now())
        run_backtest_OHLC_symbol(symbol, strategyClass_dict, portfolio_dict, portfolio, candles_dict, param, mtfcandles_dict, 0, renko_dict)
        if dbg:print("OUT backtest:",symbol, datetime.now())
        globalvar.g_instrument_dict[symbol]['backdata_ready'] = True
        #print("renko:",renko_dict[symbol])
        #build_trade_table(param)
        #write_trade_table_file(param)
    return 0


def build_scanner_data_old(strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict):
    portfolio = param['portfolio_strategy']#list(portfolio_dict.keys())[0]
    if 'scanned_option_top_gainer' in param.keys():
        opt1_list = param['scanned_option_top_gainer']
        #print("opt_list: ",opt_list)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(build_scanner_data_symbol, newsymbol, portfolio, strategyClass_dict, 
                                       portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict) for newsymbol in opt1_list]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        
        #for newsymbol in opt_list:
        #    build_scanner_data_thread = Thread(target=build_scanner_data_symbol,args=(newsymbol, portfolio, strategyClass_dict, 
        #                                                                              portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict,))
        #    build_scanner_data_thread.start()
        #    #build_scanner_data_symbol(newsymbol, portfolio, strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict)
    
    if 'scanned_option_top_loser' in param.keys():
        opt2_list = param['scanned_option_top_loser']
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(build_scanner_data_symbol, newsymbol, portfolio, strategyClass_dict, 
                                       portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict) for newsymbol in opt2_list]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        #for newsymbol in opt_list: 
        #    build_scanner_data_thread = Thread(target=build_scanner_data_symbol,args=(newsymbol, portfolio, strategyClass_dict, 
        #                                                                              portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict,))
        #    build_scanner_data_thread.start()
        #    #build_scanner_data_symbol(newsymbol, portfolio, strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict)         
    return


def build_scanner_data(strategyClass_dict, portfolio_dict, param,candles_dict, mtfcandles_dict, renko_dict):
    portfolio = param['portfolio_strategy']

    for symbol in param['scanned_option_top_gainer']:
        if symbol not in portfolio_dict[portfolio].keys():
            #globalvar.g_instrument_dict[symbol]['backdata_ready'] = False
            initialize_symbol_portfolio(portfolio_dict, portfolio, symbol)
    
    for symbol in param['scanned_option_top_loser']:
        if symbol not in portfolio_dict[portfolio].keys():
            #globalvar.g_instrument_dict[symbol]['backdata_ready'] = False
            initialize_symbol_portfolio(portfolio_dict, portfolio, symbol)
    
    executor  = concurrent.futures.ThreadPoolExecutor()

    def _submit(syms):
        return [executor.submit(build_scanner_data_symbol,
                               sym, portfolio, strategyClass_dict,
                               portfolio_dict, param,
                               candles_dict, mtfcandles_dict, renko_dict)
                for sym in syms]

    futures = []
    if 'scanned_option_top_gainer' in param:
        futures += _submit(param['scanned_option_top_gainer'])
    if 'scanned_option_top_loser' in param:
        futures += _submit(param['scanned_option_top_loser'])

    # Do NOT let the `with` close the pool here
    return futures, executor   # caller decides when to wait/shutdown

'''
def copytick(instrument_token_list):
    #instrument_token_list = param['instrument_token_list']
    if globalvar.g_copytick==True:
        print("adding stream with: ", instrument_token_list)
        zerodha.add_stream(instrument_token_list)
    if globalvar.g_copytick==False:
        print("creating stream with: ", instrument_token_list)
        zerodha.create_stream(instrument_token_list)
        globalvar.g_copytick=True
        while(True):
            try:
                time.sleep(0.1)
                quote = globalvar.g_tick#.copy()
                #print("stream quote: ", quote)
                for q in quote:
                    token = q['instrument_token']
                    ltp = q['last_price']
                    if token not in globalvar.g_lastdata.keys():   globalvar.g_lastdata[token] = {}
                    globalvar.g_lastdata[token]['last_price'] = ltp
                #quote = globalvar.g_kite.quote(instrument_token_list)
                #print(quote)
                #for q,v in quote.items():
                #    token = v['instrument_token']
                #    ltp = v['last_price']
                #    #if (ltp<0.05):print(v)
                #    if token not in globalvar.g_lastdata.keys():   globalvar.g_lastdata[token] = {}
                #    globalvar.g_lastdata[token]['last_price'] = ltp
            except:
                if globalvar.g_kite==None:return
                continue
    return
'''


'''
def copytick(instrument_token_list):
    #instrument_token_list = param['instrument_token_list']
    if globalvar.g_copytick==False:
        globalvar.g_copytick=True
        while(globalvar.g_copytick):
            try:
                #quote = globalvar.g_tick.copy()
                time.sleep(1)
                instrument_token_list = [sub_dict['token'] for sub_dict in globalvar.g_instrument_dict.values()]
                quote = globalvar.g_kite.quote(instrument_token_list)
                #print("tick: ",quote)
                for q,v in quote.items():
                    token = v['instrument_token']
                    ltp = v['last_price']
                    try:
                        ltq = v["last_quantity"]
                    except:
                        ltq = 0
                    try:
                        bid = v["depth"]["buy"][0]["price"]
                    except:
                        bid = ltp
                    try:
                        ask = v["depth"]["sell"][0]["price"]
                    except:
                        ask = ltp
                        
                    #if (ltp<0.05):print(v)
                    if token not in globalvar.g_lastdata.keys():   globalvar.g_lastdata[token] = {}
                    globalvar.g_lastdata[token]['last_price'] = ltp
                    globalvar.g_lastdata[token]['last_quantity'] = ltq
                    globalvar.g_lastdata[token]['bid'] = bid
                    globalvar.g_lastdata[token]['ask'] = ask
            except:
                if globalvar.g_kite==None:return
                continue
    return
'''

def copytick(instrument_token_list):
    #instrument_token_list = param['instrument_token_list']
    #instrument_token_list = [sub_dict['token'] for sub_dict in globalvar.g_instrument_dict.values()]
    if globalvar.g_copytick==True:
        print("adding stream with: ", instrument_token_list)
        zerodha.add_stream(instrument_token_list)
    if globalvar.g_copytick==False:
        print("creating stream with: ", instrument_token_list)
        zerodha.create_stream(instrument_token_list)
        globalvar.g_copytick=True
        while(globalvar.g_copytick):
            try:
                if globalvar.g_kite==None:return
                #instrument_token_list = [sub_dict['token'] for sub_dict in globalvar.g_instrument_dict.values()]
                #gins = globalvar.g_token_list
                time.sleep(0.1)
                quote = globalvar.g_tick
                #instrument_token_list = [sub_dict['token'] for sub_dict in globalvar.g_instrument_dict.values()]
                #quote = globalvar.g_kite.quote(instrument_token_list)
                #print("tick: ",quote)
                for v in quote:
                    token = v['instrument_token']
                    ltp = v['last_price']
                    try:
                        ltq = v["last_traded_quantity"]
                    except:
                        ltq = 0
                    try:
                        bid = v["depth"]["buy"][0]["price"]
                    except:
                        bid = ltp
                    try:
                        ask = v["depth"]["sell"][0]["price"]
                    except:
                        ask = ltp
                        
                    #if (ltp<0.05):print(v)
                    if token not in globalvar.g_lastdata.keys():   globalvar.g_lastdata[token] = {}
                    globalvar.g_lastdata[token]['last_price'] = ltp
                    globalvar.g_lastdata[token]['last_quantity'] = ltq
                    globalvar.g_lastdata[token]['bid'] = bid
                    globalvar.g_lastdata[token]['ask'] = ask
            except:
                if globalvar.g_kite==None:return
                continue
    return

    

def candle_updater(candles_dict, param, out_live):
    inverted_token_dict = {}
    for k in list(globalvar.g_instrument_dict.keys()):
        v = globalvar.g_instrument_dict[k]
        if 'token' in v.keys():
            token = v['token']
            inverted_token_dict[token] = k
    #print("inverted_token_dict =",inverted_token_dict)
    
    ltp_dict = {}
    ltq_dict = {}
    bid_dict = {}
    ask_dict = {}
    for token in list(globalvar.g_lastdata.keys()):
        try:
            ins = inverted_token_dict[token]
            #ltp = globalvar.g_lastdata[token]['last_price']
            ltp_dict[ins] = globalvar.g_lastdata[token]['last_price']
            ltq_dict[ins] = globalvar.g_lastdata[token]['last_quantity']
            bid_dict[ins] = globalvar.g_lastdata[token]['bid']
            ask_dict[ins] = globalvar.g_lastdata[token]['ask']
        except Exception as e:
            pass
            #print(token, ': token quote inverted token dict error: ',inverted_token_dict,e)
   
    
    now = datetime.now()
    nowtz = now#.astimezone(tz)
    minute = nowtz.minute
    nowmn = nowtz.hour*60+nowtz.minute
    marketmn = nowmn# - 915
    current_date = now.date()

    #for symbol in instrument_symbol_list:
    candleskeylist = list(candles_dict.keys())
    for symbol in candleskeylist:
        candledate = candles_dict[symbol][-1]['datetime']
        candlemn = candledate.hour*60+candledate.minute
        
        previous_date = candledate.date()
        newDay = current_date != previous_date
        
        newcandle = (marketmn>candlemn) or newDay 
        
        if newcandle==True:
            candle = create_candle() # {'comment':''}
        else:
            candle=candles_dict[symbol][-1]

        #msg = symbol
        #msg = msg+" :quote: "+str(quote)
        #out_live.append_stdout(msg+'\n')
        
        try:
            ltp = ltp_dict[symbol]

            if ltp<0.01: ltp = candles_dict[symbol][-1]['close']
            
            if newcandle==True:
                candle['datetime'] = nowtz
                candle['open'] = ltp
                candle['high'] = ltp
                candle['low'] = ltp
                candle['close'] = ltp
                candle['volume'] = ltq_dict[symbol]
                candle['bid'] = bid_dict[symbol]
                candle['ask'] = ask_dict[symbol]
                candles_dict[symbol].append(candle)
                #print(candle)
            else:
                candle['high'] = max(candle['high'], ltp)
                candle['low'] = min(candle['low'], ltp)
                candle['close'] = ltp
                candle['volume'] = candle['volume'] + ltq_dict[symbol]
                candle['bid'] = bid_dict[symbol]
                candle['ask'] = ask_dict[symbol]
        except:
            if newcandle==True:
                old_candle = candles_dict[symbol][-1]
                candle['datetime'] = nowtz
                candle['open'] = old_candle['close']
                candle['high'] = old_candle['close']
                candle['low'] = old_candle['close']
                candle['close'] = old_candle['close']
                candle['bid'] = old_candle['close'] if 'bid' not in old_candle.keys() else old_candle['bid']
                candle['ask'] = old_candle['close'] if 'ask' not in old_candle.keys() else old_candle['ask']
                candle['volume'] = 0
                candles_dict[symbol].append(candle)
            #continue
    return







def underlying_candle_updater(param, new_candle_update=False):
    now = datetime.now()
    '''
    ins_list = list(globalvar.g_underinstrument_dict.keys())
    instrument_token_dict = globalvar.g_param['fno_stock_token_dict']
    reversed_dict = {value: key for key, value in instrument_token_dict.items()}
    instrument_token_list= list(reversed_dict.keys())#[]
    '''
    candles_dict = globalvar.g_underinstrument_dict
    
    inverted_token_dict = {}
    instrument_token_dict = param['fno_stock_token_dict']
    #for k, v in instrument_token_dict.items():
    #    token = v['token']
    #    inverted_token_dict[token] = k
    inverted_token_dict = {value: key for key, value in instrument_token_dict.items()}
    #print("inverted_token_dict =",inverted_token_dict)
    
    ltp_dict = {}
    ltq_dict = {}
    bid_dict = {}
    ask_dict = {}
    for token in globalvar.g_lastdata.keys():
        try:
            ins = inverted_token_dict[token]
            #ltp = globalvar.g_lastdata[token]['last_price']
            ltp_dict[ins] = globalvar.g_lastdata[token]['last_price']
            ltq_dict[ins] = globalvar.g_lastdata[token]['last_quantity']
            bid_dict[ins] = globalvar.g_lastdata[token]['bid']
            ask_dict[ins] = globalvar.g_lastdata[token]['ask']
        except Exception as e:
            pass
            #print(token, ': token quote inverted token dict error: ',inverted_token_dict,e)
   
    
    
    nowtz = now#.astimezone(tz)
    minute = nowtz.minute
    nowmn = nowtz.hour*60+nowtz.minute
    marketmn = nowmn# - 915
    current_date = now.date()

    #for symbol in instrument_symbol_list:
    candleskeylist = list(candles_dict.keys())
    for symbol in candleskeylist:
        candledate = candles_dict[symbol][-1]['datetime']
        candlemn = candledate.hour*60+candledate.minute
        
        previous_date = candledate.date()
        newDay = current_date != previous_date
        
        newcandle = (marketmn>candlemn) or newDay 
        
        if newcandle==True:
            candle = create_candle() # {'comment':''}
        else:
            candle=candles_dict[symbol][-1]

        #msg = symbol
        #msg = msg+" :quote: "+str(quote)
        #out_live.append_stdout(msg+'\n')
        
        try:
            ltp = ltp_dict[symbol]

            if ltp<0.01: ltp = candles_dict[symbol][-1]['close']
            
            if newcandle==True:
                candle['datetime'] = nowtz
                candle['open'] = ltp
                candle['high'] = ltp
                candle['low'] = ltp
                candle['close'] = ltp
                candle['volume'] = ltq_dict[symbol]
                candle['bid'] = bid_dict[symbol]
                candle['ask'] = ask_dict[symbol]
                candles_dict[symbol].append(candle)
                #print(candle)
            else:
                candle['high'] = max(candle['high'], ltp)
                candle['low'] = min(candle['low'], ltp)
                candle['close'] = ltp
                candle['volume'] = candle['volume'] + ltq_dict[symbol]
                candle['bid'] = bid_dict[symbol]
                candle['ask'] = ask_dict[symbol]
        except:
            if newcandle==True:
                old_candle = candles_dict[symbol][-1]
                candle['datetime'] = nowtz
                candle['open'] = old_candle['close']
                candle['high'] = old_candle['close']
                candle['low'] = old_candle['close']
                candle['close'] = old_candle['close']
                candle['bid'] = old_candle['close'] if 'bid' not in old_candle.keys() else old_candle['bid']
                candle['ask'] = old_candle['close'] if 'ask' not in old_candle.keys() else old_candle['ask']
                candle['volume'] = 0
                candles_dict[symbol].append(candle)
            #continue
    return




def create_trade_table_new_prev(portfolio_dict, candles_dict, param, out_live):
    trade_type = "PAPER"
    if param["PLACE_ORDER"]:
        trade_type="LIVE"
    
    width = param['trade_table_width']
    scount=0
    counter = 0#globalvar.g_trade_table_counter# if param['trade_table_counter_start']==False else 0
    param['trade_table_counter_start']=True
    
    #siglen = len(globalvar.g_signal_dict[param['index_symbol']])
                
    trade_table = param['trade_table']
    signal_list = param['signal_list']

    #print("trade_table: ")
    #print(len(trade_table), len(param['trade_items']) , param['trade_table_width'])
    
    trade_items_height =  (len(param['trade_items']) / param['trade_table_width'])
    
    #trade_height = ((len(signal_list)//2) + 2)
    trade_height = (len(trade_table) + 2)
    
    if trade_height >= trade_items_height:
        for k in range(int(trade_items_height), int(trade_height)+1): add_global_trade_item_row(param)
        param['tradebox'].children = param['trade_items']

    
    for trade in trade_table:
        scount+=1
        symbol = trade['symbol']
        senp = trade['EntryPrice']
        sdten = trade['EntryDateTime'].strftime("%Y-%m-%d %H:%M:%S")
        spos = trade['position']
        shv = round(trade['holdingvalue'],2) if trade['TradeDirection']=='BUY' else trade['margin']
        sposlast = trade['remaining_position']
        
        if 'ExitPrice' in trade.keys():
            sexp = str(trade['ExitPrice'])
            if sposlast>0:
                sexp = sexp+"(M)"
        else:
            sexp = ""

        if 'ExitPrice2' in trade.keys():
            sexp = sexp +"(M)"+ str(trade['ExitPrice2'])
                
        if 'ExitDateTime2' in trade.keys():
            sdtex = trade['ExitDateTime2'].strftime("%Y-%m-%d %H:%M:%S")
        elif 'ExitDateTime' in trade.keys():
            sdtex = trade['ExitDateTime'].strftime("%Y-%m-%d %H:%M:%S")
        else:
            sdtex = ""
        
        #spnl = trade['PnL']
        candles_live = candles_dict[symbol]
        portfolio = trade['portfolio']
        security = portfolio_dict[portfolio][symbol]
        
        rbrick = round(security['brick_size'],2)
        rbrick_str = ''
        try:
            if param['renko_brick_type']=='Calculation':
                rbrick_str = str(round(security['atr_brick'],2)) + " / " + str(round(security['price_delta'],2)) + " / " + str(rbrick)
            else:
                rbrick_str = str(rbrick)
        except:
            rbrick_str = str(rbrick)
        
        close_price = candles_live[-1]['close']


        
        if 'lot_size' in security.keys():
            lot_size = security['lot_size']
        else:
            lot_size = param['lot']
        
        if (abs(sposlast)>0):
            if ('ExitPrice' not in trade.keys()):
                spnl_  = lot_size*sposlast*(close_price - senp)
            elif ('ExitPrice2' not in trade.keys()):
                spnl_  = trade['ExitPnL'] + lot_size*sposlast*(close_price - senp)
        else:
            if 'ExitPrice' in trade.keys():
                spnl_ = trade['ExitPnL']
                if 'ExitPrice2' in trade.keys():
                    spnl_ = spnl_ + trade['ExitPnL2']
            else:
                spnl_ = 0.0
        spnl = round(spnl_, 2)
        
        # trade modified
        trade['unrealized_pnl'] = spnl
            
        
        item_set_value(symbol, param['trade_items'], 0, scount, width)
        item_set_value(str(candles_live[-1]['close']), param['trade_items'], 1, scount, width)
        item_set_value(str(senp), param['trade_items'], 2, scount, width)
        item_set_value(str(sexp), param['trade_items'], 3, scount, width)
        
        squantity = spos * lot_size
        item_set_value(str(squantity), param['trade_items'], 4, scount, width)
        
        
        item_set_value(str(shv), param['trade_items'], 5, scount, width)
        
        item_set_value(str(spnl), param['trade_items'], 6, scount, width)

        
        #if True:#sposlast>0:
        #    if spnl>0:
        #        param['trade_items'][6+scount*width].style = {'background': 'green'}
        #    else:
        #        param['trade_items'][6+scount*width].style = {'background': 'red'}
                            
        
        item_set_value(sdten, param['trade_items'], 7, scount, width)
        item_set_value(sdtex, param['trade_items'], 8, scount, width)
        
        if (abs(sposlast)>0):item_set_value(rbrick_str, param['trade_items'], 9, scount, width)
        
        item_set_value(trade_type, param['trade_items'], 10, scount, width)
        
        try:
            if abs(sposlast)>0:
                wbutton = param['trade_items'][11+scount*width]
                wbutton.layout.display = 'flex'
                if spnl>0:
                    wbutton.style.button_color = 'green'
                else:
                    wbutton.style.button_color = 'red'
                if len(wbutton._click_handlers.callbacks) == 0:
                    wbutton.on_click(functools.partial(on_close_trade_button_clicked_thread, 
                                                       candle=candles_live[-1], security=security, 
                                                       param=param, symbol=symbol, portfolio=portfolio, portfolio_dict=portfolio_dict))
                #wbutton.disbaled=True
            else:
                wbutton = param['trade_items'][11+scount*width]
                wbutton.layout.display = 'flex'
                wbutton.disabled = True
                wbutton.style.button_color = 'gray'
        except Exception as e:    
            pass
            #traceback.print_exc()
            #out_live.append_stdout(str(e)+'\n')
    return
    



def idx(row, col, width):
    """row/col are 0-based, width = param['trade_table_width']"""
    return row * width + col




# ------------------------------------------------------------------
# 1. Initialise the table – run **once**
# ------------------------------------------------------------------
def create_global_trade_items(portfolio_dict, candles_dict, param):
    """
    Call this once after you have already created param['tradebox']
    (e.g. param['tradebox'] = widgets.Output(); hbox.children += (param['tradebox'],))
    """
    width  = param['trade_table_width']
    height = param['trade_table_height']

    # ---- pure data container -----------------------------------------
    param['trade_data'] = []          # list of dicts (no widgets)
    param['trade_items'] = None       # not needed any more

    # ---- clear the existing Output and write the empty skeleton -----
    with param['tradebox']:
        param['tradebox'].clear_output(wait=True)
        param['tradebox'].append_display_data(HTML(_render_skeleton(param)))

    # ---- Python callback for Close button ---------------------------
    def _close_handler(idx):
        trade = param['trade_data'][idx]
        on_close_trade_button_clicked_thread(
            candle=candles_dict[trade['symbol']][-1],
            security=portfolio_dict[trade['portfolio']][trade['symbol']],
            param=param,
            symbol=trade['symbol'],
            portfolio=trade['portfolio'],
            portfolio_dict=portfolio_dict
        )
    param['_close_handler'] = _close_handler

    # ---- inject JS bridge (event delegation) -------------------------
    param['tradebox'].append_display_data(HTML(_inject_js_bridge()))


# ------------------------------------------------------------------
# 2. HTML skeleton (header + empty rows)
# ------------------------------------------------------------------
def _render_skeleton(param):
    width = param['trade_table_width']
    rows  = param['trade_table_height'] + 2          # +2 buffer

    header = [
        "SYMBOL","LAST PRICE","ENTRY PRICE","EXIT PRICE","POSITION",
        "HOLDING","PNL","ENTRY TIME","EXIT TIME","FOS","TRADE TYPE","EXIT"
    ]

    html = "<style>"
    html += """
    .trade-table {font-family:Arial; border-collapse:collapse; width:100%;}
    .trade-table th,.trade-table td {border:1px solid #ddd; padding:4px; text-align:center;}
    .trade-table th {background:#f2f2f2;}
    .trade-table .pnl-pos {background:#d4edda; color:#155724;}
    .trade-table .pnl-neg {background:#f8d7da; color:#721c24;}
    .trade-table button {font-size:11px; padding:2px 6px;}
    """
    html += "</style>"

    html += "<table class='trade-table'>"
    html += "<tr>" + "".join(f"<th>{h}</th>" for h in header) + "</tr>"

    for r in range(1, rows):
        html += f"<tr data-idx='{r-1}'>"
        for c in range(width):
            if c == width - 1:                     # Close button column
                html += f'<td><button class="close-btn" data-idx="{r-1}">Close</button></td>'
            else:
                html += "<td></td>"
        html += "</tr>"
    html += "</table>"
    return html


# ------------------------------------------------------------------
# 3. JavaScript bridge – one listener for *all* Close buttons
# ------------------------------------------------------------------
def _inject_js_bridge():
    return """
    <script>
    function callPython(funcName, args) {
        // JupyterLab / Notebook kernel
        const kernel = (window.Jupyter && Jupyter.notebook) ? Jupyter.notebook.kernel : null;
        if (kernel) {
            kernel.execute(`${funcName}(${args.join(',')})`);
        }
    }

    document.addEventListener('click', function(e){
        if (e.target && e.target.classList.contains('close-btn')){
            const idx = e.target.getAttribute('data-idx');
            callPython('param["_close_handler"]', [idx]);
        }
    });
    </script>
    """


# ------------------------------------------------------------------
# 4. Fast cell update (tiny JS snippet)
# ------------------------------------------------------------------
def _set_cell(param, row, col, value, extra_class=""):
    js = f"""
    <script>
    const tr = document.querySelector('tr[data-idx="{row}"]');
    if (tr) {{
        const td = tr.children[{col}];
        td.innerText = `{value}`;
        td.className = `{extra_class}`;
    }}
    </script>
    """
    param['tradebox'].append_display_data(HTML(js))


# ------------------------------------------------------------------
# 5. Fill / refresh one logical row
# ------------------------------------------------------------------
def update_trade_row(portfolio_dict, candles_dict, param, trade, row_idx):
    width = param['trade_table_width']

    # ---- same calculations you already had -------------------------
    symbol   = trade['symbol']
    senp     = trade['EntryPrice']
    sdten    = trade['EntryDateTime'].strftime("%Y-%m-%d %H:%M:%S")
    spos     = trade['position']
    shv      = (round(trade['holdingvalue'],2)
                if trade['TradeDirection']=='BUY' else trade['margin'])
    sposlast = trade['remaining_position']

    # Exit price string
    sexp = ""
    if 'ExitPrice' in trade:
        sexp = str(trade['ExitPrice'])
        if sposlast > 0:
            sexp += "(M)"
    if 'ExitPrice2' in trade:
        sexp += "(M)" + str(trade['ExitPrice2'])

    sdtex = ""
    if 'ExitDateTime2' in trade:
        sdtex = trade['ExitDateTime2'].strftime("%Y-%m-%d %H:%M:%S")
    elif 'ExitDateTime' in trade:
        sdtex = trade['ExitDateTime'].strftime("%Y-%m-%d %H:%M:%S")

    candles_live = candles_dict[symbol]
    close_price  = candles_live[-1]['close']
    lot_size     = (portfolio_dict[trade['portfolio']][symbol]
                    .get('lot_size', param['lot']))

    # PnL
    if abs(sposlast) > 0:
        if 'ExitPrice' not in trade:
            spnl = lot_size * sposlast * (close_price - senp)
        else:
            spnl = trade['ExitPnL'] + lot_size * sposlast * (close_price - senp)
    else:
        spnl = trade.get('ExitPnL', 0.0) + trade.get('ExitPnL2', 0.0)
    spnl = round(spnl, 2)
    trade['unrealized_pnl'] = spnl

    # Brick string
    try:
        sec = portfolio_dict[trade['portfolio']][symbol]
        rbrick = round(sec['brick_size'], 2)
        if param['renko_brick_type'] == 'Calculation':
            rbrick_str = f"{round(sec['atr_brick'],2)} / {round(sec['price_delta'],2)} / {rbrick}"
        else:
            rbrick_str = str(rbrick)
    except:
        rbrick_str = ""

    trade_type = "LIVE" if param.get("PLACE_ORDER") else "PAPER"

    # ---- push values -------------------------------------------------
    cells = [
        symbol,
        str(close_price),
        str(senp),
        sexp,
        str(spos * lot_size),
        str(shv),
        str(spnl),
        sdten,
        sdtex,
        rbrick_str if abs(sposlast) > 0 else "",
        trade_type,
        ""                     # button placeholder
    ]

    for col, val in enumerate(cells):
        cls = "pnl-pos" if col == 6 and spnl > 0 else "pnl-neg" if col == 6 and spnl < 0 else ""
        _set_cell(param, row_idx, col, val, cls)

    # ---- Close button state -----------------------------------------
    btn_js = f"""
    <script>
    const tr = document.querySelector('tr[data-idx="{row_idx}"]');
    const btn = tr.querySelector('.close-btn');
    if ({abs(sposlast)>0}) {{
        btn.style.display = 'inline-block';
        btn.style.backgroundColor = '{ "green" if spnl>0 else "red" }';
        btn.disabled = false;
    }} else {{
        btn.style.display = 'inline-block';
        btn.disabled = true;
        btn.style.backgroundColor = 'gray';
    }}
    </script>
    """
    param['tradebox'].append_display_data(HTML(btn_js))


# ------------------------------------------------------------------
# 6. Main entry point – replace your old `create_trade_table_new`
# ------------------------------------------------------------------
def create_trade_table_new(portfolio_dict, candles_dict, param, out_live):
    """
    Call this every time `param['trade_table']` changes.
    """
    #param['candles_dict']   = candles_dict
    #param['portfolio_dict'] = portfolio_dict

    trade_table = param['trade_table']
    width       = param['trade_table_width']

    # Ensure data list is large enough
    needed = len(trade_table)
    
    if len(param['trade_data']) < needed:
        param['trade_data'].extend([{} for _ in range(2 + needed - len(param['trade_data']))])

    #param['trade_data'] = [{} for _ in range(param['trade_table_height'] + 2)]
    
    # Fill rows
    for idx, trade in enumerate(trade_table):
        row_idx = idx + 1  
        param['trade_data'][row_idx] = trade
        update_trade_row(portfolio_dict, candles_dict, param, trade, row_idx)

    # Hide surplus rows
    max_rows = param['trade_table_height'] + 2
    for r in range(len(trade_table)+1, max_rows):
        hide_js = f"""
        <script>
        const tr = document.querySelector('tr[data-idx="{r-1}"]');
        if (tr) tr.style.display = 'none';
        </script>
        """
        param['tradebox'].append_display_data(HTML(hide_js))

    for r in range(len(trade_table)):
        param['tradebox'].append_display_data(HTML(
            f'<script>document.querySelector("tr[data-idx=\'{r}\']").style.display = "";</script>'
        ))



def live_trade(strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, out_live, renko_dict):
    RUN_FOR_MINUTES = param['RUN_FOR_MINUTES']
    PLACE_ORDER = param['PLACE_ORDER']
    
    instrument_symbol_list = param['instrument_symbol_list']
    instrument_option_list = param['instrument_option_list']
    
    
    now = datetime.now()  
    nowtz = now#.astimezone(tz)
    new_now = nowtz
    old_minute=nowtz.minute-1
    
    date_str = now.strftime('%Y-%m-%d-%H%M')
    summary_filename = SUMMARYPATH+param['index_symbol_option']+"-LiveSignal-"+date_str+".csv"
    
    with open(SUMMARYPATH+"log.txt",'a') as livelog:
        livelog.write("\n----starting livetrade : "+str(nowtz)+"----------\n")
    
    #nowhmds = now.strftime("%Y-%M-%d-%H%m")
    #param['DEFAULT_SCAN_FILE'] = SUMMARYPATH+"scan_data"+datestr+".xlsx"
    summary_scan_filename = SUMMARYPATH+"scan_data"+date_str+".xlsx"

    i=0
    i_acc=0
    candles_live=None

    
    #print(now)
    newminute_flag = False
    log_flag = False
    strategy_flag=False
    dbg_flag=False
    market_data_update_flag=False
    
    qq=0

    streamer=False
    MarketHours = False 
    subscribe_ticker=False
    ACCESS_TOKEN = None    
    param_backtest_length=0
    
    print("scan trade loop BEGINS")
    out_live.append_stdout('STARTING LIVE RUN'+'\n') 
    
    datahandler.run_scanner(param)
    datahandler.prune(globalvar.g_underinstrument_dict)

    #create_global_trade_items(portfolio_dict, candles_dict, param)
    
    while(i<param['RUN_FOR_MINUTES']):
        if param['RUN_FOR_MINUTES'] == 0:
            #msg = "globalvar.g_param['RUN_FOR_MINUTES']: "+str(globalvar.g_param['RUN_FOR_MINUTES'])
            msg = "globalvar.g_param['RUN_FOR_MINUTES']: "+str(param['RUN_FOR_MINUTES'])
            out_live.append_stdout(msg+'\n')
            break
        now = datetime.now()
        nowtz = now#.astimezone(tz)
        
        
        ''' check for market hours'''
        clocktime = 100*nowtz.hour+nowtz.minute
        #tradeWindow = param['tradewindowStart'] <= clocktime and param['tradewindowEnd'] >= clocktime  
        #clocktimesec = 10000*nowtz.hour+100*nowtz.minute+nowtz.second
        
        OffHours = clocktime<915 or clocktime>1530
        
        OldMarketHours=MarketHours
        MarketHours = 915 <= clocktime and 1530 >= clocktime 
        
       
        new_minute=nowtz.minute
        new_second = nowtz.second
        if new_minute!=old_minute:
            gc.collect()
            #print_memory()
            #top_objects()
            if OffHours==True:
                if param['show_detail_log']==True:
                    out_live.append_stdout('OFF HOURS'+'\n')
            #print("param['RUN_FOR_MINUTES']:",param['RUN_FOR_MINUTES'])
            i+=1
            new_now = nowtz
            if param['show_detail_log']==True:
                print("Time:",nowtz)
                msg = "Time:"+str(nowtz)
                out_live.append_stdout(msg+'\n')
            #out_live.append_stdout("globalvar.g_param['RUN_FOR_MINUTES']: "+str(globalvar.g_param['RUN_FOR_MINUTES'])+'\n')
            old_minute = new_minute
            
            
            newminute_flag = True
            log_flag = True
            table_flag = True
            position_flag = True
            #dbg_flag = True
            strategy_flag=True
            market_data_update_flag=True
            #print("1: ",datetime.now())
            '''
            stro = ""
            for portfolio in portfolio_dict.keys():
                symbols = portfolio_dict[portfolio]
                for symbol in symbols.keys():
                    print(symbol)
                    stro+=symbol+'\n'
                    #print("CANDLE: ",candles_dict[symbol][-1])
                    stro+="CANDLE->"+"datetime:"+str(candles_dict[symbol][-1]['datetime'])+" :close"+str(candles_dict[symbol][-1]['close'])+'\n'
                    #print("PREV_CANDLE: ",candles_dict[symbol][-2])
                    #print("RENKO: ",renko_dict[symbol][-1])
                    #stro+=str(renko_dict[symbol][-1])+'\n'
                    stro+="RENKO->"+"datetime:"+str(renko_dict[symbol][-1]['datetime'])+" :close"+str(renko_dict[symbol][-1]['close'])+'\n'
            out_live.append_stdout(stro+'\n')
            '''
        
        
        if OffHours==True:
            time.sleep(10)
            continue
        #if newminute_flag==True:
        
        # run scanner and import scanned instrument history and run backdata
        clocktimesec = (100*nowtz.hour+nowtz.minute)*100+nowtz.second
        starttimesec = param['start_time']*100+param['start_time_second']
        #scanTimeWindow = clocktime>=param['start_time']# and clocktime<=param['stop_order_time']
        scanTimeWindow = (clocktimesec>=starttimesec)
        new_scan_interval = new_minute%int(param['scan_timeframe'])==0
        if newminute_flag == True and scanTimeWindow and new_scan_interval:
            newminute_flag = False
            try:
                datahandler.prune(globalvar.g_underinstrument_dict)
                ####datahandler.update_underlying(True)
                datahandler.run_scanner(param)
                #datahandler.purge(globalvar.g_underinstrument_dict)
                
                build_scanner_data(strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict)
                #print("renko_dict.keys():",renko_dict.keys())
                #for symbol in renko_dict.keys():
                #    renko = renko_dict[symbol]
                #    #print("renko: ", symbol, len(renko))
                '''
                updating OHLCV data in underlying futures
                '''
                underlying_candle_updater(param)
            except Exception as e:
                traceback.print_exc()
                print("scan error: ",e)
        else:
            try:
                '''
                updating OHLCV data in underlying futures
                '''
                underlying_candle_updater(param)
                #datahandler.update_underlying()
            except:
                pass
                

        
        if streamer==False:
            print("globalvar.g_instrument_dict: ",globalvar.g_instrument_dict)
            
            #instrument_token_list = [sub_dict['token'] for sub_dict in globalvar.g_instrument_dict.values()]
            instrument_token_list = []
            for sub_dict_key in list(globalvar.g_instrument_dict.keys()):
                sub_dict = globalvar.g_instrument_dict[sub_dict_key]
                if 'token' in sub_dict.keys():
                    instrument_token_list.append(sub_dict['token'])
                    
            
            futures_list = list(globalvar.g_futures_token_dict.values())
            #list(globalvar.g_futures_token_dict.values())
            
            
            instrument_token_list = instrument_token_list + futures_list 
            
            print("create stream instrument_token_list :",instrument_token_list)
            #if globalvar.g_kiteticker==None:
            #    zerodha.create_stream(instrument_token_list)
            #else:
            #    zerodha.add_stream(instrument_token_list)
            streamer_thread = Thread(target=copytick,args=(instrument_token_list,))
            streamer_thread.start()
            #streamer_thread.join()
            streamer=True
        else:
            #instrument_token_list = [sub_dict['token'] for sub_dict in globalvar.g_instrument_dict.values()]
            instrument_token_list = []
            for sub_dict_key in list(globalvar.g_instrument_dict.keys()):
                sub_dict = globalvar.g_instrument_dict[sub_dict_key]
                if 'token' in sub_dict.keys():
                    instrument_token_list.append(sub_dict['token'])
                    
            futures_list = list(globalvar.g_futures_token_dict.values())
            instrument_token_list = instrument_token_list + futures_list 
            
            gins = globalvar.g_token_list
            add_stream_data=False
            add_stream_list = []
            for inst in instrument_token_list:
                if inst not in gins:
                    print("inst",inst)
                    #print("gins",gins)
                    #print("instrument_token_list:",instrument_token_list)
                    add_stream_data=True
                    add_stream_list.append(inst)
                    #break
            if len(add_stream_list)>0:zerodha.add_stream(add_stream_list)
                
        

        #------------------update candles-------------------------------------
        if dbg_flag==True:print("candle updater in: ",datetime.now())
        wait_time = int(param['update_frequency'])
        time.sleep(wait_time)

        '''
        updating OHLCV data in options
        '''
        candle_updater(candles_dict, param, out_live)

        

        
        if dbg_flag==True:print("candle updater out: ",datetime.now()) 
        
        
        
        #-------------------------- strategy calculations--------------------------
        if dbg_flag==True:
            print("strategy in: ",datetime.now())


        candleclock = now.hour*100+now.minute 
        tradeEntryWindow = candleclock>=param['start_time'] and candleclock<=param['stop_order_time']
        tradeExitTimeCondition = candleclock>=param['exit_time']


        try:
            if param['trade_zerodha']==True:
                margins = globalvar.g_kite.margins()
                cash = margins['equity']['available']['cash']
                #print("Equity Balance:", margins['equity']['available']['cash'])
                globalvar.g_universalparam['overall_investment'] = cash
            elif param['trade_finvasia']==True:
                globalvar.g_universalparam['overall_investment'] = globalvar.g_universalparam['overall_investment']
        except:
            pass
        
        for portfolio in list(portfolio_dict.keys()):
            symbols = portfolio_dict[portfolio]
            for symbol in list(symbols.keys()):
                if symbol not in list(candles_dict.keys()):continue
                candles = candles_dict[symbol]
                if len(candles_dict[symbol])<1:continue
                if symbol not in list(mtfcandles_dict.keys()):continue
                mtfcandles = mtfcandles_dict[symbol]
                if symbol not in list(renko_dict.keys()):continue
                renko = renko_dict[symbol]
                if globalvar.g_instrument_dict[symbol]['backdata_ready']==True:
                    run_live(strategyClass_dict, portfolio_dict, candles_dict, portfolio, symbol, candles, mtfcandles, param, renko, 0, mtfcandles_dict)
                del candles
                del renko
        #------------build trade table-------------------
        build_trade_table(param)
        
        #----------running profit----------------------------
        globalvar.g_universalparam['profit_w'].value = str(round(globalvar.g_universalparam['profit'],2))
        if globalvar.g_universalparam['profit']>0:
            globalvar.g_universalparam['profit_w'].style = {'background': 'green'}
        else:
            globalvar.g_universalparam['profit_w'].style = {'background': 'red'}
        
        if dbg_flag==True:
            print("strategy out: ",datetime.now())
        

        #------------create trade table-------------------
        #if log_flag==True:
        create_trade_table_new_prev(portfolio_dict, candles_dict, param, out_live)


        #--------------output display------------------------
        try:
            trade_table = param['trade_table']
            totalPnL=0.0
            for trade in trade_table:
                if 'unrealized_pnl' in trade.keys():
                    totalPnL+=trade['unrealized_pnl']
            #globalvar.g_param['total_pnl_w'].value = totalPnL
            param['total_pnl_w'].value = totalPnL
        except:
            pass

 
        
        #------------------output log--------------------------------
        if log_flag == True:
            write_trade_table_file(param,summary_filename)
            write_scan_output(param,summary_scan_filename)
            log_flag = False
            
           
        #---------------------------------order management------------------------------------------
        if dbg_flag==True:
            print("order in: ",datetime.now())
        
        order_placement(param, portfolio_dict)
        
        if dbg_flag==True:
            print("order out: ",datetime.now())
            dbg_flag=False


        if market_data_update_flag==True:
            #market_data_update_flag=False
            try:
                update_trade_using_zerodha_data(param, portfolio_dict)
            except Exception as e:
                print("update_trade_using_zerodha_data: ",e)

            try:
                update_trade_using_finvasia_data(param, portfolio_dict)
            except Exception as e:
                print("update_trade_using_finvasia_data: ",e)


        # prune
        prune_length=2
        renko_prune_length=2
        for portfolio in list(portfolio_dict.keys()):
            symbols = portfolio_dict[portfolio]
            for symbol in list(symbols.keys()):
                if symbol not in list(candles_dict.keys()):continue
                #candles = candles_dict[symbol]
                if len(candles_dict[symbol])<1:continue
                if symbol not in list(renko_dict.keys()):continue
                #renko = renko_dict[symbol]
                if len(candles_dict[symbol])>prune_length and len(renko_dict[symbol])>prune_length:
                    #print("prune:",len(candles), len(renko))
                    candles_dict[symbol] = candles_dict[symbol][-prune_length:]
                    #del candles
                if len(renko_dict[symbol])>renko_prune_length:
                    renko_dict[symbol] = renko_dict[symbol][-renko_prune_length:]
                    #del renko

        
        #---------------runtime summary---------------------------------------------
        calc_runtime_summary(param)
        
    #--------------------------------end of loop------------------------------------------        
    param['RUN_FOR_MINUTES'] = 0
    #print('joining thread')
    #tick_thread.join()
    globalvar.g_copytick=False
    print("loop ENDS")
    
    

def order_placement(param, portfolio_dict):
    flag = False
    if param['PLACE_ORDER']:
        exchange = param['index_exchange']
        for portfolio in list(portfolio_dict.keys()):
            symbols = portfolio_dict[portfolio]
            for symbol in list(symbols.keys()):
                #candles_live = candles_dict[symbol]
                security = portfolio_dict[portfolio][symbol]
                if 'lot_size' in security.keys():
                    lot_size = security['lot_size']
                else:
                    lot_size = param['lot']
                #quantity = int(security['position']*lot_size)
                if len(security['signal'])>0:
                    quantity = int(security['signal'][-1]['position']*lot_size)
                else:
                    continue
                #if security['trade_in']==1:print("in place order:",security)
                ''' ZERODHA '''
                if param['trade_zerodha']==True:
                    order_id = None
                    if security['long_signal_fired'] == 1:
                        flag = True
                        #print("in place buy zerodha:")
                        if param['index_symbol_option']=='BANKEX':
                            d=(security['close']//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_buy(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                                 quantity=quantity, price=pr)
                        elif param['index_symbol_option']=='STOCK':
                            d=security['entryprice']#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_buy(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                                 quantity=quantity, price=pr)
                        else:
                            order_id = place_buy(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, quantity=quantity)
                    
                    elif security['close_long_signal_fired'] == 1:
                        flag = True
                        #quantity = int(security['signal'][-1]['position']*param['lot'])
                        if param['index_symbol_option']=='BANKEX':
                            d=(security['close']//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_sell(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, 
                                                  symbol=symbol, quantity=quantity, price=pr)
                        elif param['index_symbol_option']=='STOCK':
                            d=security['exitprice']#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_sell(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, 
                                                  symbol=symbol, quantity=quantity, price=pr)
                        else:
                            order_id = place_sell(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, quantity=quantity)
                    
                    elif security['short_signal_fired'] == 1:
                        flag = True
                        #print("in place buy zerodha:")
                        #quantity = int(security['signal'][-1]['position']*param['lot'])
                        if param['index_symbol_option']=='BANKEX':
                            d=(security['close']//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_sell(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                       quantity=quantity, price=pr, short_flag=1)
                        elif param['index_symbol_option']=='STOCK':
                            d=security['entryprice']#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_sell(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                       quantity=quantity, price=pr, short_flag=1)
                        else:
                            order_id = place_sell(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                       quantity=quantity, short_flag=1)
                    
                    elif security['close_short_signal_fired'] == 1:
                        flag = True
                        #quantity = int(security['signal'][-1]['position']*param['lot'])
                        if param['index_symbol_option']=='BANKEX':
                            d=(security['close']//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_buy(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                      quantity=quantity, price=pr)
                        elif param['index_symbol_option']=='STOCK':
                            d=security['exitprice']#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_buy(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                                 quantity=quantity, price=pr)
                        else:
                            order_id = place_buy(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                      quantity=quantity)
                    if order_id is not None:
                        security['zerodha_order_id'] = order_id
                        security['zerodha_order_id_status'] = 'OPEN'
                        security['zerodha_order_id_status_updated'] = False
                        security['signal'][-1]['zerodha_order_id'] = order_id
                ''' FINVASIA '''
                if param['trade_finvasia']==True:
                    order_id = None
                    if security['long_signal_fired'] == 1:
                        flag = True
                        #quantity = int(security['signal'][-1]['position']*param['lot'])
                        if param['index_symbol_option']=='BANKEX':
                            d=(security['close']//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, 
                                                 symbol=symbol, quantity=quantity, price=pr)
                        elif param['index_symbol_option']=='STOCK':
                            d=security['entryprice']#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, 
                                                 symbol=symbol, quantity=quantity, price=pr)
                        else:
                            order_id = place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity)
                    
                    elif security['close_long_signal_fired'] == 1:
                        flag = True
                        #quantity = int(security['signal'][-1]['position']*param['lot'])
                        if param['index_symbol_option']=='BANKEX':
                            d=(security['close']//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, 
                                                  symbol=symbol, quantity=quantity, price=pr)
                        elif param['index_symbol_option']=='STOCK':
                            d=security['exitprice']#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, 
                                                  symbol=symbol, quantity=quantity, price=pr)
                        else:
                            order_id = place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity)
                    
                    elif security['short_signal_fired'] == 1:
                        flag = True
                        #quantity = int(security['signal'][-1]['position']*param['lot'])
                        if param['index_symbol_option']=='BANKEX':
                            d=security['close']#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                       quantity=quantity, price=pr, short_flag=1)
                        elif param['index_symbol_option']=='STOCK':
                            d=(security['entryprice'])#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                       quantity=quantity, price=pr, short_flag=1)
                        else:
                            order_id = place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                       quantity=quantity, short_flag=1)
                    
                    elif security['close_short_signal_fired'] == 1:
                        flag = True
                        #quantity = int(security['signal'][-1]['position']*param['lot'])
                        if param['index_symbol_option']=='BANKEX':
                            d=(security['close']//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                                 quantity=quantity, price=pr)
                        elif param['index_symbol_option']=='STOCK':
                            d=(security['exitprice'])#//0.05)*0.05
                            pr = round(d,2)
                            order_id = place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                       quantity=quantity, price=pr, short_flag=1)
                        else:
                            order_id = place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity)
                    if order_id is not None:
                        security['finvasia_order_id'] = order_id
                        security['finvasia_order_id_status'] = 'OPEN'
                        security['finvasia_order_id_status_updated'] = False
                        security['signal'][-1]['finvasia_order_id'] = order_id
    try:
        if flag==True: write_trade_table_file(param)
    except:
        pass 
    return



def order_update(param, portfolio_dict):
    if param['PLACE_ORDER']:
        exchange = param['index_exchange']
        for portfolio in list(portfolio_dict.keys()):
            symbols = portfolio_dict[portfolio]
            for symbol in list(symbols.keys()):
                security = portfolio_dict[portfolio][symbol]
                if param['trade_zerodha']==True:
                    if 'zerodha_order_id' in security.keys():
                        order_id = security['zerodha_order_id']
                        if 'zerodha_order_id_status' in security.keys():
                            if security['zerodha_order_id_status'] == 'OPEN':
                                order_id = zerodha.modify_order(globalvar.g_kite, order_id)
                                security['zerodha_order_id'] = order_id
                                security['zerodha_order_id_status'] = 'CLOSE'
                if param['trade_finvasia']==True:
                     if 'finvasia_order_id' in security.keys():
                        order_id = security['finvasia_order_id']
                        if 'finvasia_order_id_status' in security.keys():
                            if security['finvasia_order_id_status'] == 'OPEN':
                                order_id = finvasia.modify_order(globalvar.g_shoonya, order_id)
                                security['finvasia_order_id'] = order_id
                                security['finvasia_order_id_status'] = 'CLOSE'
    return


'''
def update_trade_using_broker_data(param, portfolio_dict):
    flag=False
    #print("updating trade using broker data")
    if param['PLACE_ORDER']:
        for portfolio in portfolio_dict.keys():
            symbols = portfolio_dict[portfolio]
            for symbol in symbols.keys():
                security = portfolio_dict[portfolio][symbol]
                if param['trade_zerodha']==True:
                    if 'zerodha_order_id' in security.keys():
                        if 'zerodha_order_id_status_updated' in security.keys():
                            if security['zerodha_order_id_status_updated'] == True: continue
                        order_id = security['zerodha_order_id']
                        trade = zerodha.get_order_trade(order_id)#['entryprice']
                        if trade is not None:
                            entryprice = trade['average_price']
                            update_security(param, security, entryprice)
                            security['zerodha_order_id_status_updated'] = True
                            flag=True
                if param['trade_finvasia']==True:
                    if 'finvasia_order_id' in security.keys():
                        if 'finvasia_order_id_status_updated' in security.keys():
                            if security['finvasia_order_id_status_updated'] == True: continue
                        order_id = security['finvasia_order_id']
                        trade = finvasia.get_order_trade(order_id)#['entryprice']
                        if trade is not None:
                            entryprice = float(trade['avgprc'])#trade['average_price']
                            update_security(param, security, entryprice)
                            security['finvasia_order_id_status_updated'] = True
                            flag=True
        if flag==True: update_signal_list(param, portfolio_dict)
    return
'''


def update_trade_using_zerodha_data(param, portfolio_dict):
    flag=False
    #print("updating trade using zerodha data")
    if param['PLACE_ORDER']:
        for portfolio in list(portfolio_dict.keys()):
            symbols = portfolio_dict[portfolio]
            for symbol in list(symbols.keys()):
                security = portfolio_dict[portfolio][symbol]
                if param['trade_zerodha']==True:
                    if 'zerodha_order_id' in security.keys():
                        if 'zerodha_order_id_status_updated' in security.keys():
                            if security['zerodha_order_id_status_updated'] == True: continue
                        order_id = security['zerodha_order_id']
                        trade = zerodha.get_order_trade(order_id)#['entryprice']
                        if trade is not None:
                            price = trade['average_price']
                            transaction_type = trade['transaction_type']
                            if transaction_type=='BUY':
                                update_security(param, security, price, 'B')
                            else:
                                update_security(param, security, price, 'S')
                            security['zerodha_order_id_status_updated'] = True
                            flag=True
        if flag==True: update_signal_list(param, portfolio_dict)
        try:
            if flag==True: write_trade_table_file(param)
        except Exception as e:
            print("update_trade_using_zerodha_data trade table file write error: ",e)
    return

    
def update_trade_using_finvasia_data(param, portfolio_dict):
    flag=False
    #print("updating trade using finvasia data")
    if param['PLACE_ORDER']:
        for portfolio in list(portfolio_dict.keys()):
            symbols = portfolio_dict[portfolio]
            for symbol in list(symbols.keys()):
                security = portfolio_dict[portfolio][symbol]
                if param['trade_finvasia']==True:
                    if 'finvasia_order_id' in security.keys():
                        if 'finvasia_order_id_status_updated' in security.keys():
                            if security['finvasia_order_id_status_updated'] == True: continue
                        order_id = security['finvasia_order_id']
                        trade = finvasia.get_order_trade(order_id)#['entryprice']
                        if trade is not None:
                            price = float(trade['avgprc'])#trade['average_price']
                            trantype = trade['trantype']#: 'B'
                            if trantype=='B':
                                update_security(param, security, price, 'B')
                                security['finvasia_order_id_status_updated'] = True
                            else:
                                update_security(param, security, price, 'S')
                                security['finvasia_order_id_status_updated'] = True
                            flag=True
        if flag==True: update_signal_list(param, portfolio_dict)
        try:
            if flag==True: write_trade_table_file(param)
        except Exception as e:
            print("update_trade_using_finvasia_data trade table file write error: ",e)
    return

    



    



def write_trade_table_file(param=None,summaryfilename=None):
    try:
        #print(type(list(dftrade.columns)),list(dftrade.columns))
        trade_table = param['trade_table']
        #print(trade_table)
        if len(trade_table)<1:return
        dftrade = pd.DataFrame(trade_table)
        #print(dftrade)
        
        if param['live_trading']==False:
            filename = SUMMARYPATH+param['index_symbol_option']+"BacktestSignal.csv"
        else:
            filename = summaryfilename
            dftrade = dftrade[dftrade['live']==True]

        #print(dftrade)
        
        c1 = ['symbol','EntryDateTime','EntryPrice','EntryPosition','EntryHoldingValue','EntryMessage']
        if 'ExitDateTime' in list(dftrade.columns):
            c1 = c1+['ExitDateTime','ExitPrice','ExitPosition','ExitHoldingValue','ExitMessage','ExitPnL']
        if 'ExitDateTime2' in list(dftrade.columns):
            c1 = c1+['ExitDateTime2','ExitPrice2','ExitPosition2','ExitHoldingValue2','ExitMessage2','ExitPnL2']
        c1 = c1 + ['remaining_position','realizedPnL','cumuRealizedPnL']
        #dftrade['TradeMode'] = 'PAPER' if param['PLACE_ORDER']==False else 'REAL'
        #print(c1)
        if 'atr_brick' in list(dftrade.columns):
            c1 = c1 + ['atr_brick']
        if 'price_delta' in list(dftrade.columns):
            c1 = c1 + ['price_delta']
        if 'brick_size' in list(dftrade.columns):
            c1 = c1 + ['brick_size']
        
        dftrade = dftrade[c1]
        #print(dftrade)
        
        dftrade['TradeMode'] = 'PAPER' if param['PLACE_ORDER']==False else 'REAL'
        #display(dftrade)
        if param['live_trading']==False:
            display(dftrade)

        #display(dftrade)
        #print(filename)
        
        dftrade.to_csv(filename)
    except Exception as e:
        print(e)
        #traceback.print_exc()
    return

def write_scan_output(param,summary_scan_filename):
    try:
        #print('going in stock scan writer')
        uindex = True
        uheader = False
        now = datetime.now()
        nowhm = now.replace(second=0, microsecond=0)        
        df1 = param['stock_top_gainer_w'].data
        df1.index = [nowhm for _ in range(len(df1))]
        df1.index.name='datetime'

        df2 = param['stock_top_loser_w'].data
        df2.index = [nowhm for _ in range(len(df2))]
        df2.index.name='datetime'

        try:
            with pd.ExcelWriter(summary_scan_filename, mode='a',if_sheet_exists='overlay', engine='openpyxl') as writer:
                df1.to_excel(writer,sheet_name="STOCKTOPGAINER",index=uindex,header=uheader,startrow=writer.sheets['STOCKTOPGAINER'].max_row)
                df2.to_excel(writer,sheet_name="STOCKTOPLOSER",index=uindex,header=uheader,startrow=writer.sheets['STOCKTOPLOSER'].max_row)
        except Exception as e:
            print(e)
            with pd.ExcelWriter(summary_scan_filename, mode='w', engine='xlsxwriter') as writer:
                df1.to_excel(writer,sheet_name="STOCKTOPGAINER",index=uindex,header=True)#,startrow=writer.sheets['STOCKTOPGAINER'].max_row)
                df2.to_excel(writer,sheet_name="STOCKTOPLOSER",index=uindex,header=True)#,startrow=writer.sheets['STOCKTOPLOSER'].max_row)
    except Exception as e:
        print(e)

'''
def print_memory():
    process = psutil.Process(os.getpid())
    print(f"Memory: {process.memory_info().rss / 1024**2:.2f} MB")


def safe_sizeof(obj):
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        try:
            return obj.memory_usage(deep=True).sum()
        except:
            return 0  # fallback
    else:
        return sys.getsizeof(obj)



def top_objects():
    sizes = defaultdict(int)

    for o in gc.get_objects():
        try:
            size = safe_sizeof(o)
            sizes[type(o)] += size
        except:
            pass  # skip problematic objects

    # Sort and print top memory consumers
    for obj_type, size in sorted(sizes.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"{obj_type}: {size / 1024 / 1024:.2f} MB")
'''
#END