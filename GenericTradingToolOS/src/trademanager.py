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

from IPython.display import display

#from termcolor import colored

#from account import API_KEY, ACCOUNT_ID, REFRESH_TOKEN
#from account import get_access_token

from initialize import g_tick_dict, g_param, g_security_dict
from initialize import g_streamer_connection
#from initialize import g_bar_dict
import globalvar

#import plotly.graph_objects as go 
import matplotlib.pyplot as plt
#pip install https://github.com/matplotlib/mpl_finance/archive/master.zip
#from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import Formatter
#from matplotlib.dates import bytespdate2num, num2date
import matplotlib
#from matplotlib.widgets import Slider
#matplotlib.use('Qt4Agg')
#from plotly import __version__
#print (__version__) # requires version >= 1.9.0
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go


import datahandler
importlib.reload(datahandler)
from datahandler import get_backdata
from datahandler import create_candle, update_candles
from datahandler import get_backdata_index_zerodha#(index, param, candles_dict, timeframe):

import strategylib
importlib.reload(strategylib)
from strategylib import run_live, run_backtest_OHLC_new, create_signal_portfolio

from ordermanager import place_buy, place_sell

#import plotting
from plotting import plot_backtest_charts

from techlib import calc_atr

from initialize import SUMMARYPATH, ANALYSISPATH, PLOTPATH

from widget_lib import item_set_value
from widget_lib import add_global_trade_item_row

from strategy.eventmanager import add_sell_order
from strategy.eventmanager import build_trade_table

from datahandler import check_strike_filter

import zerodha
import livetrade





def on_close_trade_button_clicked_thread(b, candle, security, param, symbol, portfolio):
    add_sell_order(candle, security, param, 0, ":Manual Close", symbol, portfolio)
    


def copytick(instrument_token_list):
    #instrument_token_list = param['instrument_token_list']
    if globalvar.g_copytick==False:
        #globalvar.g_copytick=True
        while(True):
            try:
                #quote = globalvar.g_tick.copy()
                time.sleep(1)
                quote = globalvar.g_kite.quote(instrument_token_list)
                #print(quote)
                for q,v in quote.items():
                    token = v['instrument_token']
                    ltp = v['last_price']
                    #if (ltp<0.05):print(v)
                    if token not in globalvar.g_lastdata.keys():   globalvar.g_lastdata[token] = {}
                    globalvar.g_lastdata[token]['last_price'] = ltp
            except:
                if globalvar.g_kite==None:return
                continue
    return


def candle_updater(candles_dict, param, out_live):
    instrument_symbol_list = param['instrument_symbol_list']
    #timeframe = param['timeframe']
    #frequency = int(param['frequency'])
    #extended_hours = param['extended_hours']
    
    #instrument_option_list = param['instrument_option_list']
    #global g_tick_dict
    instrument_token_dict = param['instrument_token_dict']

    #msg = " :instrument_token_dict: "+str(instrument_token_dict)
    #out_live.append_stdout(msg+'\n')
    instrument_token_list=[]
    if 'quote_instrument_token_list' not in param.keys():
        for key in instrument_token_dict.keys():
            v = instrument_token_dict[key]
            instrument_token_list.append(v) 
        param['quote_instrument_token_list'] = instrument_token_list
    else:
        instrument_token_list = param['quote_instrument_token_list']
    
    
    inverted_token_dict = {}
    if 'quote_inverted_token_dict' not in param.keys():
        for k, v in instrument_token_dict.items():
            inverted_token_dict[v] = k
        param['quote_inverted_token_dict'] = inverted_token_dict
    else:
        inverted_token_dict = param['quote_inverted_token_dict'] 

    #if param['index_symbol_ltp'] == "NSE:NIFTY 50":
    #    instrument_token_list.append(256265)
        
    #indices_dict = globalvar.g_market_dict["INDEX"][param["instrument_index_list"][0]]["1min"][index]
    
    ltp_dict = {}
    try:
        #quote = globalvar.g_kite.quote(instrument_token_list)#[str(instrument_token_list[0])]['last_price']
        #print(quote)
        #quote_df = pd.DataFrame(quote)
        #print(quote_df)
        #ascsd=1/0
        #msg = "quote: "+str(quote)
        #out_live.append_stdout(msg+'\n')
        #ltp_dict[] = quote[str(instrument_token_list[0])]['last_price']
        #for key in instrument_token_dict.keys():
        #    ltp_dict[key] = quote[str(instrument_token_dict[key])]['last_price']
        #ltpindex = quote[str(instrument_token_list[-1])]['last_price']
        #print("ltpindex:",ltpindex)
        
        #quote = globalvar.g_tick.copy()
        #for q in quote:
        #    token = q['instrument_token']
        #    ltp = q['last_price']
        #    ins = inverted_token_dict[token]
        #    ltp_dict[ins] = ltp
        for token in globalvar.g_lastdata.keys():
            try:
                ins = inverted_token_dict[token]
                ltp = globalvar.g_lastdata[token]['last_price']
                ltp_dict[ins] = ltp
            except:
                pass
            
    #for key in instrument_token_dict.keys():
        #    token = instrument_token_dict[key]
        #    #ltp_dict[key] = quote[str(instrument_token_dict[key])]['last_price']
        #    lpr = quote_df.loc[quote_df['instrument_token'] == token, 'last_price']
        #    #print(lpr)
        #    try:
        #        ltp_dict[key] = lpr.values[0]
        #    except:
        #        pass
        
    #print("LTP:=--------------------------------->")
        #print(ltp_dict)
        #msg = str(ltp_dict)
        #out_live.append_stdout(msg+'\n')
    except Exception as e:
        #traceback.print_exc()
        print('quote:',e)
    
    #msg = " :ltp_dict: "+str(ltp_dict)
    #out_live.append_stdout(msg+'\n')
    
    now = datetime.now()
    nowtz = now#.astimezone(tz)
    minute = nowtz.minute
    nowmn = nowtz.hour*60+nowtz.minute
    marketmn = nowmn# - 915
    current_date = now.date()

    for symbol in instrument_symbol_list:
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
                candle['volume'] = 0 
                candles_dict[symbol].append(candle)
                #print(candle)
            else:
                candle['high'] = max(candle['high'], ltp)
                candle['low'] = min(candle['low'], ltp)
                candle['close'] = ltp
                candle['volume'] = candle['volume']+0
        except:
            if newcandle==True:
                old_candle = candles_dict[symbol][-1]
                candle['datetime'] = nowtz
                candle['open'] = old_candle['close']
                candle['high'] = old_candle['close']
                candle['low'] = old_candle['close']
                candle['close'] = old_candle['close']
                candle['volume'] = 0 
                candles_dict[symbol].append(candle)
            #continue    
    
    #globalvar.g_market_dict["INDEX"][param["instrument_index_list"][0]]["1min"] = candles_dict[param["instrument_index_list"][0]]
    #aasas=1/0
    return




def create_trade_table_new(portfolio_dict, candles_dict, param, out_live):
    trade_type = "PAPER" if param["PLACE_ORDER"]==False else "LIVE"
    width = param['trade_table_width']
    scount=0
    counter = 0#globalvar.g_trade_table_counter# if param['trade_table_counter_start']==False else 0
    param['trade_table_counter_start']=True
    
    #siglen = len(globalvar.g_signal_dict[param['index_symbol']])
                
    trade_table = param['trade_table']
    signal_list = param['signal_list']

   
    if ((len(signal_list)//2) + 2) >= (len(param['trade_items']) / param['trade_table_width']):
        add_global_trade_item_row(param)
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
        
        if (abs(sposlast)>0):
            if ('ExitPrice' not in trade.keys()):
                spnl_  = param['lot']*sposlast*(close_price - senp)
            elif ('ExitPrice2' not in trade.keys()):
                spnl_  = trade['ExitPnL'] + param['lot']*sposlast*(close_price - senp)
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
        item_set_value(str(spos), param['trade_items'], 4, scount, width)
        item_set_value(str(shv), param['trade_items'], 5, scount, width)
        
        item_set_value(str(spnl), param['trade_items'], 6, scount, width)
        if True:#sposlast>0:
            if spnl>0:
                param['trade_items'][6+scount*width].style = {'background': 'green'}
            else:
                param['trade_items'][6+scount*width].style = {'background': 'red'}
                            
        
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
                                                       param=param, symbol=symbol, portfolio=portfolio))
                #wbutton.disbaled=True
            else:
                wbutton = param['trade_items'][11+scount*width]
                wbutton.layout.display = 'flex'
                wbutton.disabled = True
                wbutton.style.button_color = 'gray'
        except Exception as e:    
            traceback.print_exc()
            out_live.append_stdout(str(e)+'\n')
    return
    
    
   

    
def live_trade(strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, out_live, out_live_table, out_live_position, renko_dict):
    RUN_FOR_MINUTES = param['RUN_FOR_MINUTES']
    #UPDATE_TICK_DATA_SECONDS = param['UPDATE_TICK_DATA_SECONDS']
    #TRADE_LIVE = param['TRADE_LIVE']
    #ALLOW_SHORT = param['ALLOW_SHORT']
    PLACE_ORDER = param['PLACE_ORDER']
    #LOT_dict = param['LOT_dict']
    
    instrument_symbol_list = param['instrument_symbol_list']
    #timeframe = param['timeframe']
    #frequency = int(param['frequency'])
    #extended_hours = param['extended_hours']
    
    #allow_unauthenticated_requests = param['allow_unauthenticated_requests']
    
    instrument_option_list = param['instrument_option_list']
    
    #tz = pytz.timezone('US/Eastern')
    #global g_streamer_connection
    #global g_param
    #global g_bar_dict
    #g_param['RUN_FOR_MINUTES'] = param['RUN_FOR_MINUTES']
    
    
    now = datetime.now()  
    nowtz = now#.astimezone(tz)
    new_now = nowtz
    old_minute=nowtz.minute-1
    
    now = datetime.now()#.date()
    date_str = now.strftime('%Y-%m-%d-%H%M')
    summary_filename = SUMMARYPATH+param['index_symbol_option']+"-LiveSignal-"+date_str+".csv"
    #print()
    
    i=0
    i_acc=0
    candles_live=None
    
    
    with open(ANALYSISPATH+"log.txt",'a') as livelog:
        livelog.write("\n----starting livetrade : "+str(nowtz)+"----------\n")
    
    
    space_='\t \t \t'

    
    #print(now)
    log_flag = False
    strategy_flag=False
    dbg_flag=False
    
    qq=0
    
    MarketHours = False 
    subscribe_ticker=False
    ACCESS_TOKEN = None    
    param_backtest_length=0
    
    print("loop BEGINS")
    out_live.append_stdout('STARTING LIVE RUN'+'\n')
    #globalvar.g_param['RUN_FOR_MINUTES'] = param['RUN_FOR_MINUTES'] 
    streamer=False
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
        
        
        OffHours = clocktime<915 or clocktime>1530
        
        OldMarketHours=MarketHours
        MarketHours = 915 <= clocktime and 1530 >= clocktime 
        
       
        new_minute=nowtz.minute
        new_second = nowtz.second
        if new_minute!=old_minute:
            if OffHours==True:
                #time.sleep(1200)
                #HARDCODE
                #time.sleep(1)
                #nowtz = nowtz + timedelta(minutes=20)
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
            log_flag = True
            table_flag = True
            position_flag = True
            #dbg_flag = True
            strategy_flag=True
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



        # run scanner and import scanned instrument history and run backdata
        #datahander.run_scanner(param)
        #build_scanner_data(strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, renko_dict)
        if streamer==False:
            instrument_token_dict = param['instrument_token_dict']
            instrument_token_list=[]
            for key in instrument_token_dict.keys():
                v = instrument_token_dict[key]
                instrument_token_list.append(v) 
            param['instrument_token_list'] = instrument_token_list
            #if globalvar.g_kiteticker==None:
            #    zerodha.create_stream(instrument_token_list)
            #else:
            #    zerodha.add_stream(instrument_token_list)
            
            streamer_thread = Thread(target=copytick,args=(instrument_token_list,))
            streamer_thread.start()
            #streamer_thread.join()
            streamer=True
        
        
        if dbg_flag==True:print("candle updater in: ",datetime.now())
        wait_time = int(param['update_frequency'])
        time.sleep(wait_time)
        candle_updater(candles_dict, param, out_live)
        if dbg_flag==True:print("candle updater out: ",datetime.now()) 
        
        
        
        '''-------------------------- strategy calculations--------------------------'''
        if dbg_flag==True:
            print("strategy in: ",datetime.now())


        candleclock = now.hour*100+now.minute 
        tradeEntryWindow = candleclock>=param['start_time'] and candleclock<=param['stop_order_time']
        tradeExitTimeCondition = candleclock>=param['exit_time']
        
        for portfolio in portfolio_dict.keys():
            symbols = portfolio_dict[portfolio]
            for symbol in symbols.keys():
                mtfcandles = mtfcandles_dict[symbol]
                candles_dict[symbol], mtfcandles = run_live(strategyClass_dict, portfolio_dict, candles_dict, 
                                                            portfolio, symbol, candles_dict[symbol], 
                                                            mtfcandles, param, renko_dict[symbol])

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
        
        
        
        '''
        for portfolio in portfolio_dict.keys():
            symbols = portfolio_dict[portfolio]
            for symbol in symbols.keys():
                security = symbols[symbol]
                if len(security['backdata']) > param_backtest_length:
                    print(security['backdata'])
                    param_backtest_length = len(security['backdata'])
        '''

        #------------create trade table-------------------
        create_trade_table_new(portfolio_dict, candles_dict, param, out_live)


        #----------------strike display---------------------
        indices_close = candles_dict[param['index_symbol'][0]][-1]['close']
        param['index_value_w'].value = indices_close
        for portfolio in portfolio_dict.keys():
            symbols = portfolio_dict[portfolio]
            for symbol in symbols.keys():
                    #strike_filter = check_strike_filter(indices_close, symbol, param)
                    strike_filter = symbol in param['instrument_in_action'] 
                    if strike_filter==True:
                        if "CE" in symbol:
                            param['selected_strike_call_w'].value = symbol
                            param['selected_strike_call_value_w'].value = candles_dict[symbol][-1]['close']
                            #globalvar.g_param['selected_strike_call_signal_w'].value = 1 if renko_dict[symbol][-1]['buy_signal'] else 0
                            param['selected_strike_call_signal_w'].value = renko_dict[symbol][-1]['buy_signal']
                            try:
                               param['selected_strike_call_signal_time_w'].value = str(renko_dict[symbol][-1]['buy_signal_datetime'])
                            except:
                                pass
                            try:
                               param['selected_strike_call_signal_fos_w'].value = str(renko_dict[symbol][-1]['fos'])
                            except:
                                pass
                        if "PE" in symbol:
                            param['selected_strike_put_w'].value = symbol
                            param['selected_strike_put_value_w'].value = candles_dict[symbol][-1]['close']
                            param['selected_strike_put_signal_w'].value = renko_dict[symbol][-1]['buy_signal']
                            try:
                               param['selected_strike_put_signal_time_w'].value = str(renko_dict[symbol][-1]['buy_signal_datetime'])
                            except:
                                pass
                            try:
                               param['selected_strike_put_signal_fos_w'].value = str(renko_dict[symbol][-1]['fos'])
                            except:
                                pass
        '''
        try:
            signal_list = param['signal_list']
            totalPnL=0.0
            for sig in signal_list:
                if sig['position']>0:
                    if sig['status_open']==True:
                        if 'unrealized_pnl' in sig.keys():
                            totalPnL+=sig['unrealized_pnl']
                else:
                    totalPnL+=sig['PnL']
            globalvar.g_param['total_pnl_w'].value = totalPnL
        except:
            pass
        '''

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

 
        
        
        
        
        
        '''------------------output log--------------------------------'''
        if log_flag == True:
            if param['show_detail_log']==True and i==1:
                msg = "symbol"+"\t\t"+"position"+"\t"+"entryprice"+"\t"+"holdingvalue"
                msg = msg+"\t"+"close"+"\t"+"renko"+"\t"+"supertrend"
                out_live.append_stdout(msg+'\n')
                
            dfltp = pd.DataFrame(columns=['price'])
            for portfolio in portfolio_dict.keys():
                symbols = portfolio_dict[portfolio]
                scount=0
                for symbol in symbols.keys():
                    scount+=1
                    security = portfolio_dict[portfolio][symbol]
                    candles_live = candles_dict[symbol]
                    candledate_ = candles_live[-1]['datetime']
                    candlemn_ = candledate_.hour*60+candledate_.minute
                    clockmn_ = 60*nowtz.hour+nowtz.minute

                    renko_live = renko_dict[symbol]
                    #print("Live:",candles_live[-1]['datetime'], candlemn_ , clockmn_)
                    #print(symbol)
                    #print(candlemn_, clockmn_)
                    #msg = symbol+" : "+str(candlemn_)+" : "+str(clockmn_)
                    #out_live.append_stdout(msg+'\n')
                    
                    if candlemn_ < clockmn_:
                        continue
                    
                    #msg = "CANDLE->"+portfolio+":"+symbol+" : " +str(candles_live[-1]['datetime'])+' '+str(candles_live[-1]['close'])
                    #param['live_output']+=str(msg)
                    #out_live.append_stdout(msg+'\n')
                    
                    #dfltp.loc[symbol] = [candles_live[-1]['close']]
                    #renko_live = renko_dict[symbol]
                    if param['show_detail_log']==True:#out_live.clear_output()
                        indices_close = portfolio_dict[portfolio][param["instrument_index_list"][0]]['close']
                        strike_filter = check_strike_filter(indices_close, symbol, param)
                        if strike_filter:
                            msg = "RENKO->"+symbol+" : " +str(security['brick_size'])+' : '+str(indices_close) + " : " + str(renko_live[-1]['close'])
                            out_live.append_stdout(msg+'\n')
                        if security['trade_in']:
                            msg = "TRADEIN->"+symbol+" : " + str(renko_live[-1]['trend'])
                            out_live.append_stdout(msg+'\n')
                    
                    #param['live_output']+=str(msg)
                    #out_live.append_stdout(msg+'\n')
                    # if len(security['signal'])>0

                    
                    
                    #try:
                    #    item_set_value(symbol, globalvar.g_param['trade_items'], 0, scount)
                    #    item_set_value(str(candles_live[-1]['close']), globalvar.g_param['trade_items'], 1, scount)
                    #    item_set_value(str(security['position']), globalvar.g_param['trade_items'], 2, scount)
                    #except:
                    #    pass
                    
                    if param['show_detail_log']==True and security['trade_in'] == True:
                        #msg = "RENKO->"+portfolio+":"+symbol+" : " +str(renko_live[-1]['datetime'])+' '+str(renko_live[-1]['close'])
                        msg = symbol+"\t"+str(security['position'])+"\t"+str(security['entryprice'])+"\t\t"+str(round(security['holdingvalue'],2))
                        msg = msg+"\t\t"+str(candles_live[-1]['close'])+"\t"+str(round(renko_live[-1]['close'],2))+"\t"+str(renko_live[-1]['trend'])
                        msg = msg+"\t"+str(security['signal'][-1]['live'])+"\t"+str(security['signal'][-1]['datetime'])
                        out_live.append_stdout(msg+'\n')

            '''
            try:
                write_signal_output(portfolio_dict, param, summary_filename, out_live)    
            except Exception as e:    
                traceback.print_exc()
                out_live.append_stdout(str(e)+'\n')
            '''
            write_trade_table_file(param,summary_filename)
            log_flag = False
            #out_live_table.clear_output()
            #msg = str(dfltp)
            #out_live_table.append_stdout(msg+'\n')
            #with out_live_table:
            #    display(dfltp)
           
        '''---------------------------------order management-------------------------------------------'''
        if dbg_flag==True:
            print("order in: ",datetime.now())
        
        #for security in portfolio_dict[portfolio].keys()
        #option_set_enter = ['C2','P1','C1','P2']
        #option_set_exit = ['C1','P2','C2','P1']
        
        if param['PLACE_ORDER']:
            exchange = param['index_exchange']
            for portfolio in portfolio_dict.keys():
                symbols = portfolio_dict[portfolio]
                for symbol in symbols.keys():
                    #candles_live = candles_dict[symbol]
                    security = portfolio_dict[portfolio][symbol]
                    quantity = int(security['position']*param['lot'])
                    #if security['trade_in']==1:print("in place order:",security)
                    ''' ZERODHA '''
                    if param['trade_zerodha']==True:
                        if security['long_signal_fired'] == 1:
                            #print("in place buy zerodha:")
                            quantity = int(security['signal'][-1]['position']*param['lot'])
                            if param['index_symbol_option']=='BANKEX':
                                d=(security['close']//0.05)*0.05
                                pr = round(d,2)
                                place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity, price=pr)
                            else:
                                place_buy(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, quantity=quantity)
                        
                        if security['close_long_signal_fired'] == 1:
                            quantity = int(security['signal'][-1]['position']*param['lot'])
                            if param['index_symbol_option']=='BANKEX':
                                d=(security['close']//0.05)*0.05
                                pr = round(d,2)
                                place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity, price=pr)
                            else:
                                place_sell(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, quantity=quantity)
                        
                        if security['short_signal_fired'] == 1:
                            #print("in place buy zerodha:")
                            quantity = int(security['signal'][-1]['position']*param['lot'])
                            if param['index_symbol_option']=='BANKEX':
                                d=(security['close']//0.05)*0.05
                                pr = round(d,2)
                                place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                           quantity=quantity, price=pr, short_flag=1)
                            else:
                                place_sell(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                           quantity=quantity, short_flag=1)
                        
                        if security['close_short_signal_fired'] == 1:
                            quantity = int(security['signal'][-1]['position']*param['lot'])
                            if param['index_symbol_option']=='BANKEX':
                                d=(security['close']//0.05)*0.05
                                pr = round(d,2)
                                place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                          quantity=quantity, price=pr)
                            else:
                                place_buy(exchange=exchange, broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, 
                                          quantity=quantity)

                    ''' FINVASIA '''
                    if param['trade_finvasia']==True:
                        if security['long_signal_fired'] == 1:
                            quantity = int(security['signal'][-1]['position']*param['lot'])
                            if param['index_symbol_option']=='BANKEX':
                                d=(security['close']//0.05)*0.05
                                pr = round(d,2)
                                place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity, price=pr)
                            else:
                                place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity)
                        
                        if security['close_long_signal_fired'] == 1:
                            quantity = int(security['signal'][-1]['position']*param['lot'])
                            if param['index_symbol_option']=='BANKEX':
                                d=(security['close']//0.05)*0.05
                                pr = round(d,2)
                                place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity, price=pr)
                            else:
                                place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity)
                        
                        if security['short_signal_fired'] == 1:
                            quantity = int(security['signal'][-1]['position']*param['lot'])
                            if param['index_symbol_option']=='BANKEX':
                                d=(security['close']//0.05)*0.05
                                pr = round(d,2)
                                place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                           quantity=quantity, price=pr, short_flag=1)
                            else:
                                place_sell(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, 
                                           quantity=quantity, short_flag=1)
                        
                        if security['close_short_signal_fired'] == 1:
                            quantity = int(security['signal'][-1]['position']*param['lot'])
                            if param['index_symbol_option']=='BANKEX':
                                d=(security['close']//0.05)*0.05
                                pr = round(d,2)
                                place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity, price=pr)
                            else:
                                place_buy(exchange=exchange, broker="finvasia",broker_object=globalvar.g_shoonya, symbol=symbol, quantity=quantity)
        
                    #if param['use_stop_loss']==True and security['trade_in']>0 and security['SLPrice']>=security['close']:
                    #    place_sell(broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, quantity=quantity)
                    
                    #if param['use_target']==True and security['trade_in']>0 and security['TargetPrice']<=security['close']:
                    #    place_sell(broker="zerodha",broker_object=globalvar.g_kite, symbol=symbol, quantity=quantity)
                        
                        

                   
        if dbg_flag==True:
            print("order out: ",datetime.now())
            dbg_flag=False
    '''--------------------------------end of loop------------------------------------------'''        
    param['RUN_FOR_MINUTES'] = 0
    #g_param['RUN_FOR_MINUTES'] = 0
    #print('joining thread')
    #tick_thread.join()
    print("loop ENDS")    
    
    
    
    




    

def run_system(param=None, backdata=None, out_live=None, out_live_table=None, out_live_position=None, ibprogram=None):
    instrument_symbol_list = [] #param['instrument_symbol_list']
    #for portfolio in param['portfolio_dict'].keys():
    #    symbols = param['portfolio_dict'][portfolio]
    #    for symbol in symbols.keys():
    #        if symbol not in instrument_symbol_list:
    #            instrument_symbol_list.append(symbol)
    #param['signal_list'] = []
    
    param['instrument_symbol_list'] =  instrument_symbol_list       
    print('portfolio symbol unique list:',param['instrument_symbol_list'])        
    
    param['instrument_in_action'] =  []      
    
    RUN_FOR_MINUTES = param['RUN_FOR_MINUTES']
    #UPDATE_TICK_DATA_SECONDS = param['UPDATE_TICK_DATA_SECONDS']
    #TRADE_LIVE = param['TRADE_LIVE']
    #ALLOW_SHORT = param['ALLOW_SHORT']
    PLACE_ORDER = param['PLACE_ORDER']
    #LOT_dict = param['LOT_dict']
    
    
    #timeframe = param['timeframe']
    #frequency = param['frequency']
    #extended_hours = param['extended_hours']
    #periodType = param['periodType']
    #period = param['period']
    
   
    
    mtf_list = ['1min','2min','3min','4min','5min','10min','15min','20min','30min','60min','240min','1D','1W','1M','1Y']
    mtfcandles_dict = {}
    temp_instrument_symbol_list = ['RELIANCE']
    for symbol in temp_instrument_symbol_list:
        mtfcandles_dict[symbol] = {}
        mtfcandles = mtfcandles_dict[symbol]
        mtfcandles['1min'] = {}
        mtfcandles['2min'] = {}
        mtfcandles['3min'] = {}
        mtfcandles['4min'] = {}
        mtfcandles['5min'] = {}
        mtfcandles['10min'] = {}
        mtfcandles['15min'] = {}
        mtfcandles['20min'] = {}
        mtfcandles['30min'] = {}
        mtfcandles['60min'] = {}
        mtfcandles['240min'] = {}
        mtfcandles['1D'] = {}
        mtfcandles['1W'] = {}
        mtfcandles['1M'] = {}
        mtfcandles['1Y'] = {}
    #print(mtfcandles_dict)
    '''
    globalvar.g_market_dict = {"INDEX":{}, "EQUITY":{}, "OPTION":{},"FUTURES":{},"FOREX":{}}
    market_dict = globalvar.g_market_dict
    atr_timeframe = str(param["index_atr_timeframe_hour"])+"H"
    #market_dict["INDEX"][atr_timeframe] = {}
    #market_dict["INDEX"]["1min"] = {}
    for indices in param['instrument_index_list']:
        market_dict["INDEX"][indices] = {}
        market_dict["INDEX"][indices][atr_timeframe] = get_backdata_index_zerodha(indices, param, atr_timeframe)[indices]
        market_dict["INDEX"][indices]["1min"] = get_backdata_index_zerodha(indices, param, '1min')[indices]
    #print(market_dict)
    #return
    '''
    # candles                
    candles_dict = {}
    param['instrument_option_list'] = []
    '''
    Renko Dictionary
    '''
    renko_dict = {}

    #globalvar.g_market_dict = {"INDEX":{}, "EQUITY":{}, "OPTION":{},"FUTURES":{},"FOREX":{}}

    #print("IN HISTORY IMPORT")
    #print(datetime.now())
    msg="IN HISTORY: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    if True:#param['live_trading']==False:
        if backdata is None:
            historyData_dict = get_backdata(param, mtfcandles_dict)
            #print(param)
            if historyData_dict is None:
                return None
            # create detailed candle properties 
            candles_dict = historyData_dict.copy()
            if param['show_detail_log']: print(candles_dict.keys())
            #market_dict["OPTION"] = candles_dict
            #param['instrument_symbol_list'] = list(candles_dict.keys())
            
            #for ix in globalvar.g_market_dict["INDEX"].keys():
            #    candles_dict[ix] = globalvar.g_market_dict["INDEX"][ix]["1min"]
                #param['instrument_symbol_list'].append(ix)
            
            instrument_symbol_list = param['instrument_symbol_list']
            for symbol in instrument_symbol_list:
                for candle_ in candles_dict[symbol]:
                    candle_ = create_candle(candle_)
            #for symbol in instrument_symbol_list:
            #    firstcandle = candles_dict[symbol][0]
            #    for key in firstcandle.keys():
            #        if '_average' in key:
            #            opslocal = key.replace('_average','')
            #            param['instrument_option_list'].append(opslocal)
            #print("instrument_option_list:",param['instrument_option_list'])
        else:
            candles_dict = backdata.copy()
            for symbol in instrument_symbol_list:
                for candle_ in candles_dict[symbol]:
                    candle_ = create_candle(candle_)
    #print("OUT HISTORY IMPORT")
    #print(datetime.now())
    msg="OUT HISTORY: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    
       
    #print(candles_dict)
    for symbol in instrument_symbol_list:
        if param['show_detail_log']: print(candles_dict[symbol][-1])
        #print(candles_dict[symbol][list(candles_dict.keys())[-1]])

    for symbol in instrument_symbol_list:
        renko_dict[symbol] = []

    mtf_list = ['1min','2min','3min','4min','5min','10min','15min','20min','30min','60min','240min','1D','1W','1M','1Y']
    mtfcandles_dict = {}
    for symbol in instrument_symbol_list:
        mtfcandles_dict[symbol] = {}
        mtfcandles = mtfcandles_dict[symbol]
        mtfcandles['1min'] = {}
        mtfcandles['2min'] = {}
        mtfcandles['3min'] = {}
        mtfcandles['4min'] = {}
        mtfcandles['5min'] = {}
        mtfcandles['10min'] = {}
        mtfcandles['15min'] = {}
        mtfcandles['20min'] = {}
        mtfcandles['30min'] = {}
        mtfcandles['60min'] = {}
        mtfcandles['240min'] = {}
        mtfcandles['1D'] = {}
        mtfcandles['1W'] = {}
        mtfcandles['1M'] = {}
        mtfcandles['1Y'] = {}
    
    

    
    '''
    indicator initialization
    '''    
    #portfolio_dict =  param['portfolio_dict'].copy()
    for portfolio in param['portfolio_dict'].keys():
        param['indicator_dict'][portfolio] = {} 
        for symbol in instrument_symbol_list:
             param['indicator_dict'][portfolio][symbol] = []

    
    '''
    portfolio initialization
    '''    
    #portfolio_dict =  param['portfolio_dict'].copy()
    for portfolio in param['portfolio_dict'].keys():
        param['portfolio_dict'][portfolio] = {} 
        for symbol in instrument_symbol_list:
             param['portfolio_dict'][portfolio][symbol] = {}


    '''
    signal initialization
    ''' 
    #signal_list = []
    #globalvar.g_signal_dict[param['index_symbol']] = []
    param['signal_list'] = []

    '''
    trade table initialization
    ''' 
    param['trade_table'] = []

    
    print(param)
    
    portfolio_dict =  param['portfolio_dict']
    for portfolio in portfolio_dict.keys():
        symbols = portfolio_dict[portfolio]
        for symbol in symbols.keys():
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
            security['available_capital'] = param['account_capital']  
            
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
            
            #security['option']['signal'] = []

    #importlib.reload(TraderSystem)
    
    strategyClass_dict = {}
    for portfolio in portfolio_dict.keys():
        modu = "strategy."+portfolio+'_strategy'
        #MyClass = getattr(importlib.import_module(modu), portfolio)
        MyClass = getattr(importlib.reload(importlib.import_module(modu)), portfolio)
        #importlib.reload(MyClass)
        strategyClass = MyClass()
        strategyClass_dict[portfolio] = strategyClass
        #portfolio_dict[portfolio]['strategyClass'] = strategyClass
    
    
    #print(candles_dict.keys())
    #print(mtfcandles_dict.keys())
    
    indices = param['instrument_index_list'][0]
    atr_timeframe = str(param["index_atr_timeframe_hour"])+"H"
    indices_candles =  globalvar.g_market_dict["INDEX"][indices][atr_timeframe] #candles_dict[indices]
    indices_index = len(indices_candles) - 1
    indices_atr_period = param['index_atr_period']
    for i in range(len(indices_candles)):
        #print(i)
        #print(indices_candles[i])
        indices_candles[i]['atr'] = calc_atr(indices_candles, i, indices_atr_period)
        #print(indices_candles[i])
        iatr = indices_candles[i]['atr']
        #print(iatr)
        inum = param["index_atr_timeframe_hour"]*60
        itflower = inum / param['index_atr_lowertimeframe']
        iatrlower = iatr / itflower
        brick_size = iatrlower
        indices_candles[i]['brick_size'] = brick_size
        #param['brick_size'] = brick_size
        #print(param['brick_size'])
        
    #''' prepare data for entire history'''
    '''
    if True:#param['live_trading']==False:
        for portfolio in portfolio_dict.keys():
            symbols = portfolio_dict[portfolio]
            for symbol in symbols.keys():
                #candles = candles_dict[symbol].copy()
                #candles_dict[symbol] = run_backtest(portfolio_dict, portfolio, symbol, candles_dict[symbol], param)
                candles_dict[symbol], mtfcandles_dict[symbol] = run_backtest_OHLC_new(strategyClass_dict, portfolio_dict, 
                                                                                      portfolio, symbol, candles_dict[symbol], 
                                                                                      param, mtfcandles_dict[symbol], 0, renko_dict[symbol])
    '''
    #print("IN BACKTEST: ",datetime.now())
    msg="IN BACKTEST: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    #print(datetime.now())
    if True:#param['live_trading']==False:
        param['signal_live'] = False
        for portfolio in portfolio_dict.keys():
            run_backtest_OHLC_new(strategyClass_dict, portfolio_dict, portfolio, candles_dict, param, mtfcandles_dict, 0, renko_dict)
            #for index in range(len(candles_dict[symbol])):
            #    create_signal_portfolio(portfolio_dict, portfolio, candles_dict, index, renko_dict, param)            
    #print("OUT BACKTEST: ",datetime.now())
    msg="OUT BACKTEST: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    #print(datetime.now())
    build_trade_table(param)
    write_trade_table_file(param)
    #print(portfolio_dict.keys())        
    #for portfolio in portfolio_dict.keys():
    #    symbol = portfolio_dict[portfolio]
    #    print(mtfcandles_dict[symbol]['2min'][-1])
    
    #print(renko_dict)
    
    #df_renko = pd.DataFrame(renko_dict)
    #df_renko.to_csv('./renkodata.csv')
    
    '''
    BACKTEST SUMMARY
    '''
    '''
    if param['live_trading']==False:
        for portfolio in portfolio_dict.keys():
            #dfsum = pd.DataFrame()
            symbols = portfolio_dict[portfolio]
            count=0
            for symbol in symbols.keys():
                security = portfolio_dict[portfolio][symbol]
                signal = security['signal']
                dfsig = pd.DataFrame(signal)
                dfsig['symbol'] = symbol
                if count==0: dfsum = pd.DataFrame(columns=dfsig.columns)
                dfsum = pd.concat([dfsum, dfsig], ignore_index=True)
                count+=1
            df_sorted = dfsum.sort_values(by='datetime')
            df_sorted['cumPnL'] = df_sorted['PnL'].cumsum()
            display(df_sorted)
            print("PnL GRAND SUM:",df_sorted['PnL'].sum())
            df_sorted.to_csv("./summary/BacktestSignal.csv")
    '''
    #try:
    #    write_signal_output(portfolio_dict, param)
    #except Exception as e:
    #    traceback.print_exc()
    '''
    PLOT RENKO
    '''
    if param['show_plot'] and param['live_trading']==False:
        for portfolio in portfolio_dict.keys():
                symbols = portfolio_dict[portfolio]
                for symbol in symbols.keys():
                    security = portfolio_dict[portfolio][symbol]
                    signal = security['signal']
                    dfsig = pd.DataFrame(signal)
                    plot_renko(symbol, renko_dict[symbol], dfsig, param)
    
    #for symbol in renko_dict.keys():
    #    plot_renko(symbol, renko_dict[symbol])
    ####return
    #for symbol in renko_dict.keys():
    #    plot_backtest_charts(portfolio=None, symbol='AAPL', timeframe='minute', frequency='1', periodType='day', period='2', params=None, tradeDirection="LONG", extended_hours=False, candles_dict=None, indicator_list=None, portfolio_dict=None):
        #plot_renko(symbol, renko_dict[symbol])

    #print("IN LIVE: ",datetime.now())
    msg="IN LIVE: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    ''' run live trade system ''' 
    #param['RUN_FOR_MINUTES'] = 100
    RUN_FOR_MINUTES = param['RUN_FOR_MINUTES']
    if RUN_FOR_MINUTES>0:
        print("run live_trade")
        param['instrument_in_action'] = []
        param['signal_live'] = True
        live_trade(strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, out_live, out_live_table, out_live_position, renko_dict)
    #print("OUT LIVE: ",datetime.now())
    msg="OUT LIVE: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    '''
    for portfolio in portfolio_dict.keys():
        symbols = portfolio_dict[portfolio]
        for symbol in symbols.keys():
            security = symbols[symbol]
            dfsignal = pd.DataFrame(security['signal'])
            #print(dfsignal)
            #display(dfsignal)
            dfsignal.to_csv(ANALYSISPATH+portfolio+"_"+symbol+str(param['backtest_date1'])+'_BACKTEST.csv')
    '''        
    
    return candles_dict, portfolio_dict
    #return
      
    #print("------------Equity Backtest Analysis------------")
    backtest_analysis_dict={}
    grandPnL = 0.0
    ''' post process file '''
    for portfolio in portfolio_dict.keys():
        backtest_analysis_dict[portfolio] = {}
        symbols = portfolio_dict[portfolio]
        for symbol in symbols.keys():
            backtest_analysis_dict[portfolio][symbol] = {}
            ba = backtest_analysis_dict[portfolio][symbol]
            try:
                security = symbols[symbol]
                    
                dfsignal = pd.DataFrame(security['signal'])

                #print(dfsignal)
                
                if param['tradeDirection'] == 'LONG':
                    dfsignal['Short'] = ''
                    dfsignal['CloseShort'] = ''
                    dfsignal['ShortPrice'] = ''
                    dfsignal['CloseShortPrice'] = ''
                    dfsignal['ShortPriceTime'] = ''
                
                if param['tradeDirection'] == 'SHORT':
                    dfsignal['Long'] = ''
                    dfsignal['CloseLong'] = ''
                    dfsignal['LongPrice'] = ''
                    dfsignal['CloseLongPrice'] = ''
                    dfsignal['LongPriceTime'] = ''     
                
                if 'Short' not in dfsignal.columns:
                    dfsignal['Short'] = ''
                if 'CloseShort' not in dfsignal.columns:
                    dfsignal['CloseShort'] = ''
                if 'ShortPrice' not in dfsignal.columns:
                    dfsignal['ShortPrice'] = ''
                if 'CloseShortPrice' not in dfsignal.columns:
                    dfsignal['CloseShortPrice'] = ''
                if 'ShortPriceTime' not in dfsignal.columns:
                    dfsignal['ShortPriceTime'] = ''
                
                
                if 'Long' not in dfsignal.columns:
                    dfsignal['Long'] = ''
                if 'CloseLong' not in dfsignal.columns:
                    dfsignal['CloseLong'] = ''
                if 'LongPrice' not in dfsignal.columns:
                    dfsignal['LongPrice'] = ''
                if 'CloseLongPrice' not in dfsignal.columns:
                    dfsignal['CloseLongPrice'] = ''
                if 'LongPriceTime' not in dfsignal.columns:
                    dfsignal['LongPriceTime'] = ''
                 
                #print(dfsignal.head())
                
                
                dfsignal[['LongPrice','ShortPrice']] = dfsignal[['LongPrice','ShortPrice']].fillna(method='ffill')
                
                #print(dfsignal.head())

                dfsignal['LongPriceTime'] = dfsignal[dfsignal['Long']==True]['datetime']
                dfsignal['ShortPriceTime'] = dfsignal[dfsignal['Short']==True]['datetime']
                dfsignal[['LongPriceTime','ShortPriceTime']] = dfsignal[['LongPriceTime','ShortPriceTime']].fillna(method='ffill')

                
                dfsignal['LongHoldingPeriod'] = (dfsignal[dfsignal['CloseLong']==True]['datetime']\
                                                -dfsignal[dfsignal['CloseLong']==True]['LongPriceTime'])
                dfsignal['ShortHoldingPeriod'] = (dfsignal[dfsignal['CloseShort']==True]['datetime']\
                                                -dfsignal[dfsignal['CloseShort']==True]['ShortPriceTime'])
                
                
                dfsignal['LongPosition'] = dfsignal[dfsignal['Long']==True]['position']
                dfsignal['ShortPosition'] = dfsignal[dfsignal['Short']==True]['position']
                #dfsignal[['LongPosition','ShortPosition']] = dfsignal[['LongPosition','ShortPosition']].fillna(method='ffill')
                
                
                dfsignal['lastposition'] = dfsignal['position'].shift(1)
                
                dfsignal['LongPnL'] = (dfsignal[dfsignal['CloseLong']==True]['lastposition'] - dfsignal[dfsignal['CloseLong']==True]['position'])*(dfsignal[dfsignal['CloseLong']==True]['CloseLongPrice']-dfsignal[dfsignal['CloseLong']==True]['LongPrice'])
                
                dfsignal['ShortPnL'] = (dfsignal[dfsignal['CloseShort']==True]['lastposition'] - dfsignal[dfsignal['CloseShort']==True]['position'])*(dfsignal[dfsignal['CloseShort']==True]['CloseShortPrice']-dfsignal[dfsignal['CloseShort']==True]['ShortPrice'])
                
                
                #print(dfsignal.head())
                
                #-----------writing postprocessed output
                dfsignal = dfsignal.reindex(columns=(list([a for a in dfsignal.columns if a != 'comment'])+['comment']  ))
                dfsignal.to_csv('./data/'+portfolio+"_"+symbol+'_POSTPROCESSED_BACKTEST.csv')
                
                
                ba['LongTradeCount'] = dfsignal[dfsignal['Long']==True]['Long'].count()
                ba['ShortTradeCount'] = dfsignal[dfsignal['Short']==True]['Short'].count()
                ba['TradeCount'] = dfsignal[dfsignal['Long']==True]['Long'].count()+dfsignal[dfsignal['Short']==True]['Short'].count()
                
                ba['LongPnL'] = round(dfsignal['LongPnL'].sum(),2)
                ba['ShortPnL'] = round(dfsignal['ShortPnL'].sum(),2)
                ba['PnL'] = round(dfsignal['LongPnL'].sum() + dfsignal['ShortPnL'].sum(),2)
                
                grandPnL += ba['PnL']
                
                ba['LongPositionAvg'] = round(dfsignal['LongPosition'].mean(),2)
                ba['ShortPositionAvg'] = round(dfsignal['ShortPosition'].mean(),2)
                
                tmp=0
                try:
                    tmp = (dfsignal['LongPosition'].sum()+dfsignal['ShortPosition'].sum())\
                            /(dfsignal['LongPosition'].count()+dfsignal['ShortPosition'].count())
                except:
                    tmp=0
                backtest_analysis_dict[portfolio][symbol]['PositionAvg'] = round(tmp,2)
                
                
                ba['LongHoldPeriodAvg(min)'] = round(dfsignal['LongHoldingPeriod'].mean().total_seconds() / 60,2)
                ba['ShortHoldPeriodAvg(min)'] = round(dfsignal['ShortHoldingPeriod'].mean().total_seconds() / 60,2)
                tmp=0
                try:
                    tmp = (dfsignal['LongHoldingPeriod'].sum()+dfsignal['ShortHoldingPeriod'].sum())\
                            /(dfsignal['LongHoldingPeriod'].count()+dfsignal['ShortHoldingPeriod'].count())
                except:
                    tmp=0
                ba['HoldPeriodAvg(min)'] = round(tmp / np.timedelta64(1, 'm'),2)
                
               
                '''
                ba['WinLongTrade'] = dfsignal[dfsignal['LongPnL']>0]['LongPnL'].count()
                ba['WinShortTrade'] = dfsignal[dfsignal['ShortPnL']>0]['ShortPnL'].count()
                ba['WinTrade'] = dfsignal[dfsignal['LongPnL']>0]['LongPnL'].count()\
                                    + dfsignal[dfsignal['ShortPnL']>0]['ShortPnL'].count()
                
                
                ba['LossLongTrade'] = dfsignal[dfsignal['LongPnL']<=0]['LongPnL'].count()
                ba['LossShortTrade'] = dfsignal[dfsignal['ShortPnL']<=0]['ShortPnL'].count()
                ba['LossTrade'] = dfsignal[dfsignal['LongPnL']<=0]['LongPnL'].count()\
                                    + dfsignal[dfsignal['ShortPnL']<=0]['ShortPnL'].count()
                
                
                
                try:
                    ba['WinLongTradePercent'] = round(100*ba['WinLongTrade'] / ba['LongTradeCount'],2)
                except:
                    ba['WinLongTradePercent'] = 0
                try:    
                    ba['WinShortTradePercent'] = round(100*ba['WinShortTrade'] / ba['ShortTradeCount'],2)
                except:
                    ba['WinShortTradePercent'] = 0
                try:    
                    ba['WinTradePercent'] = round(100*ba['WinTrade']/ba['TradeCount'],2)
                except:
                    ba['WinTradePercent'] = 0
                '''
                
                
                
                print('\n\n')
                print('Backtest Analysis:'+portfolio+" : "+symbol)
                #print(ba)
                
                k=0
                r=0
                sr=''
                for key in ba.keys():
                    kk = 30*(k%3)+10
                    r = r+1 if k%3==0 else r
                    nl = '\n' if k%3==0 else ''
                    
                    tt = '\t\t\t\t' if r==2 or r==5 else '\t\t\t'
                    tt = '\t\t' if r==4 or r==7 else tt
                    #tt = '' if r==5 and k%3==2 else tt
                    
                    sr += (nl+key+":"+str(ba[key])+tt)
                    #print((key+":"+str(ba[key])+nl).ljust(kk)) 
                    k+=1
                print(sr)
                
                
                dfn = pd.DataFrame(candles_dict[symbol])
                dfn= dfn[dfn['close'] != 0.0]
                trade_cap = 0.01*security['trade_capital']*param['account_capital']
                size = math.floor(trade_cap/dfn.iloc[0]['open'])
                BuyNHold = round(size*(dfn.iloc[-1-RUN_FOR_MINUTES]['close'] - dfn.iloc[0]['open']), 2)
                print('BuyNHold Size: '+str(size), " BuyNHold Profit: "+str(BuyNHold) )

            except:
                pass
                #print('Error writing postprocessed backtest for '+symbol+':'+portfolio)
    
    #print("\n\n Grand PnL: "+str(grandPnL))
    btdf = pd.DataFrame()
    #with open('./data/BacktestAnalysis.txt','w') as bawriter:
        #bawriter.write(backtest_analysis_dict)
        #bawriter.write("Backtest analyis\n")
    for portfolio in portfolio_dict.keys():
        #bawriter.write(portfolio+'\n')
        symbols = portfolio_dict[portfolio]
        for symbol in symbols.keys():
            #bawriter.write(symbol+'\n')
            ba = backtest_analysis_dict[portfolio][symbol]
            #bawriter.write(ba)
            for key in ba.keys():
                #bawriter.write("%s,%s\n"%(key,ba[key]))
                btdf.at[portfolio+":"+symbol,key]=ba[key]
    
    #btdf.to_csv('./data/BacktestAnalysis.csv')
    
    
    
    '''' write final output in files '''
    #backtest_list = ['datetime','trade_signal','trade_signal_type','tradeprice','net_PnL']
    for portfolio in portfolio_dict.keys():
        backtest_list = ['datetime',portfolio+'trade_signal',\
                         portfolio+'trade_signal_type',portfolio+'tradeprice',\
                         portfolio+'position',portfolio+'net_PnL','comment']
        pts = portfolio+'trade_signal'
        symbols = portfolio_dict[portfolio]
        for symbol in symbols.keys():
            security = symbols[symbol]
            try:
                #print(dfn[backtest_list])
                dfn = pd.DataFrame(candles_dict[symbol])
                dfn.to_csv('./data/'+symbol+'_RAW.csv')
                #dfn[backtest_list].to_csv('./data/'+symbol+'_BACKTEST.csv')
                #fn2 = dfn[backtest_list].loc[0:len(dfn)-1-RUN_FOR_MINUTES]
                #fn2.loc[fn2[pts]!=0].to_csv('./data/'+portfolio+"_"+symbol+'_EQUITY_BACKTEST.csv')
                
                dfsig = pd.DataFrame(security['signal'])
                dfsig = dfsig.reindex(columns=(list([a for a in dfsig.columns if a != 'comment'])+['comment']  ))
                #dfsig.to_csv('./data/'+portfolio+"_"+symbol+'_BACKTEST.csv')
                
            except:
                print('Error writing backtest file for '+symbol)
    
    
    
    
    
    ''' trade analysis '''        
    #print("------------Equity Backtest Analysis------------")
    '''
    for portfolio in portfolio_dict.keys():
        print("\n \n Portfolio: ",portfolio)
        #backtest_list = ['datetime',portfolio+'trade_signal',portfolio+'trade_signal_type',portfolio+'tradeprice',portfolio+'net_PnL']
        #pts = portfolio+'trade_signal'
        symbols = portfolio_dict[portfolio]
        for symbol in symbols.keys():
            try:
                dfn = pd.DataFrame(candles_dict[symbol])
                dfn= dfn[dfn['close'] != 0.0]
                
                trade_cap = 0.01*portfolio_dict[portfolio][symbol]['trade_capital']*param['account_capital']
                size = math.floor(trade_cap/dfn.iloc[0]['open'])
                
                print("\n Symbol: ",symbol)
                
                back_equity_profit=round(dfn.loc[0:len(dfn)-1-RUN_FOR_MINUTES][portfolio+'PnL'].sum(),2)
                print("Strategy Equity Backtest Profit: "+str(back_equity_profit))
                
                BuyNHold = round(size*(dfn.iloc[-1-RUN_FOR_MINUTES]['close'] - dfn.iloc[0]['open']), 2)
                print('BuyNHold Size: '+str(size), " BuyNHold Profit: "+str(BuyNHold) )
            except:
                print('Error writing backtest analysis for '+symbol)
    '''
    
    
    return candles_dict, portfolio_dict






def create_candles_history(param, candles_dict, backdata, out_live):
    msg="IN HISTORY: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    if backdata is None:
        candles_dict = get_backdata(param, mtfcandles_dict)
        if candles_dict is None: return None
        if param['show_detail_log']: print(candles_dict.keys())
    else:
        candles_dict = backdata.copy()
    msg="OUT HISTORY: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')



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
    security['available_capital'] = param['account_capital']  
    
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



def portfolio_initialization(param, candles_dict):
    portfolio_dict =  param['portfolio_dict']
    for portfolio in portfolio_dict.keys():
        portfolio_dict[portfolio] = {} 
        for symbol in candles_dict.keys():
             initialize_symbol_portfolio(portfolio_dict, portfolio, symbol)
    return portfolio_dict



def run_system_new(param=None, out_live=None):
    param['instrument_symbol_list'] =  []
    
    param['instrument_token_dict'] = {}
    param['instrument_token_list'] = []
    
    param['instrument_option_list'] = []
    param['instrument_in_action'] =  [] 


    param['signal_list'] = []
    param['trade_table'] = []

    portfolio_dict = param['portfolio_dict']
    strategyClass_dict = {}
    
    mtfcandles_dict = {}            
    candles_dict = {}
    renko_dict = {}
    
    

    
    for portfolio in portfolio_dict.keys():
        modu = "strategy."+portfolio+'_strategy'
        #MyClass = getattr(importlib.import_module(modu), portfolio)
        MyClass = getattr(importlib.reload(importlib.import_module(modu)), portfolio)
        #importlib.reload(MyClass)
        strategyClass = MyClass()
        strategyClass_dict[portfolio] = strategyClass
        #portfolio_dict[portfolio]['strategyClass'] = strategyClass

    
    
    
    
    # create candles dictionary from data import    
    #create_candles_history(param, candles_dict, backdata, out_live)
    

    '''
    #renko initialization
    
    for symbol in candles_dict.keys():
        renko_dict[symbol] = []
    '''

    
    '''
    #indicator initialization
        
    for portfolio in param['portfolio_dict'].keys():
        param['indicator_dict'][portfolio] = {} 
        for symbol in candles_dict.keys():
             param['indicator_dict'][portfolio][symbol] = []
    '''
    
    '''
    #portfolio initialization
        
    portfolio_initialization(param, candles_dict)
    '''
    
    
    
    
    
    #print(candles_dict.keys())
    #print(mtfcandles_dict.keys())
    '''
    indices = param['instrument_index_list'][0]
    atr_timeframe = str(param["index_atr_timeframe_hour"])+"H"
    indices_candles =  globalvar.g_market_dict["INDEX"][indices][atr_timeframe] #candles_dict[indices]
    indices_index = len(indices_candles) - 1
    indices_atr_period = param['index_atr_period']
    for i in range(len(indices_candles)):
        #print(i)
        #print(indices_candles[i])
        indices_candles[i]['atr'] = calc_atr(indices_candles, i, indices_atr_period)
        #print(indices_candles[i])
        iatr = indices_candles[i]['atr']
        #print(iatr)
        inum = param["index_atr_timeframe_hour"]*60
        itflower = inum / param['index_atr_lowertimeframe']
        iatrlower = iatr / itflower
        brick_size = iatrlower
        indices_candles[i]['brick_size'] = brick_size
        #param['brick_size'] = brick_size
        #print(param['brick_size'])
    '''    

    
    #print("IN BACKTEST: ",datetime.now())
    '''
    msg="IN BACKTEST: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    #print(datetime.now()
    
    if True:#param['live_trading']==False:
        param['signal_live'] = False
        for portfolio in portfolio_dict.keys():
            run_backtest_OHLC_new(strategyClass_dict, portfolio_dict, portfolio, candles_dict, param, mtfcandles_dict, 0, renko_dict)
    
    msg="OUT BACKTEST: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    #print(datetime.now())
    build_trade_table(param)
    write_trade_table_file(param)
    '''
    #try:
    #    write_signal_output(portfolio_dict, param)
    #except Exception as e:
    #    traceback.print_exc()

    
    '''
    #PLOT RENKO
    
    if param['show_plot'] and param['live_trading']==False:
        for portfolio in portfolio_dict.keys():
                symbols = portfolio_dict[portfolio]
                for symbol in symbols.keys():
                    security = portfolio_dict[portfolio][symbol]
                    signal = security['signal']
                    dfsig = pd.DataFrame(signal)
                    plot_renko(symbol, renko_dict[symbol], dfsig, param)
    '''

    
    #Run Live
    msg="IN LIVE: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
    ''' run live trade system ''' 
    #param['RUN_FOR_MINUTES'] = 100
    RUN_FOR_MINUTES = param['RUN_FOR_MINUTES']
    if RUN_FOR_MINUTES>0:
        print("run live_trade")
        param['instrument_in_action'] = []
        param['signal_live'] = True
        livetrade.live_trade(strategyClass_dict, portfolio_dict, param, candles_dict, mtfcandles_dict, out_live, renko_dict)
    #print("OUT LIVE: ",datetime.now())
    msg="OUT LIVE: "+str(datetime.now())
    out_live.append_stdout(msg+'\n')
     
    
    return candles_dict, portfolio_dict
    



   
def plot_renko(symbol, d, dfsig, param):
    df=pd.DataFrame(d)
    #df.to_csv('./plots/'+symbol+'_DATA.csv')
    
    df['index'] = df.index
    #print(df)
    display(df)
    
    data = []
    
    traceOHLC = go.Candlestick(
        x=df['datetime'].astype(str),
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )
    data.append(traceOHLC)

    
    #df['supertrend'] = df[df['HullTrend']==1]['avgHullMA'].replace(0,float('nan'))
    if param['use_supertrend']==True:
        indicatorvalues = df['supertrend'].tolist()
        trace = go.Scatter(x = df['datetime'].astype(str), y = indicatorvalues, mode = 'markers', 
                               marker=dict(size=5, color='rgba(0, 0, 255, .6)'), name = "supertrend") #
        data.append(trace)

    if param['use_jurikma']==True:
        indicatorvalues = df['jurikma'].tolist()
        datetime_values = df['datetime'].astype(str)
        # Determine colors based on the value comparison
        '''
        colors = ['rgba(0, 0, 255, .6)']  # Starting color for the first point (can be set to your default)
        for i in range(1, len(indicatorvalues)):
            if indicatorvalues[i] > indicatorvalues[i-1]:
                colors.append('rgba(0, 255, 0, .6)')  # Green for greater
            else:
                colors.append('rgba(255, 0, 0, .6)')  # Red for smaller or equal
        
        trace = go.Scatter(x = datetime_values, y = indicatorvalues, mode = 'markers', 
                               marker=dict(size=5, color=colors), name = "jurikma")
        '''
        trace = go.Scatter(x = datetime_values, y = indicatorvalues, mode = 'markers', 
                               marker=dict(size=5, color='rgba(0, 0, 255, .6)'), name = "jurikma") #
        data.append(trace)
        
        '''
            # Create segments for the line plot
        segments = []
        for i in range(1, len(indicatorvalues)):
            segment = go.Scatter(
                x=[datetime_values[i-1], datetime_values[i]],
                y=[indicatorvalues[i-1], indicatorvalues[i]],
                mode='lines',
                line=dict(color=colors[i-1], width=2),
                showlegend=False
            )
            segments.append(segment)
        
        # Combine all segments into the data list
        data.extend(segments)
        '''
        

    if param['use_rsi']==True:
        indicatorvalues = df['rsi'].tolist()
        trace = go.Scatter(x = df['datetime'].astype(str), y = indicatorvalues, mode = 'markers', 
                               marker=dict(size=5, color='rgba(0, 255, 0, .6)'), name = "rsi")
        data.append(trace)

    
        indicatorvalues = df['rsima'].tolist()
        trace = go.Scatter(x = df['datetime'].astype(str), y = indicatorvalues, mode = 'markers', 
                               marker=dict(size=5, color='rgba(255, 0, 0, .6)'), name = "rsima")
        data.append(trace)
    
    '''
    layout = go.Layout(
        title="Renko",
        plot_bgcolor='rgba(0,0,0,0)')        
    '''
    layout = go.Layout(
        title="Renko",
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            #rangeselector = rangeselector,
            type='category', 
            categoryorder='category ascending',
            rangeslider = dict(
                visible = False
            )
            #tickcolor='#000'
        ),
        yaxis=dict(
            autorange=True
        )    
    )        


    # -----------------Signals--------------------------------
    arrowSize = 15

    '''
    traceLong = go.Scatter(
        x = df.loc[df['Long'] == True , 'dates'].astype(str),
        y = df.loc[df['Long'] ==True, 'LongPrice'].values.tolist(),
        text=df.loc[df['Long'] == True , portfolio+'position'].astype(str),
        textposition='top center',
        mode = 'markers+text',
        marker={'color': 'rgba(0, 255, 0, .8)', 'symbol': 'triangle-up', 'size': arrowSize},
        name = 'Long'
        )
    data.append(traceLong)
    '''
    
    try:
        if 'Long' in dfsig.columns:
            traceLong = go.Scatter(
                x = dfsig.loc[dfsig['Long'] == True , 'datetime'].astype(str),
                y = dfsig.loc[dfsig['Long'] ==True, 'LongPrice'].values.tolist(),
                text=dfsig.loc[dfsig['Long'] == True , 'position'].astype(str),
                textposition='top center',
                mode = 'markers+text',
                marker={'color': 'rgba(0, 255, 0, .8)', 'symbol': 'triangle-up', 'size': arrowSize},
                name = 'Long'
                )
            data.append(traceLong)
    except:
        pass


    try:
        if 'CloseLong' in dfsig.columns:
            traceCloseLong = go.Scatter(
                x = dfsig.loc[dfsig['CloseLong'] == True , 'datetime'].astype(str),
                y = dfsig.loc[dfsig['CloseLong'] ==True, 'CloseLongPrice'].values.tolist(),
                text=dfsig.loc[dfsig['CloseLong'] == True , 'position'].astype(str),
                textposition='top center',
                mode = 'markers+text',
                marker={'color': 'rgba(0, 0, 255, .8)', 'symbol': 'triangle-down', 'size': arrowSize},
                name = 'CloseLong'
                ) 
            data.append(traceCloseLong)
    except:
        pass


    '''
    fig = go.Figure(data=data)
    fig.update_layout(
        title='Candlestick Chart',
        xaxis_title='Index',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )
    '''
    
    
    fig = go.Figure(data=data, layout=layout)        
    #fig.show()
    #fig.update_traces(textposition='top center')
    plot(fig, show_link = True, filename = PLOTPATH+symbol+'.html')
    plt.show(block=False)
    return fig







def write_signal_output(portfolio_dict=None, param=None, summaryfilename=None, out_live=None):
    signal_list = param['signal_list']
    if len(signal_list)>0:
        #for ss in range(len(signal_list)):    
        #    signal = signal_list[ss]

        #    portfolio = signal['portfolio']
        #    symbol = signal['symbol']
            
            #candles_live = candles_dict[symbol]
            #close_price = candles_live[-1]['close']
            #security = portfolio_dict[portfolio][symbol]
            #rbrick = round(security['brick_size'],2)
            
            #dfsig = pd.DataFrame(signal)
            #dfsig['symbol'] = symbol
            #if count==0 and len(dfsig)>0:
            #    dfsum = pd.DataFrame(columns=dfsig.columns)
            #    count+=1    
            #if count>0:
            #    dfsum = pd.concat([dfsum, dfsig], ignore_index=True)
            #count+=1
        dfsum = pd.DataFrame(signal_list)
        if(len(dfsum)<1):return
            
        ''' Post processing '''
        #dfsum['TradeDirection'] = dfsum['symbol'].apply(lambda x: 'BUY' if 'CE' in x else 'SELL')
        dfsum['TradeDirection'] = dfsum['Long'].apply(lambda x: 'BUY' if x==True else 'SELL')
        dfsum['TradeMode'] = 'PAPER' if param['PLACE_ORDER']==False else 'REAL'
        dfsum['EntryPrice'] = dfsum.apply(lambda row: row['LongPrice'] if row['Long'] == True else np.nan, axis=1)
        dfsum['ExitPrice'] = dfsum.apply(lambda row: row['CloseLongPrice'] if row['CloseLong'] == True else np.nan, axis=1)
        
        
        
        
        ''' sorting '''
        df_sorted = dfsum#.sort_values(by='datetime')
        df_sorted['cumPnL'] = df_sorted['PnL'].cumsum()
        
        if param['live_trading']==False:
            display(df_sorted)
        
        print("PnL GRAND SUM:",df_sorted['PnL'].sum())
        
        #msg = summaryfilename
        #out_live.append_stdout(msg+'\n')
        #msg = str(df_sorted)
        #out_live.append_stdout(msg+'\n')
        #print(summaryfilename)
        #print(df_sorted)
        #df_sorted.to_csv("./summary/BacktestSignal.csv")
       
        if param['live_trading']==False:
            filename = SUMMARYPATH+param['index_symbol_option']+"-BacktestSignal.csv"
        else:
            filename = summaryfilename
            #now = datetime.now()#.date()
            #date_str = now.strftime('%Y-%m-%d-%H%M')
            #filename = "./summary/LiveSignal-"+date_str+".csv"
            df_sorted = df_sorted[df_sorted['live']==True]
            #filename = "./summary/LiveSignal-"+str(portfolio)+str(date)+".csv"

        #print(filename)
        #msg = str(df_sorted)
        #out_live.append_stdout(msg+'\n')
        #df_sorted.to_csv(filename)
        #return
        column_seq = ['TradeDirection','TradeMode','position','symbol','datetime','EntryPrice','ExitPrice',
                      'unrealized_pnl','PnL','holdingvalue','comment','live','brick_size','jurikma']
        df_sortedfile = df_sorted[column_seq]
        try:
            df_sortedfile.to_csv(filename)#, mode='a', index=False, header=False))
        except:
            try:
                df_sortedfile.to_csv(filename)
            except:
                pass
        
        return df_sorted


def write_trade_table_file(param=None,summaryfilename=None):
    try:
        #print(type(list(dftrade.columns)),list(dftrade.columns))
        trade_table = param['trade_table']
        if len(trade_table)<1:return
        dftrade = pd.DataFrame(trade_table)
        if param['live_trading']==False:
            filename = SUMMARYPATH+param['index_symbol_option']+"BacktestSignal.csv"
        else:
            filename = summaryfilename
            dftrade = dftrade[dftrade['live']==True]
            
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
        dftrade['TradeMode'] = 'PAPER' if param['PLACE_ORDER']==False else 'REAL'
        #display(dftrade)
        if param['live_trading']==False:
            display(dftrade)
        dftrade.to_csv(filename)
    except Exception as e:
        traceback.print_exc()
    return

#END