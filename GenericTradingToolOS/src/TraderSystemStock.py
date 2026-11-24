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

# from ShoonyaApipymaster.api_helper import ShoonyaApiPy

from initialize import g_tick_dict, g_param, STRATEGY_LIST
#from initialize import g_tick_dict, param, g_param, STRATEGY_LIST
from ACCOUNT_DETAIL import IP, PORT, USERNAME, PASSWORD, BROKER,PARAMETER_PASSWORD

from ACCOUNT_DETAIL import ZERODHA_USER_ID, FINVASIA_USER_ID

import trademanager
importlib.reload(trademanager)
#from trademanager import run_system
import symbol_window
importlib.reload(symbol_window)


import symbol_window_new
importlib.reload(symbol_window_new)

# Get the current working directory
current_path = os.getcwd()
#---------------------------initiaze chart varaiables--------------------------------------- 
globalvar.g_market_dict = {"INDEX":{}, "EQUITY":{}, "OPTION":{},"FUTURES":{},"FOREX":{}}

#------------------------widget templates-----------------------------------------------------
style = {'description_width': 'initial'}
bw = '90%'



reset_backtest = widgets.Output(layout={'border': '1px solid yellow', 'width':'100%'})
reset_live = widgets.Output(layout={'border': '1px solid green', 'width':'100%'})

out_live = widgets.Output()
out_live_table = widgets.Output()
out_live_position = widgets.Output()



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
    try:
        stockWindowClass.get_account_info(broker='ZERODHA')
    except Exception as e:
        print(e)
    return


@out_live.capture(clear_output=False)
def on_connect_finvasia_button_clicked(b, param):
    print('CONNECTING FINVASIA')
    finvasia.create_shoonya()
    b.disabled = True
    try:
        stockWindowClass.get_account_info(broker='FINVASIA')
    except Exception as e:
        print(e)
    return











account_w = widgets.Textarea(
    value='',
    #placeholder='',
    description='Account Details',
    disabled=False,
    layout={'width':'100%'},)
#account_w.observe(account_f,'value')
#account_w.value = dfa.to_string()

# def html_f(change):
#    html_w.value = change.new
# html_w = widgets.HTML(value=live_param['live_output'])
# html_w.observe(html_f,'value')
# ---------------------------PASSWORD--------------------------------------------------------------
# Create a password widget



# Create a VBox to hide
# hidden_box = widgets.VBox([widgets.Label("This is a hidden box")])
# Hide the VBox initially
# hidden_box.layout.display = 'none'
# Display the widgets
# display(password)
# display(hidden_box)

horizontal_line = widgets.HTML(value="<hr>")

'''
param['account_capital'] = 100000.0
def account_capital_f(change):
    param['account_capital'] = change.new
account_capital_w=widgets.FloatText(value=param['account_capital'],description='Trade Capital',disabled=False, layout={'width': bw}, style=style)
account_capital_w.observe(account_capital_f,'value')
'''



# ------------------------------------------------------------------------------------------------


stockparam = {}
stockparam = globalvar.g_stockparam
stockparam['index_exchange'] = "NSE"
stockparam['index_symbol'] = ["NIFTY"]
stockparam['index_symbol_option'] = 'STOCK'
stockparam['index_symbol_ltp'] = "NSE:NIFTY"
stockparam["option_expiry"] = "TUESDAY"
stockparam["strike_interval"] = 100
stockparam['lot'] = 15
stockparam['interest_rate'] = 0.065
stockparam['annualized_volatility'] = 0.2335
stockparam['timeframe']='minute'

stockWindowClass = symbol_window_new.symbolWindow()
stock_vbox = stockWindowClass.create_stock_window(stockparam)

stockparam['single_trade']=False 






#-----------------------------------------------------------------------------------------------
#-------------------------------------ACCOUNT----------------------------------------------------
# Create widgets for displaying account balance
equity_balance_w = widgets.Text(value=str(0), description='Equity Bal')
#commodity_balance_widget = widgets.Text(value=str(0), description='Commodity Balance:')
# Create widgets for displaying open positions
positions_w = widgets.Textarea(value=str(0), description='Position', layout=widgets.Layout(width='70%', height='400px'))

# Display the widgets
# display(equity_balance_widget, commodity_balance_widget, positions_widget)
'''
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
'''



#----------------------------------------------------------------------------------------------
#-----------------------------------------MASTER-----------------------------------------------
globalvar.g_out_live = out_live

universalparam = globalvar.g_universalparam#{}

universalparam['path'] = ""
universal_path_w = widgets.Text(value=current_path,description='Path', disabled=True, layout={'width': '90%'}, style=style)
#create_text(universalparam, 'path', current_path, 'Path')
#universal_path_w.disabled=True

universalparam['INDEX'] = {}

stockparam['datasource'] = 'zerodha'
def nifty_datasource_f(change):
    stockparam['datasource'] = change.new
nifty_datasource_w=widgets.Dropdown(options=['zerodha'],value='zerodha',\
                                  description='Data Source', layout={'width': '20%'}, style=style)
nifty_datasource_w.observe(nifty_datasource_f, 'value')


nifty_connect_zerodha_button = widgets.Button(description="Connect Zerodha:"+ZERODHA_USER_ID,layout={'width': bw})
nifty_connect_zerodha_button.style.button_color = 'green'
nifty_connect_zerodha_button.on_click(functools.partial(on_connect_zerodha_button_clicked, param=stockparam))


nifty_connect_finvasia_button = widgets.Button(description="Connect Finvasia:"+FINVASIA_USER_ID,layout={'width': bw})
nifty_connect_finvasia_button.style.button_color = 'green'
nifty_connect_finvasia_button.on_click(functools.partial(on_connect_finvasia_button_clicked, param=stockparam))



@out_live.capture(clear_output=True)
def on_zerodha_master_liquidate_clicked_thread(b, param):
    print("in zerodha liq")
    b.disabled=True
    try:
        kite = globalvar.g_kite
        tag = globalvar.magic_tag
        print(tag)
        zerodha.liquidate(kite, tag, 1)
        print("waiting to check liquidation")
        time.sleep(3)
        bal, df = zerodha.get_account_info()
        if not df.empty:
            print("not fully liquidated..... liquidating again")
            zerodha.liquidate(kite, tag, 1)
    except Exception as e:
        traceback.print_exc()
    b.disabled=False
    return    
zerodha_master_liquidate_button = widgets.Button(description="Zerodha Liquidate")
zerodha_master_liquidate_button.style.button_color = 'red'
zerodha_master_liquidate_button.on_click(functools.partial(on_zerodha_master_liquidate_clicked_thread, param=universalparam))




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
        print("waiting to check liquidation")
        time.sleep(3)
        bal, df = finvasia.get_account_info()
        if not df.empty:
            print("not fully liquidated..... liquidating again")
            finvasia.liquidate(shoonya, tag)
        else:
            print("fully liquidated")
    except Exception as e:
        traceback.print_exc()
    b.disabled=False
    return    
finvasia_master_liquidate_button = widgets.Button(description="Finvasia Liquidate")
finvasia_master_liquidate_button.style.button_color = 'red'
finvasia_master_liquidate_button.on_click(functools.partial(on_finvasia_master_liquidate_clicked_thread, param=universalparam))




# def universal_max_profit_f(change):
#    globalvar.max_profit = change.new
# universal_profit_w.observe(universal_max_profit_f,'value')


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

# globalvar.overall_investment = universalparam['overall_investment']
# def universal_overall_investment_f(change):
#    globalvar.overall_investment = change.new
# universal_overall_investment_w.observe(universal_overall_investment_f,'value')




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



universal_magic_tag_w = create_text(universalparam, 'magic_tag', "saturn", 'Magic Tag')
globalvar.magic_tag = universalparam['magic_tag']
def universal_magic_tag_f(change):
    globalvar.magic_tag = change.new
universal_magic_tag_w.observe(universal_magic_tag_f,'value')

universal_setting1 = HBox([universal_path_w])
universal_setting2 = HBox([nifty_datasource_w, nifty_connect_zerodha_button, nifty_connect_finvasia_button])
master1 = HBox([zerodha_master_liquidate_button,finvasia_master_liquidate_button,universal_overall_investment_w,universal_magic_tag_w])
master2 = HBox([universal_profit_type_w,universal_max_profit_w, universal_max_loss_w, universal_profit_w])
#master3 = HBox([zerodha_master_liquidate_button,finvasia_master_liquidate_button])

master = VBox([universal_setting1, universal_setting2, master1, master2])
#----------------------------------------------------------------------------------------------------


#from ipywidgets import widgets
#tab_contents = ['NIFTY', 'BANKNIFTY','FINNIFTY','MIDCAPNIFTY','SENSEX','BANKEX']#, 'Account']
#children = [widgets.Text(description=name) for name in tab_contents]
#tab = widgets.Tab()
#tab.children = [backtest_box, live_box, account_box]

#tablist = []
#tablist.append(stock_vbox)

#tab.children = tablist#[nifty_vbox, banknifty_vbox, finnifty_vbox, midcapnifty_vbox, sensex_vbox, bankex_vbox]#, account_vbox]
#tab.titles = [str(i) for i in range(len(tab_contents))]
#tab.set_title(0, 'SCANNER')
#tab.set_title(1, 'SETTING')
#tab.set_title(6, 'ACCOUNT')
#tab.set_title(6, 'STOCK')

# Style the selected tab
# tab.selected_index = 0  # Set the first tab as selected
# tab.style.selected_tab_color = 'green'  # Change the color of the selected tab to red



#GUIBox = VBox([master, tab, out_live])
GUIBox = VBox([master, stock_vbox, out_live])
#Box universal_box
#supertab_contents = ['System', 'Display']#, 'Account']
#supertab = widgets.Tab()
#supertab.children = [tradeTab]
#supertab.set_title(0, 'System')
#supertab.set_title(1, 'Display')
#supertab.set_title(2, 'Account')

