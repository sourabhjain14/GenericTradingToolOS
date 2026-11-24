"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import math
import numpy as np
from datetime import datetime,timedelta
import pandas as pd
import importlib

from techlib import totalvolumeday
from techlib import SMA, EMA, HullMA, SMACandle, EMACandle
from techlib import SMACandleKey, EMACandleKey, HullMACandleKey
from techlib import EMAKeyCandleKey, EMAIndexKeyCandleKey
from techlib import  calc_atr, CCI


#import importlib
#importlib.reload(strategy.strategy1_strategy)

from strategy.eventmanager import get_state_analysis, build_trade_table
#from strategy.mtfcrosstrend_strategy import mtfcrosstrend


    
def calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price, tf):
    o = 'open'+str(tf)+'min'
    c = 'close'+str(tf)+'min'
    h = 'high'+str(tf)+'min'
    l = 'low'+str(tf)+'min'
    mi = 'index'+str(tf)+'min'
    
    new_candle_ = candles_slice[index]
    
    if index==0:
        newmtf=True
    else:    
        newmtf = candles_slice[index][mi] != candles_slice[index-1][mi] 
    
    if newmtf==True:
        if param['backtest_point'] != 'C':
            if price=='O':
                new_candle_[o] = new_candle['open']
                new_candle_[c] = new_candle['open']
                new_candle_[h] = new_candle['open']
                new_candle_[l] = new_candle['open']
        else:
            new_candle_[o] = new_candle['open']
            new_candle_[c] = new_candle['close']
            new_candle_[h] = new_candle['high']
            new_candle_[l] = new_candle['low']
                
        candletf = {'index1min':index,'datetime':new_candle['datetime'],'open':new_candle[o], 
                    'high':new_candle[h], 
                    'low':new_candle[l],
                    'close':new_candle[c]}
        mtfcandles_slice[str(tf)+'min'].append(candletf)
            #new_candle[mi] = len(mtfcandles_slice[str(tf)+'min']) - 1
    else:
        mindex = int(new_candle[mi])
        
        #print(new_candle['datetime']," : ",str(tf),":",mindex," : ", len(mtfcandles_slice[str(tf)+'min'])-1)
        
        if param['backtest_point'] != 'C':
            close = new_candle['close']
            mtfcandles_slice[str(tf)+'min'][mindex]['high'] =  max(close, mtfcandles_slice[str(tf)+'min'][mindex]['high']) 
            mtfcandles_slice[str(tf)+'min'][mindex]['low'] = min(close, mtfcandles_slice[str(tf)+'min'][mindex]['low'])
            mtfcandles_slice[str(tf)+'min'][mindex]['close'] = close
        else:
            close = new_candle['close']
            high = new_candle['high']
            low = new_candle['low']
            mtfcandles_slice[str(tf)+'min'][mindex]['high'] =  max(high, mtfcandles_slice[str(tf)+'min'][mindex]['high']) 
            mtfcandles_slice[str(tf)+'min'][mindex]['low'] = min(low, mtfcandles_slice[str(tf)+'min'][mindex]['low'])
            mtfcandles_slice[str(tf)+'min'][mindex]['close'] = close
        

        
        
def calc_higher_tf_slice(candles_slice, mtfcandles_slice, close, tf):
    o = 'open'+str(tf)+'min'
    c = 'close'+str(tf)+'min'
    h = 'high'+str(tf)+'min'
    l = 'low'+str(tf)+'min'
    mi = 'index'+str(tf)+'min'
    
    candles_slice[-1][c] = close
    candles_slice[-1][h] = max(close, candles_slice[-1][h])
    candles_slice[-1][l] = min(close, candles_slice[-1][l])
    
    
    #mindex = len(mtfcandles_slice[str(tf)+'min']) - 1
    mindex = int(candles_slice[-1][mi])
    mtfcandles_slice[str(tf)+'min'][mindex]['open'] = candles_slice[-1][o] 
    mtfcandles_slice[str(tf)+'min'][mindex]['high'] = candles_slice[-1][h] 
    mtfcandles_slice[str(tf)+'min'][mindex]['low'] = candles_slice[-1][l]
    mtfcandles_slice[str(tf)+'min'][mindex]['close'] = candles_slice[-1][c]
    #mtf_candles_slice[str(tf)+'min'].append(candletf) 

    
    
def calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price):
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price, 2)
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price,3)
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price,4)
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price,5)
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price,10)
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price,15)
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price,20)
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price,30)
    calc_higher_tf(param, new_candle, candles_slice, mtfcandles_slice, index, price,60)
    return






def run_backtest_OHLC_symbol(symbol=None, strategyClass_dict=None,portfolio_dict=None, 
                          portfolio=None, candles_symbols=None, 
                          param=None, mtfcandles=None, start_index=0, renko_symbols=None):
    #print(datetime.now(), portfolio, symbol)
    max_end_index = 0
    
    symbols = portfolio_dict[portfolio]
    #symbols = {}
    symbollist = [symbol]
    
    candles_symbols_slice = {}
    mtfcandles_symbols_slice = {}
    for symbol in list(symbols.keys()):
        #candles_symbols_slice[symbol] = {}
        candles_symbols_slice[symbol] = []
        #candles_slice = []
        
        mtfcandles_symbols_slice[symbol] = {}
        mtfcandles_slice = mtfcandles_symbols_slice[symbol]
        mtfcandles_slice['1min'] = []
        mtfcandles_slice['2min'] = []
        mtfcandles_slice['3min'] = []
        mtfcandles_slice['4min'] = []
        mtfcandles_slice['5min'] = []
        mtfcandles_slice['10min'] = []
        mtfcandles_slice['15min'] = []
        mtfcandles_slice['20min'] = []
        mtfcandles_slice['30min'] = []
        mtfcandles_slice['60min'] = []
        mtfcandles_slice['240min'] = []
        mtfcandles_slice['1D'] = []
        mtfcandles_slice['1W'] = []
        mtfcandles_slice['1M'] = []
        mtfcandles_slice['1Y'] = []
    
    
    if start_index!=0:
        for i in range(start_index):
            for symbol in list(symbols.keys()):
                candle = candles_symbols[symbol][i]
                new_candle = candle.copy()
                candles_symbols_slice[symbol].append(new_candle)
        
    for symbol in symbollist:
        end_index = len(candles_symbols[symbol])
        max_end_index = max(max_end_index, end_index) 
        print("size: ",symbol, end_index)
    
    #for symbol in symbols.keys():
    #    print(symbol,len(candles_symbols[symbol]))
        
    for index in range(start_index, max_end_index):    
        for symbol in symbollist:
            candles = candles_symbols[symbol]
            try:
                candle = candles[index]
            except:
                #print(symbol, len(candles), index)
                candle = candles[-1]
            
            candles_slice = candles_symbols_slice[symbol]
            intrabar = []
            if candle['close'] > candle['open']:
                if param['backtest_point'] == 'OHCLC': intrabar = ['O','L','C','H','C']
                elif param['backtest_point'] == 'OHLC': intrabar = ['O','H','L','C']
                elif param['backtest_point'] == 'C': intrabar = ['C']
            else:
                if param['backtest_point'] == 'OHCLC': intrabar = ['O','H','C','L','C']
                elif param['backtest_point'] == 'OHLC': intrabar = ['O','H','L','C']
                elif param['backtest_point'] == 'C': intrabar = ['C']
                #intrabar = ['O','H','C','L','C']
                #intrabar = ['O','PH','H','PL','C','L','C']
                #intrabar = ['O','PH','PL','C']
                
            for price in intrabar:
                #print('backtest loop:',index)
                if param['backtest_point'] == 'C':
                    new_candle = candle.copy()
                    #new_candle['close'] = new_candle['open']
                    #new_candle['high'] = new_candle['open']
                    #new_candle['low'] = new_candle['open']
                    candles_slice.append(new_candle)
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, None)
                        
                elif price == 'O':
                    new_candle = candle.copy()
                    
                    new_candle['close'] = new_candle['open']
                    new_candle['high'] = new_candle['open']
                    new_candle['low'] = new_candle['open']
                    
                    candles_slice.append(new_candle)
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                        
                    
                elif price == 'L':
                    #new_candle = candle.copy()
                    #print(index)
                    #print(candles_slice)
                    close = candle['low']
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                elif price == 'C':
                    #new_candle = candle.copy()
                    close = candle['close']
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                elif price == 'H':
                    #new_candle = candle.copy()
                    close = candle['high']
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                elif price == 'PH':
                    #new_candle = candle.copy()
                    close = 1.00011*candles[index-1]['high']
                    if close<candle['low'] or close>candle['high']: continue
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                    
                elif price == 'PL':
                    #new_candle = candle.copy()
                    close = 0.99989*candles[index-1]['low']
                    if close<candle['low'] or close>candle['high']: continue
                    
                    #print(candle)
                    
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                    
                else:
                    new_candle = candle.copy()
                    new_candle['close'] = new_candle['close']
                    new_candle['high'] = max(new_candle['close'], candles_slice[-1]['high'])
                    new_candle['low'] = min(new_candle['close'], candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = new_candle['close']
                    candles_slice[-1]['high'] = new_candle['high']
                    candles_slice[-1]['low'] = new_candle['low']
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                
                candles_slice, mtfcandles_slice = run_live(strategyClass_dict, portfolio_dict, candles_symbols_slice, portfolio, 
                                                           symbol, candles_slice, mtfcandles_slice, param, renko_symbols[symbol], 1, mtfcandles)
                #strategyClass_dict, portfolio_dict, candles_dict, portfolio, symbol, candles, mtfcandles, param, renko, backtest=0
            
    return 0






def run_backtest_OHLC_new(strategyClass_dict=None,portfolio_dict=None, 
                          portfolio=None, candles_symbols=None, 
                          param=None, mtfcandles=None, start_index=0, renko_symbols=None):
    #print(datetime.now(), portfolio, symbol)
    max_end_index = 0
    symbols = portfolio_dict[portfolio]
    candles_symbols_slice = {}
    mtfcandles_symbols_slice = {}
    for symbol in list(symbols.keys()):
        #candles_symbols_slice[symbol] = {}
        candles_symbols_slice[symbol] = []
        #candles_slice = []
        
        mtfcandles_symbols_slice[symbol] = {}
        mtfcandles_slice = mtfcandles_symbols_slice[symbol]
        mtfcandles_slice['1min'] = []
        mtfcandles_slice['2min'] = []
        mtfcandles_slice['3min'] = []
        mtfcandles_slice['4min'] = []
        mtfcandles_slice['5min'] = []
        mtfcandles_slice['10min'] = []
        mtfcandles_slice['15min'] = []
        mtfcandles_slice['20min'] = []
        mtfcandles_slice['30min'] = []
        mtfcandles_slice['60min'] = []
        mtfcandles_slice['240min'] = []
        mtfcandles_slice['1D'] = []
        mtfcandles_slice['1W'] = []
        mtfcandles_slice['1M'] = []
        mtfcandles_slice['1Y'] = []
    
    
    if start_index!=0:
        for i in range(start_index):
            for symbol in list(symbols.keys()):
                candle = candles_symbols[symbol][i]
                new_candle = candle.copy()
                candles_symbols_slice[symbol].append(new_candle)
        
    for symbol in list(symbols.keys()):
        end_index = len(candles_symbols[symbol])
        max_end_index = max(max_end_index, end_index) 
        print("size: ",symbol, end_index)
    
    #for symbol in symbols.keys():
    #    print(symbol,len(candles_symbols[symbol]))
        
    for index in range(start_index, max_end_index):    
        for symbol in list(symbols.keys()):
            candles = candles_symbols[symbol]
            try:
                candle = candles[index]
            except:
                #print(symbol, len(candles), index)
                candle = candles[-1]
            
            candles_slice = candles_symbols_slice[symbol]
            intrabar = []
            if candle['close'] > candle['open']:
                if param['backtest_point'] == 'OHCLC': intrabar = ['O','L','C','H','C']
                elif param['backtest_point'] == 'OHLC': intrabar = ['O','H','L','C']
                elif param['backtest_point'] == 'C': intrabar = ['C']
            else:
                if param['backtest_point'] == 'OHCLC': intrabar = ['O','H','C','L','C']
                elif param['backtest_point'] == 'OHLC': intrabar = ['O','H','L','C']
                elif param['backtest_point'] == 'C': intrabar = ['C']
                #intrabar = ['O','H','C','L','C']
                #intrabar = ['O','PH','H','PL','C','L','C']
                #intrabar = ['O','PH','PL','C']
                
            for price in intrabar:
                #print('backtest loop:',index)
                if param['backtest_point'] == 'C':
                    new_candle = candle.copy()
                    #new_candle['close'] = new_candle['open']
                    #new_candle['high'] = new_candle['open']
                    #new_candle['low'] = new_candle['open']
                    candles_slice.append(new_candle)
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, None)
                        
                elif price == 'O':
                    new_candle = candle.copy()
                    
                    new_candle['close'] = new_candle['open']
                    new_candle['high'] = new_candle['open']
                    new_candle['low'] = new_candle['open']
                    
                    candles_slice.append(new_candle)
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                        
                    
                elif price == 'L':
                    #new_candle = candle.copy()
                    #print(index)
                    #print(candles_slice)
                    close = candle['low']
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                elif price == 'C':
                    #new_candle = candle.copy()
                    close = candle['close']
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                elif price == 'H':
                    #new_candle = candle.copy()
                    close = candle['high']
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                elif price == 'PH':
                    #new_candle = candle.copy()
                    close = 1.00011*candles[index-1]['high']
                    if close<candle['low'] or close>candle['high']: continue
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                    
                elif price == 'PL':
                    #new_candle = candle.copy()
                    close = 0.99989*candles[index-1]['low']
                    if close<candle['low'] or close>candle['high']: continue
                    
                    #print(candle)
                    
                    high = max(close, candles_slice[-1]['high'])
                    low = min(close, candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = close
                    candles_slice[-1]['high'] = high
                    candles_slice[-1]['low'] = low
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                    
                else:
                    new_candle = candle.copy()
                    new_candle['close'] = new_candle['close']
                    new_candle['high'] = max(new_candle['close'], candles_slice[-1]['high'])
                    new_candle['low'] = min(new_candle['close'], candles_slice[-1]['low'])
                    candles_slice[-1]['close'] = new_candle['close']
                    candles_slice[-1]['high'] = new_candle['high']
                    candles_slice[-1]['low'] = new_candle['low']
                    
                    if param['multitimeframe']:
                        calc_higher_tf_mtf(param, new_candle, candles_slice, mtfcandles_slice, index, price)
                    
                
                candles_slice, mtfcandles_slice = run_live(strategyClass_dict, portfolio_dict, candles_symbols_slice, portfolio, 
                                                           symbol, candles_slice, mtfcandles_slice, param, renko_symbols[symbol])
            
            #mindex
            #print(mtfcandles_slice['2min'][mindex])
            
            #try:
            #    mindex = int(candles_slice[index]['index2min'])
            #    print(mindex, mtfcandles_slice['2min'][mindex]['datetime'], mtfcandles_slice['2min'][mindex-1]['CCI'])
            #except:
            #    pass
            
            #if price=='O' and index%100==0: print(index, candles_slice[index])
   
        
    #print(mtfcandles_slice['2min'][-1])
    #print(mtfcandles_slice['2min'][-2])
    #print(mtfcandles_slice['2min'][-3])
    #print(mtfcandles_slice['2min'][-4])
    #print(mtfcandles_slice['2min'][-5])
    #print(mtfcandles_slice['2min'][-6])
    #print('leaving backtest')    
    return# candles_slice, mtfcandles_slice













def run_live(strategyClass_dict, portfolio_dict, candles_dict, portfolio, symbol, candles, mtfcandles, param, renko, backtest=0, mtfcandles_dict=None):
    index = len(candles) - 1
    df = None
    
    #print(portfolio, symbol)
    #df = pd.DataFrame(candles)
    #index = len(candles) - 1    
    candle = candles[index]
    candle['totalvolumeday'] = 0;#totalvolumeday(candles, index)
    
    '''
    strat = portfolio 
    modu = "strategy."+strat+'_strategy'
    MyClass = getattr(importlib.import_module(modu), strat)
    strategyClass = MyClass()
    '''
    #print(index)
    #print(portfolio_dict[portfolio])
    strategyClass = strategyClass_dict[portfolio]
    strategyClass.on_tick(df, candles, mtfcandles, index, param, symbol, portfolio, portfolio_dict)
    strategyClass.calculate(df, candles, mtfcandles, index, param, symbol, portfolio, portfolio_dict, candles_dict, renko, backtest, mtfcandles_dict)
    #get_state_analysis(symbol, candles, index, portfolio_dict, portfolio, param, True)    
    #if param['live_trading']:build_trade_table(param)
    return candles, mtfcandles




def create_signal_portfolio(portfolio_dict, portfolio, candles_dict, index, renko_dict, param):
    symbols = portfolio_dict[portfolio]
    #print(portfolio_dict[portfolio])
    #strategyClass = strategyClass_dict[portfolio]
    for symbol in symbols.keys():
        if "CE" in symbol:
            putsymbol = symbol.replace("CE", "PE")
            
            candle = candles_dict[symbol][-1]
            put_candle = candles_dict[putsymbol][-1]
            
            candleclock = candle['datetime'].hour*100+candle['datetime'].minute
            tradeEntryWindow = candleclock>=param['start_time'] and candleclock<=param['stop_order_time']
            tradeExitTimeCondition = candleclock>=param['exit_time']
            
            
            call_buy = renko_dict[symbol][-1]['buy']
            call_sell = renko_dict[symbol][-1]['sell']
            
            put_buy = renko_dict[putsymbol][-1]['buy']
            put_sell = renko_dict[putsymbol][-1]['sell']

            security =  portfolio_dict[portfolio][symbol]
            put_security =  portfolio_dict[portfolio][putsymbol]
            
            if call_buy and put_buy:
                if(security['trade_in']==0 and put_security['trade_in']==0 and tradeEntryWindow):
                    add_buy_order(candle, security, param, 0)
                    add_buy_order(put_candle, put_security, param, 0)
            
            if call_sell or put_sell or tradeExitTimeCondition:
                if(security['trade_in']==1 and put_security['trade_in']==1):
                    add_sell_order(candle, security, param, 0)
                    add_sell_order(put_candle, put_security, param, 0)
     
    return

