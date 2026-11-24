"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


#------------------------------------------------------------------------------------------------
#----------------------------------------NIFTY---------------------------------------------------
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


import globalvar

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

import trademanager

from ACCOUNT_DETAIL import PARAMETER_PASSWORD


DEBUG_MODE=True
DEBUG_MODE=False

style = {'description_width': 'initial'}
bw = '90%'


horizontal_line = widgets.HTML(value="<hr>")

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
    #fl = ['BACKTEST FILES']+glob.glob("./analysis/*BACKTEST.csv")
    #backtest_files_w.options = fl
    return
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
    print('STOPPING LIVE TRADE for :',param['index_symbol'])
    #global live_param
    #live_param['RUN_FOR_MINUTES'] = 0
    #globalvar.g_param['RUN_FOR_MINUTES'] = 0
    param['RUN_FOR_MINUTES'] = 0


@out_live.capture(clear_output=False)
def on_go_live_button_clicked(b, param):
    #print('STOPPING LIVE TRADE for :',param['index_symbol'])
    #global live_param
    #live_param['RUN_FOR_MINUTES'] = 0
    #globalvar.g_param['RUN_FOR_MINUTES'] = 0
    value = param['PLACE_ORDER']
    if value == False:
        param['PLACE_ORDER'] = True
    else:
        param['PLACE_ORDER'] = False
    
    if param['PLACE_ORDER']==True:
        b.style.button_color = 'yellow'
    else:
        b.style.button_color = 'brown'


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
    height = int(len(param['trade_items'])/width) #param['trade_table_height']
    scount=0
    vs = " "
    for j in range(1,height):
        for i in range(0,width):
            if(i==width-1):
                #item_set_value(vs, globalvar.g_param['trade_items'], i, j, width)
                wbutton = param['trade_items'][i+j*width]
                wbutton.layout.display = 'none'
                wbutton.disabled = False
                wbutton.style.button_color = 'green'
                #wbutton.on_click(callback, remove=True)
                wbutton._click_handlers.callbacks = []
            else:
                item_set_value(vs, param['trade_items'], i, j, width)
                param['trade_items'][i+j*width].style = {}#{'background': 'transparent'}
    #grid.children = new_values
    return




def create_window(param):
    #param = {}
    #param = globalvar.g_param
    #param['index_symbol'] = ["NIFTY 50"]
    #param['index_symbol_ltp'] = "NSE:NIFTY 50"
    #param["strike_interval"] = 50
    #param['interest_rate'] = 0.065
    #param['annualized_volatility'] = 0.24
    
    
    
    param['portfolio_dict'] = {}
    param['indicator_dict'] = {}
    param['live_trading'] = False
    param['use_streamer'] = True
    param['multitimeframe'] = False
    param['contract_list'] = {}
    param['stream_table'] = None
    param['backtest_point'] = 'C'
    param['trade_table_counter_start'] = False
    param['account_capital'] = 100000.0
    
    
    
    param['RUN_FOR_MINUTES'] = 50000
    def nifty_RUN_FOR_MINUTES_f(change):
        param['RUN_FOR_MINUTES'] = change.new
    nifty_RUN_FOR_MINUTES_w = widgets.IntText(value=param['RUN_FOR_MINUTES'],description='RUN_FOR_MINUTES',disabled=False, layout={'width': 'auto'}, style=style)
    nifty_RUN_FOR_MINUTES_w.observe(nifty_RUN_FOR_MINUTES_f, 'value')
    
    
    nifty_trade_direction_w = create_dropdown(param, 'trade_direction', ['LONG','SHORT'], 'SHORT')
    nifty_show_param_b = create_button(param, 'show_param', False, 'Show Param')
    
    
    param['backtest_date1'] = None
    def nifty_bk_dt1_f(change):
        param['backtest_date1'] = change.new
        print(param['backtest_date1'])
    nifty_bk_dt1_w = widgets.DatePicker(description='Backtest Start',disabled=False,layout={'width': '25%'}, style=style)
    nifty_bk_dt1_w.observe(nifty_bk_dt1_f,'value')
    
    
    param['backtest_date2'] = None
    def nifty_bk_dt2_f(change):
        param['backtest_date2'] = change.new
        print(param['backtest_date2'])
    nifty_bk_dt2_w = widgets.DatePicker(description='Backtest End',disabled=False,layout={'width': '25%'}, style=style)
    nifty_bk_dt2_w.observe(nifty_bk_dt2_f,'value')
    
    nifty_clearBacktestdate_button = widgets.Button(description="clearBacktestDates",layout={'width': '15%'})
    #clearBacktestdate_button.style.button_color = 'black'
    def on_nifty_clearBacktestdate_clicked(b):
        nifty_bk_dt1_w.value = None
        nifty_bk_dt2_w.value = None
    nifty_clearBacktestdate_button.on_click(on_nifty_clearBacktestdate_clicked)
    
    
    param['datasource'] = 'zerodha'
    def nifty_datasource_f(change):
        param['datasource'] = change.new
    nifty_datasource_w=widgets.Dropdown(options=['local','zerodha','finvasia'],value='zerodha',\
                                      description='Data Source', layout={'width': '20%'}, style=style)
    nifty_datasource_w.observe(nifty_datasource_f, 'value')
    #nifty_datasource_w.value = 'local'
    
    
    param['broker'] = 'finvasia'
    def nifty_broker_f(change):
        param['broker'] = change.new
    nifty_broker_w=widgets.Dropdown(options=['zerodha','finvasia'],value='finvasia',\
                                      description='Broker', layout={'width': '20%'}, style=style)
    nifty_broker_w.observe(nifty_broker_f, 'value')
    
    nifty_connect_broker_button = widgets.Button(description="Connect Broker")
    nifty_connect_broker_button.style.button_color = 'green'
    nifty_connect_broker_button.on_click(functools.partial(on_connect_broker_button_clicked, param=param))
    
    
    nifty_connect_zerodha_button = widgets.Button(description="Connect Zerodha",layout={'width': bw})
    nifty_connect_zerodha_button.style.button_color = 'green'
    nifty_connect_zerodha_button.on_click(functools.partial(on_connect_zerodha_button_clicked, param=param))
    
    nifty_trade_zerodha_w = create_checkbox(param, 'trade_zerodha', False, 'Trade Zerodha')
    nifty_trade_zerodha_w.layout={'width': '20%'}
    
    nifty_connect_finvasia_button = widgets.Button(description="Connect Finvasia",layout={'width': bw})
    nifty_connect_finvasia_button.style.button_color = 'green'
    nifty_connect_finvasia_button.on_click(functools.partial(on_connect_finvasia_button_clicked, param=param))
    
    nifty_trade_finvasia_w = create_checkbox(param, 'trade_finvasia', False, 'Trade Finvasia')
    nifty_trade_finvasia_w.layout={'width': '20%'}
    #nifty_connect_zerodha_button, nifty_trade_zerodha_w, nifty_connect_finvasia_button, nifty_trade_finvasia_w 
    
    nifty_disconnect_broker_button = widgets.Button(description="Disconnect Broker")
    nifty_disconnect_broker_button.style.button_color = 'red'
    nifty_disconnect_broker_button.on_click(functools.partial(on_disconnect_broker_button_clicked, param=param))
    
    
    
    
    
    param['show_detail_log'] = False
    def nifty_show_detail_log_f(change):
        param['show_detail_log'] = change.new
    nifty_show_detail_log_w = widgets.Checkbox(
        value=param['show_detail_log'],
        description='Show Log',
        disabled=False,
        indent=False,layout={'width': bw}, style=style
    )
    nifty_show_detail_log_w.observe(nifty_show_detail_log_f,'value')
    
    
    param['PLACE_ORDER'] = False
    def nifty_PLACE_ORDER_f(change):
        param['PLACE_ORDER'] = change.new
    nifty_PLACE_ORDER_w = widgets.Checkbox(
        value=param['PLACE_ORDER'],
        description='PLACE ORDER (BE CAREFUL! It will place live orders in your trade account)',
        disabled=False,
        indent=False,
        layout={'width': '100%'}
    )
    nifty_PLACE_ORDER_w.observe(nifty_PLACE_ORDER_f,'value')
    
    nifty_password_w = widgets.Password(description='Password:',placeholder='Enter password',)
    def nifty_check_password(change):
        if change['new'] == PARAMETER_PASSWORD:  # Replace 'your_password' with your actual password
            nifty_strategy_box.layout.display = 'block'
        else:
            nifty_strategy_box.layout.display = 'none'
    nifty_password_w.observe(nifty_check_password, names='value')
    
    
    nifty_run_backtest_button = widgets.Button(description="Backtest")
    nifty_run_backtest_button.style.button_color = 'orange'
    nifty_run_backtest_button.on_click(functools.partial(on_backtest_button_clicked_thread, symbol='RELIANCE', param=param))
    
    
    nifty_run_live_button = widgets.Button(description="START")
    nifty_run_live_button.style.button_color = 'green'
    nifty_run_live_button.on_click(functools.partial(on_live_button_clicked_thread, symbol='RELIANCE', param=param))
    
    nifty_stop_live_button = widgets.Button(description="STOP")
    nifty_stop_live_button.style.button_color = 'red'
    nifty_stop_live_button.on_click(functools.partial(on_stop_live_button_clicked, param=param))


    nifty_go_live_button = widgets.Button(description="Go Live")
    nifty_go_live_button.style.button_color = 'brown'
    nifty_go_live_button.on_click(functools.partial(on_go_live_button_clicked, param=param))


    
    
    nifty_start_time_w = create_boundedinttext(param, 'start_time', 915, 915,1530,1, 'Start Time')
    nifty_stop_order_time_w = create_boundedinttext(param, 'stop_order_time', 1515, 915,1530,1, 'Entry End Time')
    nifty_exit_time_w = create_boundedinttext(param, 'exit_time', 1525, 915,1530,1, 'SquareOff Time')
    
    nifty_max_profit_w = create_floattext(param, 'max_profit', 5000.0, 'Max Profit')
    globalvar.max_profit = param['max_profit']
    def nifty_max_profit_f(change):
        globalvar.max_profit = change.new
    nifty_max_profit_w.observe(nifty_max_profit_f,'value')
    
    
    nifty_max_loss_w = create_floattext(param, 'max_loss', -2000.0, 'Max Loss')
    globalvar.max_loss = param['max_loss']
    def nifty_max_loss_f(change):
        globalvar.max_loss = change.new
    nifty_max_loss_w.observe(nifty_max_loss_f,'value')
    
    nifty_show_plot_w = create_checkbox(param, 'show_plot', False, 'Show Plot')
    
    nifty_single_trade_w = create_checkbox(param, 'single_trade', True, 'Single Trade')
    nifty_single_trade_w.disabled=True
    nifty_use_lot_w = create_checkbox(param, 'useLot', False, 'Use Lot')
    #nifty_lot_w = create_boundedinttext(param, 'lot', 25, 25, 1000, 25, 'Nifty Lot')
    #nifty_strike_interval_w = create_inttext(param, 'strike_interval', 50, 'Strike Interval')
    nifty_trade_direction_w = create_dropdown(param, 'tradeDirection', ['LONG','SHORT','BOTH'], 'LONG','Trade Direction')
    
    
    nifty_update_frequency_w = create_boundedinttext(param, 'update_frequency', 1, 1, 3600, 1, 'Update Timeframe(sec)')
    
    nifty_exposure_amount_w = create_floattext(param, 'trade_capital', 25000.0, 'Exposure')
    nifty_lower_exposure_amount_w = create_floattext(param, 'lower_exposure_trade_capital', 1000.0, 'Lower Exposure')
    nifty_lower_exposure_price_w = create_floattext(param, 'lower_exposure_price', 20.0, 'Lower Exposure Price')
    
    nifty_use_martingale_w = create_checkbox(param, 'use_martingale', False, 'Use Martingale')
    nifty_martingale_length_w = create_inttext(param, 'martingale_length', 2, 'Martingale Length')


    nifty_expiry_frequency_w = create_dropdown(param, 'expiry_frequency', ['Week','Month'], 'Month', 'Expiry Frequency')
    nifty_expiry_w = create_dropdown(param, 'expiry_week', ['CurrentWeek','NextWeek'], 'CurrentWeek','Expiry')
    nifty_strike_w = create_dropdown(param, 'strike', ['ATM','ITM1','OTM1','ITM2','OTM2','ITM3','OTM3'], 'ATM','Strike')
    
    
    nifty_use_stop_loss_w = create_checkbox(param, 'use_stop_loss', False, 'Use StopLoss')
    nifty_stop_loss_type_w = create_dropdown(param, 'stop_loss_type', ['Rupee','Points'], 'Rupee')
    nifty_SL_w = create_floattext(param, 'SL', 5000, 'stop loss')
    
    nifty_use_target_w = create_checkbox(param, 'use_target', False, 'Use TargetProfit')
    nifty_target_type_w = create_dropdown(param, 'target_type', ['Rupee','Points'], 'Rupee')
    nifty_target_w = create_floattext(param, 'target', 10000, 'target')
    
    nifty_use_trail_w = create_checkbox(param, 'use_trail', False, 'Use Trail')
    nifty_trail_type_w = create_dropdown(param, 'trail_type', ['Rupee','Points'], 'Rupee')
    nifty_trail_w = create_floattext(param, 'trail_by', 3000, 'trail stop loss')
    nifty_trail_step_w = create_floattext(param, 'trail_step', 1, 'trail step')
    
    nifty_use_rsi_w = create_checkbox(param, 'use_rsi', False, 'Use RSI')
    nifty_rsi_length_w = create_inttext(param, 'rsi_length', 14, 'RSI Length')
    nifty_rsima_type_w = create_dropdown(param, 'rsima_type', ['SMA','EMA'], 'SMA','MA Type')
    nifty_rsima_length_w = create_inttext(param, 'rsima_length', 14, 'RSI MA Length')
    
    
    nifty_use_supertrend_w = create_checkbox(param, 'use_supertrend', True, 'Use Supertrend')
    nifty_supertrend_length_w = create_inttext(param, 'supertrend_length', 10, 'Supertrend Length')
    nifty_supertrend_factor_w = create_boundedfloattext(param, 'supertrend_factor', 1.0, 0.1, 10.0, 0.1, 'Supertrend Factor')
    
    
    nifty_use_jurikma_w = create_checkbox(param, 'use_jurikma', False, 'Use Jurik MA')
    nifty_jurik_length_w = create_inttext(param, 'jurik_length', 7, 'Jurik Length')
    nifty_jurik_phase_w = create_inttext(param, 'jurik_phase', 50, 'Jurik Phase')
    nifty_jurik_power_w = create_inttext(param, 'jurik_power', 2, 'Jurik Power')
    
    
    nifty_renko_brick_type_w = create_dropdown(param, 'renko_brick_type', ['Points','StrikeLTPPercent','Calculation'], 'Points','Renko Brick Type')
    
    #nifty_renko_atr_timeframe_w = create_dropdown(param, 'renko_atr_timeframe', ['H1','H4','D'], 'H1','Renko ATR TimeFrame')
    nifty_renko_atr_input_type_w = create_dropdown(param, 'renko_atr_input_type', ['Manual','Automatic'], 'Manual','Renko ATR Input Type')
    nifty_renko_atr_input_value_w = create_floattext(param, 'renko_atr_input_value', 150.0, 'ATR Input Value')
    nifty_renko_atr_timeframe_w = create_inttext(param, 'index_atr_timeframe_hour', 6, 'ATR TimeFrame Hour')
    nifty_renko_atr_period_w = create_inttext(param, 'index_atr_period', 5, 'ATR Period')
    nifty_renko_atr_lowertimeframe_w = create_inttext(param, 'index_atr_lowertimeframe', 15,'ATR Lower TimeFrame Minute')
    
    nifty_renko_brick_size_w = create_floattext(param, 'renko_brick_size', 5.0, 'Renko Brick Size')
    
    
    nifty_use_previous_day_signal_w = create_checkbox(param, 'nifty_use_previous_day_signal', True, 'Use Previous Day Signal') 
    
    
    
    #--------------------create diplay box-------------------------------------
    nifty_setting1 = HBox([nifty_datasource_w, nifty_connect_zerodha_button, nifty_connect_finvasia_button])
    nifty_setting2 = HBox([nifty_show_detail_log_w])
    nifty_uni_hbox1 = HBox([nifty_max_profit_w, nifty_max_loss_w])
    nifty_uni_hbox2 = HBox([nifty_start_time_w, nifty_stop_order_time_w, nifty_exit_time_w]) 
    nifty_universal_box = VBox([nifty_uni_hbox2])
    
    
    nifty_hbox1 = HBox([nifty_exposure_amount_w, nifty_lower_exposure_price_w, 
                        nifty_lower_exposure_amount_w,nifty_use_martingale_w,nifty_martingale_length_w])
    nifty_hbox11 = HBox([nifty_use_target_w,nifty_target_type_w,nifty_target_w])
    nifty_hbox12 = HBox([nifty_use_stop_loss_w,nifty_stop_loss_type_w,nifty_SL_w])
    nifty_hbox13 = HBox([nifty_use_trail_w,nifty_trail_type_w,nifty_trail_w])
    
    nifty_hbox2 = HBox([nifty_expiry_w, nifty_strike_w, nifty_update_frequency_w])
    
    
    nifty_hbox3 = HBox([nifty_renko_brick_type_w,  nifty_renko_brick_size_w])
    nifty_hbox31 = HBox([nifty_renko_atr_input_type_w ,nifty_renko_atr_input_value_w,
                         nifty_renko_atr_timeframe_w, nifty_renko_atr_period_w,  nifty_renko_atr_lowertimeframe_w])
    nifty_hbox_rsi = HBox([nifty_use_rsi_w, nifty_rsi_length_w, nifty_rsima_type_w, nifty_rsima_length_w])
    nifty_hbox_supertrend = HBox([nifty_use_supertrend_w, nifty_supertrend_length_w, nifty_supertrend_factor_w])
    nifty_hbox_jurikma = HBox([nifty_use_jurikma_w, nifty_jurik_length_w, nifty_jurik_phase_w, nifty_jurik_power_w])
    
    nifty_hbox5 = HBox([nifty_use_previous_day_signal_w])
    
    nifty_strategy_box = VBox([nifty_hbox3,nifty_hbox31,nifty_hbox_rsi, nifty_hbox_supertrend, nifty_hbox_jurikma, nifty_hbox5])
    nifty_strategy_box.layout.display = 'none'
    
    nifty_hbox6 = HBox([nifty_run_backtest_button, nifty_run_live_button, 
                        nifty_stop_live_button, nifty_go_live_button,
                        nifty_trade_zerodha_w,nifty_trade_finvasia_w ])
    nifty_hbox7 = HBox([reset_backtest])
    nifty_hbox8 = HBox([reset_live])
    nifty_hbox9 = HBox([out_live_table])
    nifty_hbox10 = HBox([out_live])
    
    
    
    
    param['trade_table_width'] = 12
    param['trade_table_height'] = 2
    iw = param['trade_table_width']
    #iwx = param['trade_table_height']*iw-1
    #globalvar.g_param['trade_items'] = [widgets.Label("") for i in range(iwx)]
    
    #globalvar.g_param['trade_items'] = []
    param['trade_items'] = []
    
    
    #styles = [{'background-color': 'lightblue'},{'background-color': 'lightgray'}]
    create_global_trade_items(param)
    #nifty_tradebox = widgets.GridBox(globalvar.g_param['trade_items'], layout=widgets.Layout(grid_template_columns="repeat(12, 100px)"))
    nifty_tradebox = widgets.GridBox(param['trade_items'], 
                                     layout=widgets.Layout(grid_template_columns='175px 90px 95px 120px 75px 100px 75px 130px 130px 120px 80px 100px'))
    #nifty_tradebox = widgets.GridBox(globalvar.g_param['trade_items'], 
    #                                 layout=widgets.Layout(grid_template_columns='auto auto auto auto auto auto auto auto auto auto auto auto'))
    #width='max-content',#layout={'width': 'max-content'}
    #param['']
    param['tradebox'] = nifty_tradebox
    #nifty_tradebox.children = globalvar.g_param['trade_items']
    
    
    
    nifty_index_value_w =  create_floattext(param, 'index_value', 0.0, 'Index value')
    nifty_index_value_w.disabled=True
    param['index_value_w'] = nifty_index_value_w
    
    nifty_total_pnl_w =  create_floattext(param, 'total_pnl', 0.0, 'PnL')
    nifty_total_pnl_w.disabled=True
    param['total_pnl_w'] = nifty_total_pnl_w
    
    #nifty_atm_w =  create_floattext(param, 'atm_value', 0.0, 'ATM value')
    
    #nifty_selected_strike_call_w =  create_text(param, 'selected_strike_call', '', 'ATM')
    #nifty_selected_strike_call_value_w =  create_floattext(param, 'selected_strike_call_value', 0.0, 'CALL value')
    
    nifty_selected_strike_call_w =  create_text(param, 'selected_strike_call', '', 'CALL')
    param['selected_strike_call_w'] = nifty_selected_strike_call_w
    
    nifty_selected_strike_call_value_w =  create_floattext(param, 'selected_strike_call_value', 0.0, 'CALL value')
    nifty_selected_strike_call_value_w.disabled=True
    param['selected_strike_call_value_w'] = nifty_selected_strike_call_value_w
    
    nifty_selected_strike_call_signal_w =  create_floattext(param, 'selected_strike_call_signal', 0.0, 'CALL signal')
    nifty_selected_strike_call_signal_w.disabled=True
    param['selected_strike_call_signal_w'] = nifty_selected_strike_call_signal_w
    
    nifty_selected_strike_call_signal_time_w =  create_text(param, 'selected_strike_call_signal_time', '', 'CALL signal time')
    #nifty_selected_strike_call_signal_time_w.disabled=True
    param['selected_strike_call_signal_time_w'] = nifty_selected_strike_call_signal_time_w
    
    
    
    
    
    
    nifty_selected_strike_put_w =  create_text(param, 'selected_strike_put', '', 'PUT')
    param['selected_strike_put_w'] = nifty_selected_strike_put_w
    
    nifty_selected_strike_put_value_w =  create_floattext(param, 'selected_strike_put_value', 0.0, 'PUT value')
    nifty_selected_strike_put_value_w.disabled=True
    param['selected_strike_put_value_w'] = nifty_selected_strike_put_value_w
    
    nifty_selected_strike_put_signal_w =  create_floattext(param, 'selected_strike_put_signal', 0.0, 'PUT signal')
    nifty_selected_strike_put_signal_w.disabled=True
    param['selected_strike_put_signal_w'] = nifty_selected_strike_put_signal_w
    
    nifty_selected_strike_put_signal_time_w =  create_text(param, 'selected_strike_put_signal_time', '', 'PUT signal time')
    #nifty_selected_strike_put_signal_time_w.disabled=True
    param['selected_strike_put_signal_time_w'] = nifty_selected_strike_put_signal_time_w
    

    DEFAULT_DATA_FILE = '../default_data.xlsx'
    try:
        #default_data = f.open("DEFAULT.csv","r")
        #default_data_read = pd.read_csv(DEFAULT_DATA_FILE,index_col=0)
        default_data_read = pd.read_excel(DEFAULT_DATA_FILE, sheet_name=param['index_symbol_option'], index_col=0)
        #print(default_data_read)
        param['lot'] = default_data_read.loc['lot','value']
        nifty_exposure_amount_w.value = default_data_read.loc['exposure_amount','value']
        nifty_lower_exposure_amount_w.value = default_data_read.loc['lower_exposure_amount','value']
        nifty_lower_exposure_price_w.value = default_data_read.loc['lower_exposure_price','value']
        nifty_renko_atr_input_value_w.value = default_data_read.loc['renko_atr_input_value','value']
        nifty_update_frequency_w.value = default_data_read.loc['update_frequency','value']
        nifty_supertrend_length_w.value = default_data_read.loc['supertrend_length','value']
        nifty_supertrend_factor_w.value = default_data_read.loc['supertrend_factor','value']
    except Exception as e:
        traceback.print_exc()

    #print()
    def write_default_data_file():
        index_vals = [[param['lot']], [nifty_exposure_amount_w.value], [nifty_lower_exposure_amount_w.value],
                      [nifty_lower_exposure_price_w.value], [nifty_renko_atr_input_value_w.value], 
                      [nifty_update_frequency_w.value], [ nifty_supertrend_length_w.value], [nifty_supertrend_factor_w.value]]
        index_names = ['lot', 'exposure_amount', 'lower_exposure_amount','lower_exposure_price',
                       'renko_atr_input_value','update_frequency', 'supertrend_length','supertrend_factor']
        
        default_data_write = pd.DataFrame(index_vals,index=index_names,columns=['value'])
        default_data_write.index.name='parameter'
        #data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]}
        #df = pd.DataFrame(data)
        # Writing to Excel with a specific sheet name
        #with pd.ExcelWriter(DEFAULT_DATA_FILE) as writer:
        #    default_data_write.to_excel(writer, sheet_name=param['index_symbol_option'], index=False)
        with pd.ExcelWriter(DEFAULT_DATA_FILE, mode='a',if_sheet_exists='replace', engine='openpyxl') as writer:
            default_data_write.to_excel(writer, sheet_name=param['index_symbol_option'])
    #write_default_data_file()


    
    
    
    nifty_databox1 = HBox([nifty_index_value_w, nifty_total_pnl_w])
    nifty_databox2 = HBox([nifty_selected_strike_call_w, nifty_selected_strike_call_value_w,  
                          nifty_selected_strike_call_signal_w, nifty_selected_strike_call_signal_time_w])
    nifty_databox3 = HBox([nifty_selected_strike_put_w, nifty_selected_strike_put_value_w,  
                          nifty_selected_strike_put_signal_w, nifty_selected_strike_put_signal_time_w])
    nifty_databox = VBox([nifty_databox1,nifty_databox2,nifty_databox3,horizontal_line])
    
    
    
    
    nifty_vbox = VBox([nifty_setting2, nifty_hbox1, nifty_hbox11, nifty_hbox12, nifty_hbox13, 
                       nifty_hbox2, nifty_universal_box, nifty_password_w, horizontal_line, nifty_strategy_box, nifty_hbox6, 
                       horizontal_line, nifty_databox, nifty_tradebox, 
                       nifty_hbox7, nifty_hbox8, nifty_hbox9, nifty_hbox10])

    
    

    
    return nifty_vbox


