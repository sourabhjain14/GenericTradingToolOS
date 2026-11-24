"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import math
import numpy as np
from datetime import datetime,timedelta, date
import pandas as pd
import traceback
import re

import globalvar

from techlib import totalvolumeday
from techlib import vwapday
from techlib import supertrend, calc_renko, calc_rsi, SMACandleKey, EMACandleKey, calc_atr
from techlib import JurikMovingAverage, calculate_option_delta


import importlib
import strategy.eventmanager
importlib.reload(strategy.eventmanager)
from strategy.eventmanager import check_tradewindow, status_intraday_squareoff
from strategy.eventmanager import add_buy_order, add_sell_order, add_short_order, add_cover_order
from strategy.eventmanager import add_target, add_stop_loss, add_trail_stop_loss, add_target_custom

from initialize import g_security_dict

from datahandler import check_strike_filter

class strategy1(object):
    def __init__(self):
        self.state = True
        self.ofs=0
        
    def add_plot(self, var_tuple, param, portfolio, symbol):    
        if var_tuple not in param['indicator_dict'][portfolio][symbol]:
            param['indicator_dict'][portfolio][symbol].append(var_tuple)
            
    def on_tick(self, df, candles, mtfcandles, index, param, symbol, portfolio, portfolio_dict):
        candle = candles[index]
        security =  portfolio_dict[portfolio][symbol]
        ps = param['portfolio_dict'][portfolio][symbol]
    
        now=candles[index]['datetime']
        hour = now.hour
        minute = now.minute
        clocktime = 100*hour+minute
        
        self.MarketHours = 930 <= clocktime and 1600 > clocktime
        self.PreMarket = 400 <= clocktime and 930 > clocktime
        
        
        self.PreMarketOpen = (candle['datetime'].day != candles[index-1]['datetime'].day)
        
        newDay = candle['datetime'].hour==9 and candle['datetime'].minute==30

        
        if portfolio+'trade' not in candle.keys():
            candle[portfolio+'trade'] = 0

        newBar = False
        if security['index']!=index:
            security['index'] = index
            newBar=True

        
        self.newBar = newBar
        
        
        if index==0 and newBar:
            security['trade_today'] = 0

        if index==0 and newBar:
            security['trade_capital'] = param['trade_capital']
            
        if index==0 and newBar:
            security['available_capital'] = param['account_capital']

        if (newDay and newBar):
            security['trade_today'] = 0
            
        
        
        if (index==0 and newBar):
            security['optionATM'] = []
            security['optionITMcall'] = []
            security['optionOTMcall'] = []
            security['optionITMput'] = []
            security['optionOTMput'] = []
        
        
        
        tradewindow = True#check_tradewindow(candles, index, param)  
        #print('window:',tradewindow)
        candle['tradewindow'] = tradewindow


        security['long_signal_fired'] = 0
        security['close_long_signal_fired'] = 0
        security['short_signal_fired'] = 0
        security['close_short_signal_fired'] = 0
        
        
        #for optsym in security['option'].keys():
        #    SUMPNL = SUMPNL +  security['option'][optsym]['sumpnl']
        
        for key in security['option'].keys():
            security['option'][key]['long_signal_fired'] = 0
            security['option'][key]['close_long_signal_fired'] = 0
            security['option'][key]['short_signal_fired'] = 0
            security['option'][key]['close_short_signal_fired'] = 0   
            '''
            if index==0 and newBar:
                security['option'][key]['symbol'] = None
                security['option'][key]['entryprice'] = 0.0
                security['option'][key]['livecumPnL'] = 0.0
            '''
        
        
        if index == 0 and newBar:
            security['backdata'] = []
            security['totalpnl'] = 0.0
            #bd = {"datetime":None,"Symbol":None,"EntryPrice":None,"ExitPrice":None, "Position":None, "EntryValue":None, "ExitValue":None,"PNL":None,"SUM_PNL":None,"Index":None, "comment":None}
            #security['backdata'].append(bd)
        
        buy = portfolio+'_buy'
        sell = portfolio+'_sell'
        sellPrice = portfolio+'_sellPrice'

        short = portfolio+'_short'
        cover = portfolio+'_cover'
        coverPrice = portfolio+'_coverPrice'

        candle[buy] = False
        candle[sell] = False
        candle[short] = False
        candle[cover] = False

        self.tradeLong = param['trade_direction'] == 'BOTH' or param['trade_direction'] == 'LONG'
        self.tradeShort = param['trade_direction'] == 'BOTH' or param['trade_direction'] == 'SHORT'
    
    
        if index==0:
            pass


    def calculate(self, df, candles, mtfcandles, index, param, symbol, portfolio, portfolio_dict, candles_dict, renko):
        #global g_security_dict
        candle = candles[index]
        #print(index)
        #print(symbol)
        #print(candle)
        #print(param['signal_live'])
        timenow_ = datetime.now().replace(microsecond=0)
        timenow = timenow_ if param['live_trading']==True else candle['datetime']
        
        take_trade = param['signal_live'] if param['live_trading'] else True

        syms = portfolio_dict[portfolio]
        
        C = candle['close']
        
        if index>0:
            prev = candles[index-1]
            newDay = candle['datetime'].day > prev['datetime'].day
            if newDay:
                for sym in syms.keys():
                    syms[sym]['cumPnL'] = 0.0 
            
        
        totalPnL=0.0
        #for sym in syms.keys():
        #    totalPnL+=syms[sym]['cumPnL'] 
        trade_table = param['trade_table']
        for trade in trade_table:
            if abs(trade['remaining_position'])>0:
                CTrade = candles_dict[trade['symbol']][-1]['close']
                totalPnL+=((CTrade-trade['EntryPrice'])*param['lot']*trade['remaining_position'])
            totalPnL+=trade['realizedPnL']
        totalPnL=round(totalPnL,2)

        index_symbol = param['index_symbol_option']
        trade_type = "PAPER" if param["PLACE_ORDER"]==False else "REAL"

        universal_profit=0
        if param['live_trading']:
            if index_symbol not in globalvar.g_universalparam['INDEX'].keys():
                globalvar.g_universalparam['INDEX'][index_symbol] = {}
                globalvar.g_universalparam['INDEX'][index_symbol]['trade_type'] = trade_type
                globalvar.g_universalparam['INDEX'][index_symbol]['profit'] = totalPnL
                #print("P1:",globalvar.g_universalparam['INDEX'][index_symbol]['profit'])
            else:
                globalvar.g_universalparam['INDEX'][index_symbol]['trade_type'] = trade_type
                globalvar.g_universalparam['INDEX'][index_symbol]['profit'] = totalPnL
                #print("P2:",globalvar.g_universalparam['INDEX'][index_symbol]['profit'])
    
            for inx in globalvar.g_universalparam['INDEX'].keys():
                universal_profit+=globalvar.g_universalparam['INDEX'][inx]['profit']
                #print("P3:",inx,globalvar.g_universalparam['INDEX'][inx]['profit'])
            if param['live_trading']:
                globalvar.g_universalparam['profit'] = universal_profit
        else:
            universal_profit=totalPnL
            
        if  globalvar.g_universalparam['profit_type']=='Rupee':
            within_max_profit = universal_profit < globalvar.g_universalparam['max_profit']
            within_max_loss = universal_profit > globalvar.g_universalparam['max_loss']    
        elif globalvar.g_universalparam['profit_type']=='Percentage':
            within_max_profit = universal_profit < 0.01 * globalvar.g_universalparam['max_profit'] * globalvar.g_universalparam['overall_investment']
            within_max_loss = universal_profit > 0.01 * globalvar.g_universalparam['max_loss'] * globalvar.g_universalparam['overall_investment']
        #if totalPnL <= param['max_loss']: return
        #globalvar.max_profit =
        #if len(renko)>10:return
        candleclock = candle['datetime'].hour*100+candle['datetime'].minute 
        tradeEntryWindow = candleclock>=param['start_time'] and candleclock<=param['stop_order_time']
        tradeExitTimeCondition = candleclock>=param['exit_time']

        security =  portfolio_dict[portfolio][symbol]
        security['close'] = candle['close']

        #print(portfolio_dict[portfolio])
            
        # trade count
        '''
        trade_count=0
        for s in portfolio_dict[portfolio].keys():
            sy =  portfolio_dict[portfolio][s]
            trade_count = trade_count + abs(sy['trade_in'])
        trade_count_allowed = (trade_count==0) if param['single_trade']==True else True      
        '''
        
        
        call_trade_count=0
        for s in portfolio_dict[portfolio].keys():
            if "CE" in s:
                sy =  portfolio_dict[portfolio][s]
                call_trade_count = call_trade_count + abs(sy['trade_in'])
        call_trade_count_allowed = (call_trade_count==0) if param['single_trade']==True else True 
        
        put_trade_count=0
        for s in portfolio_dict[portfolio].keys():
            if "PE" in s:
                sy =  portfolio_dict[portfolio][s]
                put_trade_count = put_trade_count + abs(sy['trade_in'])
        put_trade_count_allowed = (put_trade_count==0) if param['single_trade']==True else True

        trade_count_allowed = False
        if "CE" in symbol:
            trade_count_allowed = call_trade_count_allowed
        if "PE" in symbol:
            trade_count_allowed = put_trade_count_allowed
            

        
        
                
        
                
        if True:
            if True:
                
                    
                
                
                buy1 = False
                buy2 = False
                buy = buy1 if len(param['signal_list'])==0 else (buy1 and (not buy2))
                sell = False
                #if buy and strike_filter:
                #    print("buy:",symbol, C, timenow)
                short = False
                cover = False



                
                
                
                

                
                buyin = buy if param['trade_direction']=='LONG' else short
                buyout = sell if param['trade_direction']=='LONG' else cover

                

                
                
                '''
                strike_filter=False
                try:
                    indices_close = portfolio_dict[portfolio][param["instrument_index_list"][0]]['close']
                except:
                    return
                '''
                #if buy and security['trade_in']==0:
                #    print("ix:",ix," :index:",index," : ",symbol)
                #    strike_filter = check_strike_filter(param, symbol)   
                #print(symbol, indices_close)
                #print(security['trade_in'], buy, tradeEntryWindow, trade_count_allowed, take_trade)
                #sads=1/0
                position=0
                
                
                if(security['position']==0 and tradeEntryWindow and trade_count_allowed and take_trade and within_max_profit and within_max_loss):
                    #print("ix:",ix," :index:",index," : ",symbol)
                    #strike_filter = check_strike_filter(indices_close, symbol, param)
                    #if strike_filter:
                    if symbol in param['instrument_in_action']:
                        if buy and (param['trade_direction']=='LONG' or param['trade_direction']=='BOTH'):
                            #print("add buy->",symbol,renko_index) 
                            #print("addbuy=>",candle)
                            add_buy_order(candle, security, param, position,'', symbol, portfolio)        
                            if(param['use_target']==True):
                                add_target(param, security)
                            if(param['use_stop_loss']==True):
                                add_stop_loss(param, security)
                        if short and (param['trade_direction']=='SHORT' or param['trade_direction']=='BOTH'):
                            #security['martingale'] = mcount
                            add_short_order(candle, security, param, position,'', symbol, portfolio)        
                            if(param['use_target']==True):
                                add_target(param, security)
                            if(param['use_stop_loss']==True):
                                add_stop_loss(param, security)
                
                #if(security['trade_in']==1 and sell):
                if(security['position']>0 and sell):
                    add_sell_order(candle, security, param, 0,'', symbol, portfolio)
                
                if(security['position']<0 and cover):
                    add_cover_order(candle, security, param, 0,'', symbol, portfolio)
        

        ''' trail '''
        #if(param['use_trail']==True and security['trade_in']==1):
        if(param['use_trail']==True and abs(security['position'])>0):
            add_trail_stop_loss(param, security, candle['close'])

        
        '''
        Exit Orders
        '''
        #within_max_profit
        #if(security['trade_in']==1):
        if(security['position']>0):
            if not within_max_profit:
                print( ":Universal Profit Hit")
                add_sell_order(candle, security, param, 0, ":Universal Profit Hit", symbol, portfolio)
        if(security['position']<0):
            if not within_max_profit:
                print( ":Universal Profit Hit")
                add_cover_order(candle, security, param, 0, ":Universal Profit Hit", symbol, portfolio)

        
        #within_max_loss
        #if(security['trade_in']==1):
        if(security['position']>0):
            if not within_max_loss:
                print( ":Universal Loss Hit")
                add_sell_order(candle, security, param, 0, ":Universal Loss Hit", symbol, portfolio)
        if(security['position']<0):
            if not within_max_loss:
                print( ":Universal Loss Hit")
                add_cover_order(candle, security, param, 0, ":Universal Loss Hit", symbol, portfolio)


        #trail stop
        #if(security['trade_in']==1):
        if(security['position']>0):
            if param['use_trail']==True and security['TSLPrice']>=candle['close']:
                print( ":Trail Stop Hit")
                add_sell_order(candle, security, param, 0, ":Trail Stop Hit", symbol, portfolio)
        if(security['position']<0):
            if param['use_trail']==True and security['TSLPrice']>0 and security['TSLPrice']<=candle['close']:
                print( ":Trail Stop Hit")
                add_cover_order(candle, security, param, 0, ":Trail Stop Hit", symbol, portfolio)
           
        # exit time
        #if(security['trade_in']==1 and tradeExitTimeCondition):
        if(security['position']>0 and tradeExitTimeCondition):
            add_sell_order(candle, security, param, 0,":Time based Exit", symbol, portfolio)
        if(security['position']<0 and tradeExitTimeCondition):
            add_cover_order(candle, security, param, 0,":Time based Exit", symbol, portfolio)


        

        # stop loss
        #if(security['trade_in']==1):
        if(security['position']>0):
            if param['use_stop_loss']==True and security['SLPrice']>=candle['close']:
                print( ":Stop Loss Hit")
                add_sell_order(candle, security, param, 0, ":Stop Loss Hit", symbol, portfolio)
        if(security['position']<0):
            if param['use_stop_loss']==True and security['SLPrice']<=candle['close']:
                print( ":Stop Loss Hit")
                add_cover_order(candle, security, param, 0, ":Stop Loss Hit", symbol, portfolio)
                
        # target
        #if(security['trade_in']==1):
        if(security['position']>0):
            if param['use_target']==True and security['TargetPrice']<=candle['close']:
                print(":Target Hit")
                add_sell_order(candle, security, param, 0, ":Target Hit", symbol, portfolio)
        if(security['position']<0):
            if param['use_target']==True and security['TargetPrice']>=candle['close']:
                print(":Target Hit")
                add_cover_order(candle, security, param, 0, ":Target Hit", symbol, portfolio)

       
        return

        
        
        
   



#END            
