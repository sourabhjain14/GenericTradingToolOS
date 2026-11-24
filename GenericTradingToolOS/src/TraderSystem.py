"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


#@copyright Sourabh Jain
import time
import pandas as pd
from IPython.display import display
from ipywidgets import widgets
from ipywidgets import interact,interactive, interact_manual, Button, Output, HBox, VBox, Layout
from threading import Thread
import asyncio
import os
import glob
import ast
#import json
import csv
import copy
import datetime
import traceback
import functools
import importlib
from contextlib import redirect_stdout
import io
import re
#import logging
#import pyotp 
import globalvar

#from managerGUI import setup_kite
import zerodha
import finvasia
#from zerodha import create_kite
#from finvasia import create_shoonya

from widget_lib import item_set_value
from widget_lib import create_datepicker
from widget_lib import create_dropdown
from widget_lib import create_checkbox
from widget_lib import create_inttext
from widget_lib import create_boundedinttext
from widget_lib import create_floattext
from widget_lib import create_boundedfloattext
from widget_lib import create_button
from widget_lib import create_text
from widget_lib import add_global_trade_item_row
from widget_lib import create_global_trade_items

#from ShoonyaApipymaster.api_helper import ShoonyaApiPy

from initialize import g_tick_dict, g_param, STRATEGY_LIST
#from initialize import g_tick_dict, param, g_param, STRATEGY_LIST
from ACCOUNT_DETAIL import IP, PORT, USERNAME, PASSWORD, BROKER,PARAMETER_PASSWORD

import trademanager
importlib.reload(trademanager)
#from trademanager import run_system
import symbol_window
importlib.reload(symbol_window)


import symbol_window_new
importlib.reload(symbol_window_new)

# Get the current working directory
current_path = os.getcwd()
#print(f"Current Working Directory: {current_path}")


DEBUG_MODE=True
DEBUG_MODE=False

#-----------------------------Zerodha KiteConnect----------------------------------------------
#!pip install sourcedefender
#!pip install pyotp
#import sourcedefender
#from kiteext_pro import KiteExt
#kite = KiteExt()
#kite.login_with_credentials(userid=ZERODHA_USER_ID,password=ZERODHA_PASSWORD,twofa=ZERODHA_TOTP)
#from initialize import g_kite
#from zerodha import create_kite
#globalvar.g_kite=create_kite()
#---------------------------initiaze chart varaiables--------------------------------------- 
globalvar.g_market_dict = {"INDEX":{}, "EQUITY":{}, "OPTION":{},"FUTURES":{},"FOREX":{}}


global live_param
live_param = {}

global candles_dict_chart
global portfolio_dict_chart
global indicator_dict_chart
candles_dict_chart = {}
portfolio_dict_chart = {}
indicator_dict_chart = {}

global live_portfolio_dict_chart
global live_indicator_dict_chart
global live_candles_dict_chart
live_portfolio_dict_chart = {}
live_indicator_dict_chart = {}
live_candles_dict_chart = {}    


#------------------------widget templates-----------------------------------------------------
style = {'description_width': 'initial'}
bw = '90%'



#--------------------------Paramters-----------------------------------------------------------

'''
param['allow_unauthenticated_requests'] = False
def allow_unauthenticated_requests_f(change):
    param['allow_unauthenticated_requests'] = change.new
allow_unauthenticated_requests_w = widgets.Checkbox(
    value=param['allow_unauthenticated_requests'],
    description='Unauthenticated Requests',
    disabled=False,
    indent=False,layout={'width': bw}, style=style
)
allow_unauthenticated_requests_w.observe(allow_unauthenticated_requests_f,'value')
'''

'''--------------------------------------strategy parameters---------------------------------
'''


'''
show_open_trade_w = create_checkbox(param, 'show_open_trade', False) 


trade_expiry_w = create_datepicker(param, 'trade_expiry')
trade_expiry_w.value = datetime.date.today()
#trade_expiry_w.year = 2020
#trade_expiry_w.month = 12
#trade_expiry_w.day = 1


option_instrument_type_w = create_dropdown(param, 'option_type', ['CALL','PUT','BOTH'], 'BOTH')


ATM_strike_w = create_checkbox(param, 'ATM_strike', True) 
OTM_count_w = create_inttext(param, 'OTM_count', 5)
ITM_count_w = create_inttext(param, 'ITM_count', 2)

ATP_type_w = create_dropdown(param, 'atp_type', ['GREATER','LESS'], 'GREATER', 'VWAP Condition')
ATP_w = create_floattext(param, 'atp_percent', 50, 'VWAP %')

min_option_price_w = create_floattext(param, 'min_option_price', 2, 'Min Price')
max_option_price_w = create_floattext(param, 'max_option_price', 10, 'Max Price')

quantity_config_w = create_dropdown(param, 'quantity_configuration', ['No of Lots','Risk per trade'], 'Risk per trade')
no_of_lots_w = create_inttext(param, 'no_of_lots', 1, 'Lots')
risk_per_trade_w = create_floattext(param, 'risk_per_trade', 1000, 'Risk per trade')
max_no_of_lots_w = create_inttext(param, 'max_no_of_lots', 100, 'Max Lots')
'''

'''
stop_loss_type_w = create_dropdown(param, 'stop_loss_type', ['Percentage','Points'], 'Percentage')
SL_w = create_floattext(param, 'SL', 50, 'SL %')
target_w = create_floattext(param, 'target', 99, 'target %')
use_trail_w = create_checkbox(param, 'use_trail', False, 'Use Trail') 
trail_w = create_floattext(param, 'trail', 100, 'trail %')
trail_by_w = create_floattext(param, 'trail_by', 100, 'trail by %')


'''





'''
-------------------------------------Trade Parameters-------------------------------------------
'''




'''
param['useTemplate'] = True
def useTemplate_f(change):
    param['useTemplate'] = change.new
    #print("useTemplate:",param['useTemplate'])
useTemplate_w = widgets.Checkbox(
    value=param['useTemplate'],
    description='useTemplate',
    disabled=False,
    indent=False
)
useTemplate_w.observe(useTemplate_f, 'value')




param['LAST_TEMPLATE'] = None
def LAST_TEMPLATE_f(change):
    param['LAST_TEMPLATE'] = change.new
LAST_TEMPLATE_w = widgets.Text(value=param['LAST_TEMPLATE'],description='TEMPLATE NAME',disabled=False, layout={'width': 'auto'}, style=style)
LAST_TEMPLATE_w.observe(LAST_TEMPLATE_f, 'value')
'''


#---------------------- system settings--------------------------------------------


''' Trading window for placing orders '''
'''
param['useTradewindow'] = True
def useTradewindow_f(change):
    param['useTradewindow'] = change.new
useTradewindow_w = widgets.Checkbox(
    value=param['useTradewindow'],
    description='useTradewindow',
    disabled=False,
    indent=False
)
useTradewindow_w.observe(useTradewindow_f, 'value')


param['tradewindowStart'] = 930

def tradewindowStart1_f(change):
    param['tradewindowStart'] = 100*change.new+tradewindowStart2_w.value
tradewindowStart1_w = widgets.BoundedIntText(
    value=9,min=9,max=15,step=1,
    description='tradewindowStart',
    disabled=False,
    indent=False,layout={'width': '15%'}, style=style
)
tradewindowStart1_w.observe(tradewindowStart1_f, 'value')


def tradewindowStart2_f(change):
    param['tradewindowStart'] = 100*tradewindowStart1_w.value+change.new
tradewindowStart2_w = widgets.BoundedIntText(
    value=30,min=0,max=59,step=1,
    description='',
    disabled=False,
    indent=False,layout={'width': '40px'}, style=style
)
tradewindowStart2_w.observe(tradewindowStart2_f, 'value')
'''






'''
param['tradewindowEnd'] = 1550
def tradewindowEnd_f(change):
    param['tradewindowEnd'] = change.new
tradewindowEnd_w = widgets.BoundedIntText(
    value=param['tradewindowEnd'],min=930,max=1559,step=1,
    description='tradewindowEnd',
    disabled=False,
    indent=False,layout={'width': '20%'}, style=style
)
tradewindowEnd_w.observe(tradewindowEnd_f, 'value')

def tradewindowEnd1_f(change):
    param['tradewindowEnd'] = 100*change.new+tradewindowEnd2_w.value
tradewindowEnd1_w = widgets.BoundedIntText(
    value=15,min=9,max=15,step=1,
    description='tradewindowEnd',
    disabled=False,
    indent=False,layout={'width': '15%'}, style=style
)
tradewindowEnd1_w.observe(tradewindowEnd1_f, 'value')


def tradewindowEnd2_f(change):
    param['tradewindowEnd'] = 100*tradewindowEnd1_w.value+change.new
tradewindowEnd2_w = widgets.BoundedIntText(
    value=50,min=0,max=59,step=1,
    description='',
    disabled=False,
    indent=False,layout={'width': '40px'}, style=style
)
tradewindowEnd2_w.observe(tradewindowEnd2_f, 'value')
'''



''' Intra-day squaring of positions'''

'''
param['tradeSquare'] = True
def tradeSquare_f(change):
    param['tradeSquare'] = change.new
tradeSquare_w = widgets.Checkbox(
    value=param['tradeSquare'],
    description='Intraday tradeSquareOff',
    disabled=False,
    indent=False
)
tradeSquare_w.observe(tradeSquare_f, 'value')


param['tradeSquareTime'] = 1552
def tradeSquareTime1_f(change):
    param['tradeSquareTime'] = change.new*100+tradeSquareTime2_w.value
tradeSquareTime1_w = widgets.BoundedIntText(
    value=15,min=9,max=15,step=1,
    description='tradeSquareOffTime',
    disabled=False,
    indent=False,layout={'width': '18%'}, style=style
)
tradeSquareTime1_w.observe(tradeSquareTime1_f, 'value')


def tradeSquareTime2_f(change):
    param['tradeSquareTime'] = tradeSquareTime2_w.value*100+change.new
tradeSquareTime2_w = widgets.BoundedIntText(
    value=52,min=0,max=59,step=1,
    description='',
    disabled=False,
    indent=False,layout={'width': '40px'}, style=style
)
tradeSquareTime2_w.observe(tradeSquareTime2_f, 'value')
'''

'''
RUN_FOR_MINUTES: Duration for loop (minutes), this value
should be set as 0 for backtesting on security
'''
'''
param['RUN_FOR_MINUTES'] = 50000
def RUN_FOR_MINUTES_f(change):
    param['RUN_FOR_MINUTES'] = change.new
RUN_FOR_MINUTES_w = widgets.IntText(value=param['RUN_FOR_MINUTES'],description='RUN_FOR_MINUTES',disabled=False, layout={'width': 'auto'}, style=style)
RUN_FOR_MINUTES_w.observe(RUN_FOR_MINUTES_f, 'value')
'''



'BE CAREFUL! It will place live orders in your trade account (False/True)'



'''
Following instrument list contains symbol to be traded
input is list like param['instrument_symbol_list'] =  ["SPY","TSLA","AAPL", "AMZN","GOOG","MED"]
'''

#param['instrument_symbol_list'] = []

#param['live_output'] = 'HTML:'
#live_param['live_output'] = 'HTML:'

#-------------------------trader input settings --------------------------------


'update intra-bar tick data every N seconds'
#param['UPDATE_TICK_DATA_SECONDS'] = 0.1


'paper trading in live market'
#param['TRADE_LIVE'] = True


'allow short/put options'
#param['ALLOW_SHORT'] = True


'generate refresh token every 90 days by switching it to True and then turn False again'
#param['generate_refresh_token'] = False


#--------------------- time frame and history data paramters ---------------
'''
param['timeframe']='minute'
def timeframe_f(timeframe):
    param['timeframe'] = timeframe_w.value
#timeframe_w = interactive(timeframe_f, timeframe=['minute'],layout={'width': '10%'})
timeframe_w = widgets.Dropdown(options=['minute'], value='minute',description="timeframe",layout={'width': bw}, style=style)



param['frequency'] = '1'
frequency_list = ['1','2','3','4','5','10','15','30']
def frequency_f(change):
    param['frequency'] = change.new
#frequency_w = widgets.Text(value=param['frequency'],description='frequency',disabled=False, layout={'width': '15%'})
frequency_w = widgets.Dropdown(options=frequency_list, value=param['frequency'],description='frequency', disabled=False, layout={'width': bw}, style=style)
frequency_w.observe(frequency_f, 'value')



param['periodType']='day'
def periodType_f(periodType):
    param['periodType'] = periodType_w.value
#periodType_w = interactive(periodType_f, periodType=['day'],layout={'width': '10%'})
periodType_w = widgets.Dropdown(options=['day'], value='day',description="periodType",layout={'width': bw}, style=style)


param['period']='1'
def period_f(change):
    param['period'] = change.new
period_w = widgets.Text(value=param['period'],description='period',disabled=False, layout={'width': bw}, style=style)
period_w.observe(period_f, 'value')



param['extended_hours'] = False
def extended_hours_f(change):
    param['extended_hours'] = change.new
extended_hours_w = widgets.Checkbox(
    value=param['extended_hours'],
    description='extended_hours',
    disabled=False,
    indent=False,
    layout={'width': bw}, style=style
)
extended_hours_w.observe(extended_hours_f,'value')
'''





'''
backtest_point_list = ['OHCLC','OHLC','C']
param['backtest_point'] = 'C'
def backtest_point_f(change):
    param['backtest_point'] = change.new
backtest_point_w=widgets.Dropdown(options=backtest_point_list,value=param['backtest_point'],\
                                  decription='backtest point', layout={'width': bw}, style=style)
backtest_point_w.observe(backtest_point_f, 'value')
'''


'''
param['backtest_date'] = None
def bk_dt_f(change):
    param['backtest_date'] = change.new
    print(param['backtest_date'])
bk_dt_w = widgets.DatePicker(
    description='Backtest Date',
    disabled=False,
    layout={'width': bw}, style=style
)
bk_dt_w.observe(bk_dt_f,'value')

param['clearBacktestdate'] = False

clearBacktestdate_button = widgets.Button(description="clearBacktestDates",layout={'width': '15%'})
#clearBacktestdate_button.style.button_color = 'black'
def on_clearBacktestdate_clicked(b):
    bk_dt1_w.value = None
    #param['backtest_date1'] = None
    bk_dt2_w.value = None
    #param['backtest_date2'] = None
clearBacktestdate_button.on_click(on_clearBacktestdate_clicked)
'''



#---------------------------------post process------------------------------
#param['liveOutputFrequency'] = 5

#print('param complete')
#--------------------------------------------------------------------------

#param_original = param.copy()

button_param_reset_w = widgets.Button(description="Reset Parameters", style=style, layout={'width': 'auto','height':'80px'})
def on_button_param_reset_clicked(b):
    account_capital_w.value = param_original['account_capital']
    trade_capital_w.value = param_original['trade_capital']
    
    tradeDirection_w.value = 'LONG'
    
    symbols_w.value = []
    param['portfolio_dict']['chori_strategy'] = {}
    symbols2_w.value = []
    param['portfolio_dict']['bros24_strategy'] = {}
    
    
    useTradewindow_w.value = param_original['useTradewindow']
    tradewindowStart1_w.value = 9
    tradewindowStart2_w.value = 35
    tradewindowEnd1_w.value = 15
    tradewindowEnd1_w.value = 50
    
    tradeSquare_w.value = param_original['tradeSquare']
    tradeSquareTime1_w.value = 15
    tradeSquareTime2_w.value = 55
    
    timeframe_w.value = param_original['timeframe']
    frequency_w.value = param_original['frequency']
    period_w.value = param_original['period']
    periodType_w.value = param_original['periodType']
    
    
button_param_reset_w.on_click(on_button_param_reset_clicked)



#########----------------------------BACKTEST----------------------------------------------
#fl = ['']
fl=['BACKTEST FILES']+glob.glob("./analysis/*BACKTEST.csv")
                
def backtest_files_f(change):
    #print(change.new)
    if change.new == '':
        return
    try:
        os.startfile(change.new)
    except:
        pass
test_layout = Layout(width='100%')
backtest_files_w = widgets.Select(
    options=fl,
    layout = test_layout,
    value='BACKTEST FILES',
    # rows=10,
    description='',
    disabled=False
)
#backtest_files_w.unobserve(backtest_files_f, 'value')
#backtest_files_w.options = fl
#backtest_files_w.value=''
backtest_files_w.observe(backtest_files_f,'value')



backtest_display_w = widgets.Textarea(
    value='',
    #placeholder='',
    description='Backtest Display',
    disabled=False
)
#button = widgets.Button(description="Run BackTest")
#button.style.button_color = 'yellow'
#output = widgets.Output()
#button_w = display(button, output)
reset_backtest = widgets.Output(layout={'border': '1px solid yellow', 'width':'100%'})
reset_live = widgets.Output(layout={'border': '1px solid green', 'width':'100%'})
#live_button = widgets.Button(description="Run Live!")
#live_button.style.button_color = 'lightgreen'
#button_w = display(button, output)
out_live = widgets.Output()
out_live_table = widgets.Output()
out_live_position = widgets.Output()
#reset_backtest.observe(reset_backtest_f,'outputs')
#button = widgets.Button(description="Run BackTest")
#button.style.button_color = 'yellow'
#output = widgets.Output()
#button_w = display(button, output)
@reset_backtest.capture(clear_output=True)
def on_backtest_button_clicked_thread(b, symbol, param):
    b.disabled = True
    param['portfolio_dict'] = {}
    param['portfolio_dict']['strategy1'] = {}#{symbol:{}}
    param['indicator_dict'] = {}
    #if param['show_detail_log'] is True: print('running backtest with:',param)
    #thread = Thread(target=on_button_clicked,args=(b,))
    #thread.start()
    #thread.join()
    on_backtest_button_clicked(b, param)
    b.disabled = False

def on_backtest_button_clicked(b, backtest_param):
    #print(param['ChoriSMAPeriod'])
    #return
    #global portfolio_dict_chart
    #global indicator_dict_chart
    #global candles_dict_chart
    #with output:
    #portfolio_dict_chart = param['portfolio_dict']
    
    
    #backtest_param = param.copy()
    #backtest_param = copy.deepcopy(param)
    #print(backtest_param)
    backtest_param['RUN_FOR_MINUTES'] = 0
    #backtest_param['instrument_index_list'] = ["NIFTY 50"]
    backtest_param['instrument_index_list'] = backtest_param['index_symbol']#["NIFTY24SEPFUT"]
    
    if backtest_param['show_detail_log'] is True: print('running backtest with:',backtest_param)
        
    try:
        candles_dict_chart, portfolio_dict_chart = trademanager.run_system(backtest_param, None, out_live, out_live_table, out_live_position)
    except Exception as e:    
        traceback.print_exc()
        b.disabled = False
    
    indicator_dict_chart = backtest_param['indicator_dict']
    
    
    fl = ['BACKTEST FILES']+glob.glob("./analysis/*BACKTEST.csv")
    backtest_files_w.options = fl
#button.on_click(on_button_clicked_thread)


#out_live.auto_scroll_threshold = 10
@reset_live.capture(clear_output=True)
def on_live_button_clicked_thread(b, symbol, param):
    #live_button.disabled = True
    reset_backtest.clear_output()
    print("in live button clicked thread")
    b.disabled = True
    
    if param['show_detail_log'] is True:
        print('running live with:',param)
    
    
    try:
        reset_global_trade_items(param)
        #create_global_trade_items(param)
        #nifty_tradebox.value = globalvar.g_param['trade_items']
    except Exception as e:
        traceback.print_exc()
    
    
    live_thread = Thread(target=on_live_button_clicked,args=(b, out_live, param))
    live_thread.start()
    
    if DEBUG_MODE: live_thread.join()
    #try:
    #if symbols_select_w.value=='':
    #    print("Select a Symbol")
    #    live_button.disabled = False
    #    return
    
    #on_live_button_clicked(b)#,symbol, out_live,out_live_table, out_live_position)
    #except:
    #    print('live run failure')
    #    live_button.disabled = False


#@reset_live.capture(clear_output=True)    
def on_live_button_clicked(b, out_live, live_param):#, symbol, out_live,out_live_table, out_live_position):
    #print(param['ChoriSMAPeriod'])
    #return
    out_live.clear_output(False)
    
    #global live_param
    #global live_portfolio_dict_chart
    #global live_indicator_dict_chart
    #global live_candles_dict_chart
    #with output:
    #portfolio_dict_chart = param['portfolio_dict']
    live_indicator_dict_chart = live_param['indicator_dict']
    
    live_param['portfolio_dict']['strategy1'] = {}
    #live_param = param.copy()
    #live_param = copy.deepcopy(param)
    live_param['RUN_FOR_MINUTES']=500000
    live_param['live_trading'] = True
    live_param['backtest_date1'] = None
    live_param['backtest_date2'] = None
    #live_param['instrument_index_list'] = ["NIFTY 50"]
    live_param['instrument_index_list'] = live_param['index_symbol']#["NIFTY24SEPFUT"]["NIFTY24SEPFUT"]
    #live_param['RUN_FOR_MINUTES'] = 500
    
    #live_param['backtest_point'] = 'C'
    #print(live_param)
    #b.disabled = False
    if DEBUG_MODE: 
        live_candles_dict_chart, live_portfolio_dict_chart = trademanager.run_system(live_param, None, out_live, out_live_table, out_live_position)
        return
    
    try:
        live_candles_dict_chart, live_portfolio_dict_chart = trademanager.run_system(live_param, None, out_live, out_live_table, out_live_position)
        b.disabled = False
    except Exception as e:    
        traceback.print_exc()
        out_live.append_stdout(str(e)+'\n')
        b.disabled = False
    
    #fl = ['']+glob.glob("./data/*BACKTEST.csv")
    #backtest_files_w.options = fl
#live_button.on_click(on_live_button_clicked_thread)


@out_live.capture(clear_output=False)
def on_stop_live_button_clicked(b, param):
    print('STOPPING LIVE TRADE')
    #global live_param
    #live_param['RUN_FOR_MINUTES'] = 0
    globalvar.g_param['RUN_FOR_MINUTES'] = 0


@out_live.capture(clear_output=False)
def on_connect_broker_button_clicked(b, param):
    print('CONNECTING BOKER')
    if param['broker']=='zerodha':
        def remove_text_after_userid(input_string):
            result = re.sub(r'userid.*?\n', '', input_string)
            return result
        f = io.StringIO()
        with redirect_stdout(f):
            zerodha.create_kite()
        output = f.getvalue()
        cleaned_output = remove_text_after_userid(output)
        print(cleaned_output)
    if param['broker']=='finvasia':
        finvasia.create_shoonya() 
    return


@out_live.capture(clear_output=False)
def on_disconnect_broker_button_clicked(b, param):
    print('DISCONNECTING BOKER')
    if param['broker']=='zerodha':
        return
    if param['broker']=='finvasia':
        return 
    return


@out_live.capture(clear_output=False)
def on_connect_zerodha_button_clicked(b, param):
    print('CONNECTING ZERODHA')
    if True:
        def remove_text_after_userid(input_string):
            result = re.sub(r'userid.*?\n', '', input_string)
            return result
        f = io.StringIO()
        with redirect_stdout(f):
            zerodha.create_kite()
        output = f.getvalue()
        cleaned_output = remove_text_after_userid(output)
        print(cleaned_output)
        b.disabled = True
    return


@out_live.capture(clear_output=False)
def on_connect_finvasia_button_clicked(b, param):
    print('CONNECTING FINVASIA')
    finvasia.create_shoonya()
    b.disabled = True
    return
    

def reset_global_trade_items(param):
    width = param['trade_table_width']
    height = int(len(globalvar.g_param['trade_items'])/width) #param['trade_table_height']
    scount=0
    vs = " "
    for j in range(1,height):
        for i in range(0,width):
            if(i==width-1):
                #item_set_value(vs, globalvar.g_param['trade_items'], i, j, width)
                wbutton = globalvar.g_param['trade_items'][i+j*width]
                wbutton.layout.display = 'none'
                wbutton.disabled = False
                wbutton.style.button_color = 'green'
                #wbutton.on_click(callback, remove=True)
                wbutton._click_handlers.callbacks = []
            else:
                item_set_value(vs, globalvar.g_param['trade_items'], i, j, width)
                globalvar.g_param['trade_items'][i+j*width].style = {}#{'background': 'transparent'}
    #grid.children = new_values
    return

'''
def add_global_trade_item_row(param):
    iw=param['trade_table_width']
    iw1 =  len(globalvar.g_param['trade_items'])
    iw2 = iw1+iw
    for i in range(iw1, iw2):
        if (i>20 and ((i+1)%iw==0)):
            wbutton = widgets.Button(description="Close")
            wbutton.style.button_color = 'green'
            wbutton.layout.display = 'none'
            globalvar.g_param['trade_items'].append(wbutton)
        else:
            widgetsLabel = widgets.Text(value=" ",disabled=True)
            globalvar.g_param['trade_items'].append(widgetsLabel)
    

def create_global_trade_items(param):
    globalvar.g_param['trade_items'] = []
    iw = param['trade_table_width']
    iwx = param['trade_table_height']*iw
    for i in range(iwx):
        if (i>20 and ((i+1)%iw==0)):
            wbutton = widgets.Button(description="Close")
            wbutton.style.button_color = 'green'
            wbutton.layout.display = 'none'
            #wbutton.on_click(functools.partial(on_close_trade_button_clicked_thread, candle=None, security=None, param=None))
            globalvar.g_param['trade_items'].append(wbutton)
        else:
            #widgetsLabel = widgets.Label("")#,
            widgetsLabel = widgets.Text(value=" ",disabled=True)
            #if i<iw:widgetsLabel.style = {'background': 'yellow'}
            #widgetsLabel.layout = widgets.Layout(background_color='green')
            #style=styles[i%2]
            #widgetsLabel.layout = widgets.Layout(**style)
            #widgetsLabel.style.color == 'lightblue'
            globalvar.g_param['trade_items'].append(widgetsLabel)
            #print(globalvar.g_param['trade_items'][-1].style)
    
    item_set_value("SYMBOL", globalvar.g_param['trade_items'], 0, 0, iw)
    item_set_value("LAST PRICE", globalvar.g_param['trade_items'], 1, 0, iw)
    item_set_value("ENTRY PRICE", globalvar.g_param['trade_items'], 2, 0, iw)
    item_set_value("EXIT PRICE", globalvar.g_param['trade_items'], 3, 0, iw)
    item_set_value("POSITION", globalvar.g_param['trade_items'], 4, 0, iw)
    item_set_value("HOLDING", globalvar.g_param['trade_items'], 5, 0, iw)
    item_set_value("PNL", globalvar.g_param['trade_items'], 6, 0, iw)
    item_set_value("ENTRY TIME", globalvar.g_param['trade_items'], 7, 0, iw)
    item_set_value("EXIT TIME", globalvar.g_param['trade_items'], 8, 0, iw)
    item_set_value("HEIGHT", globalvar.g_param['trade_items'], 9, 0, iw)
    item_set_value("TRADE TYPE", globalvar.g_param['trade_items'], 10, 0, iw)
    item_set_value("EXIT", globalvar.g_param['trade_items'], 11, 0, iw)
    return
'''



'''
@out_live.capture(clear_output=False)
def on_liquidate_clicked(b):
    print('liquidation begins')
    liquidate_all()
    print('liquidation ends')
liquidate_button.on_click(on_liquidate_clicked)

def liquidate_all():
    for portfolio in param['portfolio_dict'].keys():
        symbol_list = list(param['portfolio_dict'][portfolio].keys())
        close_positions(symbol_list)
'''    
    
account_w = widgets.Textarea(
    value='',
    #placeholder='',
    description='Account Details',
    disabled=False,
    layout={'width':'100%'},)
#account_w.observe(account_f,'value')
#account_w.value = dfa.to_string()

#def html_f(change):
#    html_w.value = change.new
#html_w = widgets.HTML(value=live_param['live_output'])
#html_w.observe(html_f,'value')
#---------------------------PASSWORD--------------------------------------------------------------
# Create a password widget



# Create a VBox to hide
#hidden_box = widgets.VBox([widgets.Label("This is a hidden box")])
# Hide the VBox initially
#hidden_box.layout.display = 'none'
# Display the widgets
#display(password)
#display(hidden_box)

horizontal_line = widgets.HTML(value="<hr>")

'''
param['account_capital'] = 100000.0
def account_capital_f(change):
    param['account_capital'] = change.new
account_capital_w=widgets.FloatText(value=param['account_capital'],description='Trade Capital',disabled=False, layout={'width': bw}, style=style)
account_capital_w.observe(account_capital_f,'value')
'''

#------------------------------------------------------------------------------------------------
#----------------------------------------NIFTY---------------------------------------------------
param = {}
param = globalvar.g_param
param['index_exchange'] = "NSE"
param['index_symbol'] = ["NIFTY 50"]
param['index_symbol_option'] = 'NIFTY'
param['index_symbol_ltp'] = "NSE:NIFTY 50"
param["option_expiry"] = "THURSDAY"
param["strike_interval"] = 50
param['lot'] = 25
param['interest_rate'] = 0.065
param['annualized_volatility'] = 0.1627
param['timeframe']='minute'

#nifty_vbox = symbol_window.create_window(param)
niftyWindowClass = symbol_window_new.symbolWindow()
nifty_vbox = niftyWindowClass.create_window(param)

param['expiry_frequency'] = 'Week'
niftyWindowClass.nifty_expiry_month_w.disabled=True

#------------------------------------------------------------------------------------------------






#------------------------------------------------------------------------------------------------
#----------------------------------------banknifty---------------------------------------------------
bankparam = globalvar.g_bankparam
bankparam['index_exchange'] = "NSE"
bankparam['index_symbol'] = ['NIFTY BANK']
bankparam['index_symbol_option'] = 'BANKNIFTY'
bankparam['index_symbol_ltp'] = "NSE:NIFTY BANK"
bankparam["option_expiry"] = "WEDNESDAY"
bankparam["strike_interval"] = 100
bankparam['lot'] = 15
bankparam['interest_rate'] = 0.065
bankparam['annualized_volatility'] = 0.2056
bankparam['timeframe']='minute'


bankniftyWindowClass = symbol_window_new.symbolWindow()
banknifty_vbox = bankniftyWindowClass.create_window(bankparam)

bankniftyWindowClass.nifty_expiry_week_w.disabled=True
'''
banknifty_vbox = symbol_window.create_window(bankparam)

'''


#------------------------------------------------------------------------------------------------
#----------------------------------------finnifty---------------------------------------------------
finparam = globalvar.g_finparam
finparam['index_exchange'] = "NSE"
finparam['index_symbol'] = ['NIFTY FIN SERVICE']
finparam['index_symbol_option'] = 'FINNIFTY'
finparam['index_symbol_ltp'] = "NSE:NIFTY FIN SERVICE"
finparam["option_expiry"] = "TUESDAY"
finparam["strike_interval"] = 50
finparam['lot'] = 25
finparam['interest_rate'] = 0.065
finparam['annualized_volatility'] = 0.203
finparam['timeframe']='minute'


#finnifty_vbox = symbol_window.create_window(finparam)
finniftyWindowClass = symbol_window_new.symbolWindow()
finnifty_vbox = finniftyWindowClass.create_window(finparam)

finniftyWindowClass.nifty_expiry_week_w.disabled=True
#----------------------------------------midcapnifty---------------------------------------------------

midcapparam = globalvar.g_midcapparam
midcapparam['index_exchange'] = "NSE"
midcapparam['index_symbol'] = ['NIFTY MID SELECT']
midcapparam['index_symbol_option'] = 'MIDCPNIFTY'
midcapparam['index_symbol_ltp'] = "NSE:NIFTY MID SELECT"
midcapparam["option_expiry"] = "MONDAY"
midcapparam["strike_interval"] = 25
midcapparam['lot'] = 50
midcapparam['interest_rate'] = 0.065
midcapparam['annualized_volatility'] = 0.2278
midcapparam['timeframe']='minute'


#midcapnifty_vbox = symbol_window.create_window(midcapparam)
midcapniftyWindowClass = symbol_window_new.symbolWindow()
midcapnifty_vbox = midcapniftyWindowClass.create_window(midcapparam)

midcapniftyWindowClass.nifty_expiry_week_w.disabled=True


#----------------------------------------sensex---------------------------------------------------
sensexparam = {}
sensexparam = globalvar.g_sensexparam
sensexparam['index_exchange'] = "BSE"
sensexparam['index_symbol'] = ["SENSEX"]
sensexparam['index_symbol_option'] = 'SENSEX'
sensexparam['index_symbol_ltp'] = "BSE:SENSEX"
sensexparam["strike_interval"] = 100
sensexparam["option_expiry"] = "FRIDAY"
sensexparam['lot'] = 10
sensexparam['interest_rate'] = 0.065
sensexparam['annualized_volatility'] = 0.2335
sensexparam['timeframe']='minute'

#sensex_vbox = symbol_window.create_window(sensexparam)
sensexWindowClass = symbol_window_new.symbolWindow()
sensex_vbox = sensexWindowClass.create_window(sensexparam)

sensexparam['expiry_frequency'] = 'Week'
sensexWindowClass.nifty_expiry_month_w.disabled=True


#----------------------------------------bankex---------------------------------------------------
bankexparam = {}
bankexparam = globalvar.g_bankexparam
bankexparam['index_exchange'] = "BSE"
bankexparam['index_symbol'] = ["BANKEX"]
bankexparam['index_symbol_option'] = 'BANKEX'
bankexparam['index_symbol_ltp'] = "BSE:BANKEX"
bankexparam["option_expiry"] = "MONDAY"
bankexparam["strike_interval"] = 100
bankexparam['lot'] = 15
bankexparam['interest_rate'] = 0.065
bankexparam['annualized_volatility'] = 0.2335
bankexparam['timeframe']='minute'

#bankex_vbox = symbol_window.create_window(bankexparam)
bankexWindowClass = symbol_window_new.symbolWindow()
bankex_vbox = bankexWindowClass.create_window(bankexparam)

bankexWindowClass.nifty_expiry_week_w.disabled=True

#------------------------------------------------------------------------------------------------

'''
stockparam = {}
stockparam = globalvar.g_stockparam
stockparam['index_exchange'] = "NSE"
stockparam['index_symbol'] = ["NIFTY"]
stockparam['index_symbol_option'] = 'NIFTY'
stockparam['index_symbol_ltp'] = "NSE:NIFTY"
stockparam["option_expiry"] = "MONDAY"
stockparam["strike_interval"] = 100
stockparam['lot'] = 15
stockparam['interest_rate'] = 0.065
stockparam['annualized_volatility'] = 0.2335
stockparam['timeframe']='minute'

stockWindowClass = symbol_window_new.symbolWindow()
stock_vbox = bankexWindowClass.create_stock_window(stockparam)
'''






#-----------------------------------------------------------------------------------------------
#-------------------------------------ACCOUNT----------------------------------------------------
# Create widgets for displaying account balance
equity_balance_w = widgets.Text(value=str(0), description='Equity Bal')
#commodity_balance_widget = widgets.Text(value=str(0), description='Commodity Balance:')
# Create widgets for displaying open positions
positions_w = widgets.Textarea(value=str(0), description='Position', layout=widgets.Layout(width='70%', height='400px'))

# Display the widgets
#display(equity_balance_widget, commodity_balance_widget, positions_widget)

def get_account_info():
    kite = globalvar.g_kite
    # Get account balance
    margins = kite.margins()
    equity_balance = margins['equity']['available']['live_balance']
    commodity_balance = margins['commodity']['available']['live_balance']
    
    # Get open positions
    positions = kite.positions()
    open_positions = positions['net']
    dfac = pd.DataFrame(open_positions)
    dfacshow = dfac[['tradingsymbol','quantity','average_price','last_price']]
    #display(dfacshow)
    
    equity_balance_w.value = str(equity_balance)
    positions_w.value = str(dfacshow)
try:
    get_account_info()    
except:
    pass
account_vbox = VBox([equity_balance_w, positions_w])





#----------------------DEFAULT DATA READ/WRITE----------------------------------------------
'''
DEFAULT_DATA_FILE = '../default_data.csv'
try:
    #default_data = f.open("DEFAULT.csv","r")
    default_data_read = pd.read_csv(DEFAULT_DATA_FILE,index_col=0)
    #print(default_data_read)
    nifty_exposure_amount_w.value = default_data_read.loc['nifty_exposure_amount','value']
    nifty_update_frequency_w.value = default_data_read.loc['nifty_update_frequency','value']
    nifty_supertrend_factor_w.value = default_data_read.loc['nifty_supertrend_factor']
except Exception as e:
    traceback.print_exc()

'''
#print()
'''
def write_default_data_file():
    index_vals = [[nifty_exposure_amount_w.value], [nifty_update_frequency_w.value], [nifty_supertrend_factor_w.value]]
    index_names = ['nifty_exposure_amount', 'nifty_update_frequency', 'nifty_supertrend_factor']
    
    default_data_write = pd.DataFrame(index_vals,index=index_names,columns=['value'])
    default_data_write.index.name='parameter'
    default_data_write.to_csv(DEFAULT_DATA_FILE)
#write_default_data_file()
'''

#------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------
#-----------------------------------------MASTER-----------------------------------------------
globalvar.g_out_live = out_live

universalparam = globalvar.g_universalparam#{}

universalparam['path'] = ""
universal_path_w = widgets.Text(value=current_path,description='Path', disabled=True, layout={'width': '90%'}, style=style)
#create_text(universalparam, 'path', current_path, 'Path')
#universal_path_w.disabled=True

universalparam['INDEX'] = {}

param['datasource'] = 'zerodha'
def nifty_datasource_f(change):
    param['datasource'] = change.new
nifty_datasource_w=widgets.Dropdown(options=['zerodha'],value='zerodha',\
                                  description='Data Source', layout={'width': '20%'}, style=style)
nifty_datasource_w.observe(nifty_datasource_f, 'value')


nifty_connect_zerodha_button = widgets.Button(description="Connect Zerodha",layout={'width': bw})
nifty_connect_zerodha_button.style.button_color = 'green'
nifty_connect_zerodha_button.on_click(functools.partial(on_connect_zerodha_button_clicked, param=param))


nifty_connect_finvasia_button = widgets.Button(description="Connect Finvasia",layout={'width': bw})
nifty_connect_finvasia_button.style.button_color = 'green'
nifty_connect_finvasia_button.on_click(functools.partial(on_connect_finvasia_button_clicked, param=param))



@out_live.capture(clear_output=True)
def on_zerodha_master_liquidate_clicked_thread(b, param):
    print("in zerodha liq")
    b.disabled=True
    try:
        kite = globalvar.g_kite
        tag = globalvar.magic_tag
        print(tag)
        zerodha.liquidate(kite, tag)
    except Exception as e:
        traceback.print_exc()
    b.disabled=False
    return    
master_liquidate_button = widgets.Button(description="Zerodha Liquidate")
master_liquidate_button.style.button_color = 'red'
master_liquidate_button.on_click(functools.partial(on_zerodha_master_liquidate_clicked_thread, param=universalparam))




@out_live.capture(clear_output=True)
def on_finvasia_master_liquidate_clicked_thread(b, param):
    print("in fin liq")
    #return
    #tag = globalvar.magic_tag
    #print(tag)
    b.disabled=True
    try:
        shoonya = globalvar.g_shoonya
        tag = globalvar.magic_tag
        print(tag)
        finvasia.liquidate(shoonya, tag)
    except Exception as e:
        traceback.print_exc()
    b.disabled=False
    return    
finvasia_master_liquidate_button = widgets.Button(description="Finvasia Liquidate")
finvasia_master_liquidate_button.style.button_color = 'red'
finvasia_master_liquidate_button.on_click(functools.partial(on_finvasia_master_liquidate_clicked_thread, param=universalparam))




#def universal_max_profit_f(change):
#    globalvar.max_profit = change.new
#universal_profit_w.observe(universal_max_profit_f,'value')


universal_overall_investment_w = create_floattext(universalparam, 'overall_investment', 300000.0, 'Overall Investment')

universal_profit_type_w = create_dropdown(universalparam, 'profit_type', ['Rupee','Percentage'], 'Rupee')
def universal_profit_type_f(change):
    if change.new=='Percentage':
        universal_max_profit_w.value = 100.0
        universal_max_loss_w.value = -50.0
    else:
        universal_max_profit_w.value = 10000000.0
        universal_max_loss_w.value = -20000000.0
    #param[param_name] = change.new
universal_profit_type_w.observe(universal_profit_type_f, 'value')

#globalvar.overall_investment = universalparam['overall_investment']
#def universal_overall_investment_f(change):
#    globalvar.overall_investment = change.new
#universal_overall_investment_w.observe(universal_overall_investment_f,'value')




universal_max_profit_w = create_floattext(universalparam, 'max_profit', 10000000.0, 'Universal Profit')
#globalvar.max_profit = universalparam['max_profit']
#def universal_max_profit_f(change):
#    globalvar.max_profit = change.new
#universal_max_profit_w.observe(universal_max_profit_f,'value')


universal_max_loss_w = create_floattext(universalparam, 'max_loss', -200000000.0, 'Universal Loss')
#globalvar.max_loss = universalparam['max_loss']
#def universal_max_loss_f(change):
#    globalvar.max_loss = change.new
#universal_max_loss_w.observe(universal_max_loss_f,'value')


universal_profit_w = create_text(universalparam, 'profit', str(0), 'Running Profit')
universal_profit_w.disabled=True
universalparam['profit'] = 0 #universalparam['max_profit']
universalparam['profit_mode'] = 'REAL'
universalparam['profit_w'] = universal_profit_w



universal_magic_tag_w = create_text(universalparam, 'magic_tag', "newhope", 'Magic Tag')
globalvar.magic_tag = universalparam['magic_tag']
def universal_magic_tag_f(change):
    globalvar.magic_tag = change.new
universal_magic_tag_w.observe(universal_magic_tag_f,'value')

universal_setting1 = HBox([universal_path_w])
universal_setting2 = HBox([nifty_datasource_w, nifty_connect_zerodha_button, nifty_connect_finvasia_button])
master1 = HBox([master_liquidate_button,finvasia_master_liquidate_button,universal_overall_investment_w,universal_magic_tag_w])
master2 = HBox([universal_profit_type_w,universal_max_profit_w, universal_max_loss_w, universal_profit_w])
master3 = HBox([master_liquidate_button,finvasia_master_liquidate_button])

master = VBox([universal_setting1, universal_setting2, master1, master2])
#----------------------------------------------------------------------------------------------------


#from ipywidgets import widgets
#tab_contents = ['NIFTY', 'BANKNIFTY','FINNIFTY','MIDCAPNIFTY','SENSEX','BANKEX']#, 'Account']
#children = [widgets.Text(description=name) for name in tab_contents]
tab = widgets.Tab()
#tab.children = [backtest_box, live_box, account_box]

tablist = [nifty_vbox, banknifty_vbox, finnifty_vbox, midcapnifty_vbox, sensex_vbox, bankex_vbox]
#tablist.append(stock_vbox)

tab.children = tablist#[nifty_vbox, banknifty_vbox, finnifty_vbox, midcapnifty_vbox, sensex_vbox, bankex_vbox]#, account_vbox]
#tab.titles = [str(i) for i in range(len(tab_contents))]
tab.set_title(0, 'NIFTY')
tab.set_title(1, 'BANKNIFTY')
tab.set_title(2, 'FINNIFTY')
tab.set_title(3, 'MIDCAPNIFTY')
tab.set_title(4, 'SENSEX')
tab.set_title(5, 'BANKEX')
#tab.set_title(6, 'ACCOUNT')
#tab.set_title(6, 'STOCK')

# Style the selected tab
#tab.selected_index = 0  # Set the first tab as selected
#tab.style.selected_tab_color = 'green'  # Change the color of the selected tab to red



GUIBox = VBox([master, tab, out_live])
#Box universal_box
#supertab_contents = ['System', 'Display']#, 'Account']
#supertab = widgets.Tab()
#supertab.children = [tradeTab]
#supertab.set_title(0, 'System')
#supertab.set_title(1, 'Display')
#supertab.set_title(2, 'Account')

