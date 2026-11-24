"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import math
import numpy as np
import pandas as pd
import pytz
import datetime
from collections import OrderedDict
import glob
import traceback
import ast
import re

from account import get_access_token
import globalvar
import techlib

from initialize import DATAPATH
#from fyers_access import FYERS_ACCESS_TOKEN
import concurrent.futures

def create_candle(candle_=None):
    if candle_==None:
        candle_={}
    
    'signal data'
    #candle_['stoplossvalue'] = np.nan
    #candle_['takeprofitvalue'] = np.nan
    #candle_['totalvolumeday'] = 0
    candle_['long_signal'] = 0
    candle_['short_signal'] = 0
    candle_['sell_signal'] = 0
    candle_['cover_signal'] = 0
    
    candle_['comment'] = ''
    return candle_


def create_portfolio(param):
    for symbol in param['instrument_symbol_list']:
        pass
            
    

def get_backdata(param, mtfcandles_dict, program=None):
    if param['datasource']=='local':
        historyData_dict = get_backdata_local(param, mtfcandles_dict)
    if param['datasource']=='zerodha':
        historyData_dict = get_backdata_zerodha(param, mtfcandles_dict)
    if param['datasource']=='finvasia':
        historyData_dict = get_backdata_finvasia(param, mtfcandles_dict)
    if param['datasource']=='fyers':
        historyData_dict = get_backdata_fyers(param, mtfcandles_dict)
    return historyData_dict


def get_backdata_local(param, mtfcandles_dict):
    historyData_dict = {}
    
    if param['datasource']=='local':
        f = open('./data/localtest.txt','r')
        content = f.read()
        f.close()
    
    #instrument_symbol_list = param['instrument_symbol_list']
    instrument_symbol_list_str = content
    print("LOCAl DATA STRING->",type(instrument_symbol_list_str), instrument_symbol_list_str)
    #content
    instrument_symbol_list = ast.literal_eval(instrument_symbol_list_str)
    print("LOCAl DATA LIST->",type(instrument_symbol_list), instrument_symbol_list)
    
    if param['multitimeframe']:
        cols = ['datetime','close','open','high','low','volume']
        '''
            'close2min','open2min','high2min','low2min',
            'close3min','open3min','high3min','low3min',
            'close4min','open4min','high4min','low4min',
            'close5min','open5min','high5min','low5min',
           'close10min','open10min','high10min','low10min',
           'close15min','open15min','high15min','low15min',
            'close20min','open20min','high20min','low20min',
            'close30min','open30min','high30min','low30min',
            'close60min','open60min','high60min','low60min'
           ]
           '''
    else:
        cols = ['datetime','close','open','high','low','volume']

    market_dict = globalvar.g_market_dict
    atr_timeframe = str(param["index_atr_timeframe_hour"])+"H"
    for symbol in instrument_symbol_list:
        try:    
            filename = symbol+'.csv'
            filepath = './data/'+filename
            print(filepath)
            df = pd.read_csv(filepath,usecols=cols)
            #print(df.dtypes)
            df['datetime'] = pd.to_datetime(df['datetime'])
            #print(df.dtypes)
            
            if "FUT" in symbol:
                if atr_timeframe in symbol:
                    symbol=symbol.replace(atr_timeframe,"")
                    if(len( market_dict["INDEX"])==0): market_dict["INDEX"][symbol] = {}
                    market_dict["INDEX"][symbol][atr_timeframe] = df.to_dict('records')
                    if param['show_detail_log']: print(market_dict["INDEX"][symbol][atr_timeframe][0])
                    if param['show_detail_log']: print(market_dict["INDEX"][symbol][atr_timeframe][-1])
                else:
                    if(len( market_dict["INDEX"])==0): market_dict["INDEX"][symbol] = {}
                    market_dict["INDEX"][symbol]["1min"] = df.to_dict('records')
                    if param['show_detail_log']: print(market_dict["INDEX"][symbol]["1min"][0])
                    if param['show_detail_log']: print(market_dict["INDEX"][symbol]["1min"][-1])
                print(market_dict["INDEX"].keys())
                continue
            #df = df_multiframe(df, param, symbol)
            
            
            historyData_dict[symbol] = df.to_dict('records')
            print(symbol+' local backdata interval:')
            print(historyData_dict[symbol][0])
            print(historyData_dict[symbol][-1])
        except:
            print('offline data read failed for:',symbol)
    return historyData_dict



def get_nse_instrument_token(kite, symbol, param):
    #instruments = kite.instruments("NSE")
    if param['index_exchange']=="NSE":instruments = kite.instruments("NSE")
    elif param['index_exchange']=="BSE":instruments = kite.instruments("BSE")
    #f = open("nse_ins","w")
    #f.write(str(instruments))
    #f.close()
    #print(type(instruments))
    for instrument in instruments:
        #if "NIFTY" in instrument['tradingsymbol']:
        #    print(instrument)
        if instrument['tradingsymbol'] == symbol:
            print(instrument)
            return instrument['instrument_token']
    return None


def get_nfo_instrument_token(kite, symbol, param):
    #instruments = kite.instruments("NFO")
    '''
    try:
        if symbol in globalvar.g_instrument_dict.keys():
            token = globalvar.g_instrument_dict[symbol]['token']
            return token
    except:
        pass
    '''
    
    if param['index_exchange']=="NSE":instruments = kite.instruments("NFO")
    elif param['index_exchange']=="BSE":instruments = kite.instruments("BFO")
    #print(type(instruments))
    '''
    for instrument in instruments:
        globalvar.g_instrument_dict[symbol] = {}
        globalvar.g_instrument_dict[symbol]['token'] = ins_token
        globalvar.g_instrument_dict[symbol]['underlying'] = name
    '''    
    
    for instrument in instruments:
        #if "NIFTY" in instrument['tradingsymbol']:
        #    print(instrument)
        if instrument['tradingsymbol'] == symbol:
            #print(instrument)
            return instrument['instrument_token']
    
    return None



def get_nfo_instrument(kite, symbol, param):
    #instruments = kite.instruments("NFO")
    try:
        if symbol in globalvar.g_instrument_dict.keys():
            if 'token' in globalvar.g_instrument_dict[symbol].keys():
                instrument = globalvar.g_instrument_dict[symbol]
                return instrument
    except:
        pass
        
    if param['index_exchange']=="NSE":instruments = kite.instruments("NFO")
    elif param['index_exchange']=="BSE":instruments = kite.instruments("BFO")
    #print(type(instruments))
    
    '''
    for instrument in instruments:
        tradingsymbol = instrument['tradingsymbol']
        if tradingsymbol not in globalvar.g_instrument_dict.keys():
            globalvar.g_instrument_dict[tradingsymbol] = {}
        for k, v in instrument.items():
            globalvar.g_instrument_dict[tradingsymbol][k] = v #instrument[]
        #globalvar.g_instrument_dict[symbol]['tradingsymbol'] = instrument['tradingsymbol']
        globalvar.g_instrument_dict[tradingsymbol]['token'] = instrument['instrument_token']
        globalvar.g_instrument_dict[tradingsymbol]['underlying'] = instrument['name']
    '''
    
    for instrument in instruments:
        if instrument['tradingsymbol'] == symbol:
            tradingsymbol = instrument['tradingsymbol']
            if tradingsymbol not in globalvar.g_instrument_dict.keys():
                globalvar.g_instrument_dict[tradingsymbol] = {}
            for k, v in instrument.items():
                globalvar.g_instrument_dict[tradingsymbol][k] = v
            globalvar.g_instrument_dict[tradingsymbol]['token'] = instrument['instrument_token']
            globalvar.g_instrument_dict[tradingsymbol]['underlying'] = instrument['name']
            return instrument
    return None



def get_nse_instrument(kite, symbol, param):
    #instruments = kite.instruments("NFO")
    #{'instrument_token': 245249, 'exchange_token': '958', 'tradingsymbol': 'ESCORTS', 
    #'name': 'ESCORTS KUBOTA', 'last_price': 0.0, 'expiry': '', 'strike': 0.0, '
    #tick_size': 0.05, 'lot_size': 1, 'instrument_type': 'EQ', 'segment': 'NSE', 'exchange': 'NSE'}
    try:
        if symbol in globalvar.g_instrument_dict.keys():
            if 'token' in globalvar.g_instrument_dict[symbol].keys():
                instrument = globalvar.g_instrument_dict[symbol]
                return instrument
    except:
        pass
        
    if param['index_exchange']=="NSE":instruments = kite.instruments("NSE")
    elif param['index_exchange']=="BSE":instruments = kite.instruments("BSE")
    #print(type(instruments))

    '''
    for instrument in instruments:
        tradingsymbol = instrument['tradingsymbol']
        if tradingsymbol not in globalvar.g_instrument_dict.keys():
            globalvar.g_instrument_dict[tradingsymbol] = {}
        for k, v in instrument.items():
            globalvar.g_instrument_dict[tradingsymbol][k] = v
        globalvar.g_instrument_dict[tradingsymbol]['token'] = instrument['instrument_token']
        globalvar.g_instrument_dict[tradingsymbol]['underlying'] = instrument['name']
    '''    
        
    
    for instrument in instruments:
        #if "NIFTY" in instrument['tradingsymbol']:
        #    print(instrument)
        if instrument['tradingsymbol'] == symbol:
            #print(instrument)
            tradingsymbol = instrument['tradingsymbol']
            if tradingsymbol not in globalvar.g_instrument_dict.keys():
                globalvar.g_instrument_dict[tradingsymbol] = {}
            for k, v in instrument.items():
                globalvar.g_instrument_dict[tradingsymbol][k] = v
            globalvar.g_instrument_dict[tradingsymbol]['token'] = instrument['instrument_token']
            globalvar.g_instrument_dict[tradingsymbol]['underlying'] = instrument['name']
            return instrument
    return None





def next_thursday(date, wi):
    days_ahead = wi - date.weekday()  # Thursday is represented by 3
    if days_ahead < 0:  # Target day already passed this week
        days_ahead += 7
    return date + datetime.timedelta(days=days_ahead)


def next_to_next_thursday(date, wi):
    days_ahead = wi - date.weekday()  # 3 corresponds to Thursday
    if days_ahead < 0:  # Target day already passed this week
        days_ahead += 7
    next_thursday = date + datetime.timedelta(days=days_ahead)
    next_to_next_thursday = next_thursday + datetime.timedelta(days=7)
    return next_to_next_thursday

def is_last_thursday(date, wi):
    # Find the last day of the month
    next_month = date.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    last_day_of_month = next_month - datetime.timedelta(days=next_month.day)
    
    # Find the last Thursday of the month
    last_thursday = last_day_of_month
    while last_thursday.weekday() != wi:  # 3 corresponds to Thursday
        last_thursday -= datetime.timedelta(days=1)
    
    return date == last_thursday

def get_month_abbreviation(date):
    return date.strftime('%b').upper()

    
def get_nifty_atm_option(kite):
    #kite = globalvar.g_kite
    #nifty_ltp = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
    #print(nifty_ltp)
    inx = param['index_symbol_ltp']
    nifty_ltp = kite.ltp(inx)[inx]["last_price"]
    print(nifty_ltp)
    sofs = int(param["strike_interval"])
    atm_strike = round(nifty_ltp / sofs) * sofs
    print(atm_strike)
    today = datetime.date.today()
    next_thursday_date = next_thursday(today)
    expy = str(next_thursday_date).replace('-0','')
    expy = expy.replace('-','')
    expy = expy[2:]
    print(expy)
    #expiry_date = "24919"
    option_symbol = f"NIFTY{expy}{atm_strike}CE"
    print(option_symbol)
    return option_symbol



def get_nifty_atm_strike(kite,param):
    #kite = globalvar.g_kite
    #nifty_ltp = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
    inx = param['index_symbol_ltp']
    nifty_ltp = kite.ltp(inx)[inx]["last_price"]
    #print(nifty_ltp)
    sofs = int(param["strike_interval"])
    print(nifty_ltp)
    atm_strike = round(nifty_ltp / sofs) * sofs
    return atm_strike


'''
def check_strike_filter(index, symbol, param):
    #nifty_ltp = globalvar.g_kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
    try:
        ltp = globalvar.g_market_dict["INDEX"][param["instrument_index_list"][0]]["1min"][index]['close']
    except:
        kite = globalvar.g_kite
        ltp = get_nifty_atm_strike(kite,param)
'''
def check_strike_filter(close, symbol, param):
    ltp = close
    sofs = int(param["strike_interval"])
    atm_strike = (round(ltp / sofs) * sofs)
    #print(ltp, atm_strike)
    sgn = 1 if "CE" in symbol else -1
    #atm_strike_str = str(round(nifty_ltp / 50) * 50)
    strike_filter=False
    if (param["strike"] == "ATM") and (str(atm_strike) in symbol):
        strike_filter=True
    if (param["strike"] == "ITM1"):
        if (str(atm_strike-sgn*param["strike_interval"]) in symbol):
            strike_filter=True
    if (param["strike"] == "ITM2"):
        if (str(atm_strike-2*sgn*param["strike_interval"]) in symbol):
            strike_filter=True
    if (param["strike"] == "ITM3"):
        if (str(atm_strike-3*sgn*param["strike_interval"]) in symbol):
            strike_filter=True
    if (param["strike"] == "ITM4"):
        if (str(atm_strike-4*sgn*param["strike_interval"]) in symbol):
            strike_filter=True
    if (param["strike"] == "OTM1"):
        if (str(atm_strike+sgn*param["strike_interval"]) in symbol):
            strike_filter=True
    if (param["strike"] == "OTM2"):
        if (str(atm_strike+2*sgn*param["strike_interval"]) in symbol):
            strike_filter=True
    if (param["strike"] == "OTM3"):
        if (str(atm_strike+3*sgn*param["strike_interval"]) in symbol):
            strike_filter=True
    if (param["strike"] == "OTM4"):
        if (str(atm_strike+4*sgn*param["strike_interval"]) in symbol):
            strike_filter=True
    return strike_filter



def get_nifty_option_list(kite, param):
    #kite = globalvar.g_kite
    #nifty_ltp = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
    inx = param['index_symbol_ltp']
    nifty_ltp = kite.ltp(inx)[inx]["last_price"]
    print(nifty_ltp)
    sofs = int(param["strike_interval"])
    atm_strike = round(nifty_ltp / sofs) * sofs
    print(atm_strike)

    
    strike_list = []
    
    
    '''
    if param['strike'] == "ATM":
        strike = atm_strike
        strike_list.append(strike)
    elif param['strike'] == "ITM1":
        strike = atm_strike-sofs
        strike_list.append(strike)
    elif param['strike'] == "ITM2":
        strike = atm_strike-2*sofs
        strike_list.append(strike)
    elif param['strike'] == "ITM3":
        strike = atm_strike-3*sofs
        strike_list.append(strike)
    elif param['strike'] == "ITM4":
        strike = atm_strike-4*sofs
        strike_list.append(strike)
    elif param['strike'] == "OTM1":
        strike = atm_strike+sofs
        strike_list.append(strike)
    elif param['strike'] == "OTM2":
        strike = atm_strike+2*sofs
        strike_list.append(strike)
    elif param['strike'] == "OTM3":
        strike = atm_strike+3*sofs
        strike_list.append(strike)
    elif param['strike'] == "OTM4":
        strike = atm_strike+4*sofs
        strike_list.append(strike)
    '''

    optc = int(10)
    for i in range(-optc,optc,1):
        strike = atm_strike+i*sofs
        strike_list.append(strike)
    
    print(strike_list)
    
    
    today = datetime.date.today()
    timenow = datetime.datetime.now()
    wi = globalvar.week_code[param['option_expiry']]
    # Calculate the first day of the next month 
    if today.month == 12:
        next_month_first_day = datetime.date(today.year + 1, 1, 1)
    else:
        next_month_first_day = datetime.date(today.year, today.month + 1, 1)
    # Calculate the first day of the next to next month 
    if today.month == 12:
        next_to_next_month_first_day = datetime.date(today.year + 1, 2, 1)
    elif today.month == 11:
        next_to_next_month_first_day = datetime.date(today.year + 1, 1, 1)
    else:
        next_to_next_month_first_day = datetime.date(today.year, today.month + 2, 1)
    
    if param['expiry_frequency']=='Month':
        dulw,days_remaining = techlib.days_until_last_weekday(timenow, wi)
        if param['expiry_month']=='CurrentMonth':
            if dulw>timenow:
                mon = get_month_abbreviation(today)
            else:
                mon = get_month_abbreviation(next_month_first_day)
        else:
            if dulw>timenow:
                mon = get_month_abbreviation(next_month_first_day)
            else:
                mon = get_month_abbreviation(next_to_next_month_first_day)
        expy = str(today.year)[2:] + mon
    else:
        if param['expiry_week'] == "CurrentWeek":
            thursday_date = next_thursday(today, wi)
            if check_holiday(thursday_date)==True:
                thursday_date = thursday_date - datetime.timedelta(days=1) #next_to_next_thursday(today, wi)
        else:
            thursday_date = next_to_next_thursday(today, wi)
        last_thurs = is_last_thursday(thursday_date, wi)
        mon = get_month_abbreviation(thursday_date)
        if last_thurs:
            expy = str(thursday_date)[2:4]+mon
        elif mon=='OCT' or mon=='NOV' or mon=='DEC':
            expy = str(thursday_date)[2:4] + mon[0] + str(thursday_date)[-2:]
        else:
            expy = str(thursday_date).replace('-0','')
            expy = expy.replace('-','')
            expy = expy[2:]
    print(expy)


    #spre = "NIFTY"
    spre = param['index_symbol_option']
    #if spre=="NIFTY 50":
    #    spre="NIFTY"
    #if param['index_symbol_ltp'] == "NSE:NIFTY BANK":
    #    spre="BANKNIFTY"
        
    
    
    #expiry_date = "24919"
    option_symbol_list = []
    for strike in strike_list:
        #option_symbol = f"NIFTY{expy}{strike}CE"
        option_symbol = spre+str(expy)+str(strike)+"CE"
        option_symbol_list.append(option_symbol)
        #option_symbol = f"NIFTY{expy}{strike}PE"
        option_symbol = spre+str(expy)+str(strike)+"PE"
        option_symbol_list.append(option_symbol)
    print(option_symbol_list)
    return option_symbol_list



def get_stock_expiry(param):
    today = datetime.date.today()
    
    timenow = datetime.datetime.now()
    wi = globalvar.week_code[param['option_expiry']]

    timenow2 = timenow + datetime.timedelta(days=7)
    timenow3 = timenow + datetime.timedelta(days=37)

    #print(timenow,timenow2,timenow3)
    
    dulw,days_remaining = techlib.days_until_last_weekday(timenow, wi)
    dulw2,days_remaining2 = techlib.days_until_last_weekday(timenow2, wi)
    
    
    
    if param['expiry_month']=='CurrentMonth':
        if dulw>timenow:
            mon = dulw.strftime('%Y-%m-%d')
        else:
            mon =  dulw2.strftime('%Y-%m-%d')
    else:
        if today.month == 12:
            first_day_next_month = datetime.datetime(today.year + 1, 1, 1, 9, 15, 0) 
        else: 
            first_day_next_month = datetime.datetime(today.year, today.month + 1, 1, 9, 15, 0)
        #print("first_day_next_month: ",first_day_next_month)
        
        dulw3, days_remaining3 = techlib.days_until_last_weekday(first_day_next_month, wi)
        first_day_next_to_next_month = first_day_next_month + datetime.timedelta(days=31)
        dulw4, days_remaining4 = techlib.days_until_last_weekday(first_day_next_to_next_month, wi)
        if dulw>timenow:
            mon = dulw3.strftime('%Y-%m-%d')
        else:
            mon = dulw4.strftime('%Y-%m-%d')
            
    #print("mon: ",mon)
    return mon




def get_nse_instrument_token_dict(kite, symbol_list, param):
    #instruments = kite.instruments("NSE")
    if param['index_exchange']=="NSE":instruments = kite.instruments("NSE")
    elif param['index_exchange']=="BSE":instruments = kite.instruments("BSE")
    #print(type(instruments))
    instrument_token_dict = {}
    for symbol in symbol_list:
        for instrument in instruments:
            #if "NIFTY" in instrument['tradingsymbol']:
            #    print(instrument)
            if instrument['tradingsymbol'] == symbol:
                #print(instrument)
                instrument_token_dict[symbol] = instrument['instrument_token']
    return instrument_token_dict



def get_nfo_instrument_token_dict(kite, symbol_list, param):
    #instruments = kite.instruments("NFO")
    if param['index_exchange']=="NSE":instruments = kite.instruments("NFO")
    elif param['index_exchange']=="BSE":instruments = kite.instruments("BFO")
    #print(type(instruments))
    instrument_token_dict = {}
    for symbol in symbol_list:
        for instrument in instruments:
            #if "NIFTY" in instrument['tradingsymbol']:
            #    print(instrument)
            if instrument['tradingsymbol'] == symbol:
                #print(instrument)
                instrument_token_dict[symbol] = instrument['instrument_token']
    return instrument_token_dict



def get_backdata_index_zerodha(kite, index, param, timeframe):
    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']

    #kite = globalvar.g_kite
    #param['instrument_symbol_list'] = []
    #param['instrument_token_dict'] = instrument_token_dict

    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']

    try:
        default_backtest = backtest_date1==None or backtest_date2==None
    except:
        default_backtest = True
        
    if param['live_trading'] or default_backtest: 
        now = datetime.datetime.now()
        if timeframe=='day':
            bd = pd.tseries.offsets.BusinessDay(10)
        else:
            bd = pd.tseries.offsets.BusinessDay(5)
        
        yesterday=now-bd#BDay(10)
    
        to_date=now.strftime("%Y-%m-%d")
        from_date=yesterday.strftime("%Y-%m-%d")
        print(from_date, to_date)
    else:
        to_date=backtest_date2.strftime("%Y-%m-%d")
        from_date=backtest_date1.strftime("%Y-%m-%d")
        print(from_date, to_date)
        
    
    interval="minute"
    historyData_dict = {}


    index_symbol_list = [index]
    instrument_token_list = []
    for index_symbol in index_symbol_list:
        #print(index_symbol)
        instrument_token = get_nse_instrument_token(kite, index_symbol, param)
        print(instrument_token)
        instrument_token_list.append(instrument_token)
        #hdict = kite.historical_data(instrument_token,from_date,to_date,interval)
        if timeframe=='1min':
            hdict = kite.historical_data(instrument_token,from_date,to_date,'minute')
            #print(hdict)
        else:
            #print(instrument_token,from_date,to_date)
            hdict = kite.historical_data(instrument_token,from_date,to_date,'day')
            #print(hdict)
        dfh=None
        dfh = pd.DataFrame(hdict)
        #print(timeframe)
        #print(dfh)
        #print(index_symbol)
        if param['show_detail_log']: print(dfh.head(1))
        if param['show_detail_log']: print(dfh.tail(1))
        
        if 'date' not in dfh.columns:
            dfh['date'] = pd.to_datetime(dfh['ts'])
        
        #dfh.rename(columns={'date': 'datetime'}, inplace=True)
        dfh['datetime'] = dfh['date'].apply(lambda x: x.replace(tzinfo=None))
        '''
        dfh.set_index('datetime', inplace=True, drop=False)
        print(dfh.head(1))
        print(dfh.tail(1))
        #dfh['index'] = dfh['datetime']
        dfh = dfh.resample(timeframe).agg({'open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'}).dropna()
        dfh.reset.index()
        '''
        
        if param['show_detail_log']: print(dfh.head(1))
        if param['show_detail_log']: print(dfh.tail(1))
        dfh.to_csv(DATAPATH+index_symbol+timeframe+'.csv')
        historyData_dict[index_symbol] = dfh.to_dict('records')
    return historyData_dict
    


def get_backdata_zerodha(param, mtfcandles_dict):
    instrument_symbol_list = param['instrument_symbol_list']
    #timeframe = param['timeframe']
    #frequency = param['frequency']
    #extended_hours = param['extended_hours']
    #periodType = param['periodType']
    #period = param['period']
    
    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']


    #holdings = globalvar.g_kite.holdings()
    #for item in holdings:
    #    print(item['tradingsymbol'], item['quantity'])

    
    #if backtest_date1==None:
    #    print("provide backtest date")
    #    return None
    if param['datasource']=='zerodha':
        kite = globalvar.g_kite
    elif param['datasource']=='finvasia':
        kite = globalvar.g_shoonya
    
    #option_symbol = get_nifty_atm_option(kite)
    #instrument_token = get_nfo_instrument_token(kite, option_symbol)
    #print(instrument_token)
    param['instrument_symbol_list'] = []
    
    #globalvar.g_market_dict = {"INDEX":{}, "EQUITY":{}, "OPTION":{},"FUTURES":{},"FOREX":{}}
    market_dict = globalvar.g_market_dict

    atr_timeframe = str(param["index_atr_timeframe_hour"])+"H"
    indices_symbol_list=[]
    indices_atr_symbol_list=[]
    for indices in param['instrument_index_list']:
        market_dict["INDEX"][indices] = {}
        market_dict["INDEX"][indices][atr_timeframe] = get_backdata_index_zerodha(kite, indices, param, atr_timeframe)[indices]
        indices_atr_symbol_list.append(indices+atr_timeframe)
        market_dict["INDEX"][indices]["1min"] = get_backdata_index_zerodha(kite, indices, param, '1min')[indices]
        indices_symbol_list.append(indices)
    
    option_symbol_list = get_nifty_option_list(kite,param)
    param['option_symbol_list'] =  option_symbol_list

    ins_list =  indices_symbol_list+option_symbol_list
    param['instrument_symbol_list'] =  indices_symbol_list+option_symbol_list
    
    param['instrument_token_dict'] = {}
    #param['instrument_token_dict'][option_symbol] = instrument_token 
    indices_token_dict = get_nse_instrument_token_dict(kite, indices_symbol_list, param)
    option_token_dict = get_nfo_instrument_token_dict(kite, option_symbol_list, param)
    
    
    ins_token_dict = {**indices_token_dict, **option_token_dict}
    param['instrument_token_dict'] = ins_token_dict

    '''
    now = datetime.datetime.now()
    bd = pd.tseries.offsets.BusinessDay(5)
    yesterday=now-bd#BDay(10)

    to_date=now.strftime("%Y-%m-%d")
    from_date=yesterday.strftime("%Y-%m-%d")
    print(from_date, to_date)
    '''
    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']

    try:
        default_backtest = backtest_date1==None or backtest_date2==None
    except:
        default_backtest = True
        
    if param['live_trading'] or default_backtest: 
        now = datetime.datetime.now()
        bd = pd.tseries.offsets.BusinessDay(5)
        yesterday=now-bd#BDay(10)
    
        to_date=now.strftime("%Y-%m-%d")
        from_date=yesterday.strftime("%Y-%m-%d")
        print(from_date, to_date)
    else:
        to_date=backtest_date2.strftime("%Y-%m-%d")
        from_date=backtest_date1.strftime("%Y-%m-%d")
        print(from_date, to_date)
    
    interval="minute"

    historyData_dict = {}
    
    
    print("in history:instrument_symbol_list:",ins_list)
    f = open(DATAPATH+"localtest.txt",'w')
    f.write(str(ins_list))
    f.close()


    fetch_threadpool(option_symbol_list, ins_token_dict, from_date,to_date,interval, kite, param, historyData_dict)
    #for option_symbol in option_symbol_list:
    #    fetch_d(option_symbol, ins_token_dict, from_date,to_date,interval, kite, param, historyData_dict)
    
    
    #for ix in globalvar.g_market_dict["INDEX"].keys():
    for ix in param['instrument_index_list']:
        historyData_dict[ix] = globalvar.g_market_dict["INDEX"][ix]["1min"]


    av_ins = list(historyData_dict.keys())
    option_symbol_list = param['option_symbol_list']
    option_symbol_list_orig = option_symbol_list.copy()
    for opt in option_symbol_list_orig:
        if opt not in av_ins:
            option_symbol_list.remove(opt)
        elif len(historyData_dict[opt])<100:
            option_symbol_list.remove(opt)
    
    for opt in option_symbol_list:
        print('optlen:',opt, len(historyData_dict[opt]))
            
    param['option_symbol_list'] =  option_symbol_list
    param['instrument_symbol_list'] =  indices_symbol_list+option_symbol_list
    
    return historyData_dict



def fetch_threadpool(option_symbol_list, ins_token_dict, from_date,to_date,interval, kite, param, historyData_dict):
    print("fc1", datetime.datetime.now())
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = [executor.submit(fetch_d, option_symbol, ins_token_dict, from_date,to_date, interval, 
                                   kite, param, historyData_dict) for option_symbol in option_symbol_list]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    print("fc2", datetime.datetime.now())



def fetch_d(symbol, ins_token_dict, from_date,to_date,interval, kite, param, historyData_dict):
    #historyData_dict={}
    #for option_symbol in option_symbol_list:
    try:
        instrument_token = globalvar.g_instrument_dict[symbol]['token']
    except:
        instrument_token = ins_token_dict[symbol]
    
    
    try:
        hdict = kite.historical_data(instrument_token,from_date,to_date,interval)
    except Exception as e:
        print(symbol, e)
        return None
    
    if hdict is None: return None
    
    
    dfh=None
    dfh = pd.DataFrame(hdict)
    print("fetch: ", symbol, len(dfh))
    #print(dfh)

    # clearning up zero for backfill
    dfh = dfh.replace(0, np.nan)

    dfh = dfh.ffill(axis=0)  
    dfh = dfh.bfill(axis=0)

    has_nan = dfh['close'].isnull().values.any()
    if has_nan: return None
    
    if param['show_detail_log']: print(dfh.head(1))
    if param['show_detail_log']: print(dfh.tail(1))
    #print(dfh.head(2))
    #print(dfh.tail(2))
    
    if 'date' not in dfh.columns:
        dfh['date'] = pd.to_datetime(dfh['ts'])
    
    #dfh.rename(columns={'date': 'datetime'}, inplace=True)
    dfh['datetime'] = dfh['date'].apply(lambda x: x.replace(tzinfo=None))
    
    dfh.to_csv(DATAPATH+symbol+'.csv')
    historyData_dict[symbol] = dfh.to_dict('records')
    #historyData_dict[] = 
    return historyData_dict[symbol]




def get_backdata_symbol(symbol, candles_dict, param, interval="minute", numDays=5, instrument_type="OPT"):
    #instrument_symbol_list = param['instrument_symbol_list']
    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']
    if param['live_trading']: 
        now = datetime.datetime.now()
        bd = pd.tseries.offsets.BusinessDay(numDays)
        yesterday=now-bd
    
        to_date=now.strftime("%Y-%m-%d")
        from_date=yesterday.strftime("%Y-%m-%d")
        #print(from_date, to_date)
    else:
        to_date=backtest_date2.strftime("%Y-%m-%d")
        from_date=backtest_date1.strftime("%Y-%m-%d")
        #print(from_date, to_date)
    
    #interval="minute"
    #interval = 

    kite = globalvar.g_kite

    #ins_token_dict = param['token_dict']
    if instrument_type=="EQ":
        instrument = get_nse_instrument(kite, symbol, param)
    else:
        instrument = get_nfo_instrument(kite, symbol, param)
    
    #print("instrument->",instrument)
    
    ins_token = instrument['instrument_token']    
    name = instrument['name']
    #print(symbol, ins_token)
    if symbol not in globalvar.g_instrument_dict.keys():
        globalvar.g_instrument_dict[symbol] = {}
        globalvar.g_instrument_dict[symbol]['token'] = ins_token
        globalvar.g_instrument_dict[symbol]['underlying'] = name
    else:
        globalvar.g_instrument_dict[symbol]['token'] = ins_token
        globalvar.g_instrument_dict[symbol]['underlying'] = name

    #print(globalvar.g_instrument_dict)
    ins_token_dict = {}
    #ins_token_dict[symbol] = ins_token
    candles = fetch_d(symbol, ins_token_dict, from_date, to_date, interval, kite, param, candles_dict)
    return candles







def get_backdata_finvasia(param, mtfcandles_dict):
    instrument_symbol_list = param['instrument_symbol_list']    
    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']
    
    kite = globalvar.g_shoonya
    
    param['instrument_symbol_list'] = []
    
    #globalvar.g_market_dict = {"INDEX":{}, "EQUITY":{}, "OPTION":{},"FUTURES":{},"FOREX":{}}
    market_dict = globalvar.g_market_dict

    atr_timeframe = str(param["index_atr_timeframe_hour"])+"H"
    indices_symbol_list=[]
    indices_atr_symbol_list=[]
    for indices in param['instrument_index_list']:
        market_dict["INDEX"][indices] = {}
        market_dict["INDEX"][indices][atr_timeframe] = get_backdata_index_zerodha(indices, param, atr_timeframe)[indices]
        indices_atr_symbol_list.append(indices+atr_timeframe)
        market_dict["INDEX"][indices]["1min"] = get_backdata_index_zerodha(indices, param, '1min')[indices]
        indices_symbol_list.append(indices)
    
    option_symbol_list = get_nifty_option_list(kite,param)
    param['option_symbol_list'] =  option_symbol_list

    ins_list =  indices_symbol_list+option_symbol_list
    param['instrument_symbol_list'] =  indices_symbol_list+option_symbol_list
    
    param['instrument_token_dict'] = {}
    #param['instrument_token_dict'][option_symbol] = instrument_token 
    indices_token_dict = get_nse_instrument_token_dict(kite, indices_symbol_list, param)
    option_token_dict = get_nfo_instrument_token_dict(kite, option_symbol_list, param)
    
    
    ins_token_dict = {**indices_token_dict, **option_token_dict}
    param['instrument_token_dict'] = ins_token_dict

    '''
    now = datetime.datetime.now()
    bd = pd.tseries.offsets.BusinessDay(5)
    yesterday=now-bd#BDay(10)

    to_date=now.strftime("%Y-%m-%d")
    from_date=yesterday.strftime("%Y-%m-%d")
    print(from_date, to_date)
    '''
    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']

    try:
        default_backtest = backtest_date1==None or backtest_date2==None
    except:
        default_backtest = True
        
    if param['live_trading'] or default_backtest: 
        now = datetime.datetime.now()
        bd = pd.tseries.offsets.BusinessDay(5)
        yesterday=now-bd#BDay(10)
    
        to_date=now.strftime("%Y-%m-%d")
        from_date=yesterday.strftime("%Y-%m-%d")
        print(from_date, to_date)
    else:
        to_date=backtest_date2.strftime("%Y-%m-%d")
        from_date=backtest_date1.strftime("%Y-%m-%d")
        print(from_date, to_date)
        
    interval="minute"

    historyData_dict = {}
    
    
    print("in history:instrument_symbol_list:",ins_list)
    f = open(DATAPATH+"localtest.txt",'w')
    f.write(str(ins_list))
    f.close()

    fetch_threadpool(option_symbol_list, ins_token_dict, from_date,to_date,interval, kite, param, historyData_dict)
    
    for ix in globalvar.g_market_dict["INDEX"].keys():
        historyData_dict[ix] = globalvar.g_market_dict["INDEX"][ix]["1min"]
        
    return historyData_dict






def get_backdata_fyers(param, mtfcandles_dict):
    instrument_symbol_list = param['instrument_symbol_list']
    timeframe = param['timeframe']
    frequency = param['frequency']
    extended_hours = param['extended_hours']
    periodType = param['periodType']
    period = param['period']
    
    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']
    
    if backtest_date1==None:
        print("provide backtest date")
        return None
    
    #period = "5d", interval = "5m"
    historyData_dict = {}
    return historyData_dict
    
    





def df_multiframe(df, param, symbol):
    instrument_symbol_list = param['instrument_symbol_list']
    timeframe = param['timeframe']
    frequency = param['frequency']
    extended_hours = param['extended_hours']
    periodType = param['periodType']
    period = param['period']
    backtest_date1 = param['backtest_date1']
    backtest_date2 = param['backtest_date2']
    sctf = int(param['stoploss_secondary_timeframe'])
    allow_unauthenticated_requests = param['allow_unauthenticated_requests']
    
    dflist = []
    
    if frequency!='1':
        fq = int(frequency)
        for j in range(len(df)):
                i=1+j#int((df['datetime'][j] - df['datetime'][0]).seconds/60)

                if i%fq==1: df.loc[j,'open'] = df.loc[j,'open']
                else: df.loc[j,'open'] = df.loc[j-1,'open']

                df.loc[j,'close'] = df.loc[j,'close']    
                #if i%2==0 or i==1: df.loc[j,'close2min'] = df.loc[j,'close']
                #else: df.loc[j,'close2min'] = df.loc[j-1,'close2min']    

                if i%fq==1: df.loc[j,'low'] = df.loc[j,'low']    
                else: df.loc[j,'low'] = min(df.loc[j,'low'], df.loc[j-1,'low'])

                if i%fq==1: df.loc[j,'high'] = df.loc[j,'high']    
                else: df.loc[j,'high'] = max(df.loc[j,'high'], df.loc[j-1,'high'])
        rs = frequency+'T'
        df = df.resample(rs,on='datetime',origin='start').last()
        df = df.drop('datetime',axis=1)
        df =df.dropna(how='any')
        df = df.reset_index()
    
    
    
    #print(df.head(10))
    #print(df.tail(10))
    #print(df['datetime'])
    
    if param['multitimeframe']:
        dff = df.copy()
        dff.index = dff['datetime']
        
        #print(dff.head(20))
        
        dff2min = dff.resample('2T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        dff3min = dff.resample('3T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        dff4min = dff.resample('4T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        dff5min = dff.resample('5T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        dff10min = dff.resample('10T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        dff15min = dff.resample('15T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        dff20min = dff.resample('20T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        dff30min = dff.resample('30T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        dff60min = dff.resample('60T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
        
        
        dff2min = dff2min.dropna()
        dff3min = dff3min.dropna()
        dff4min = dff4min.dropna()
        dff5min = dff5min.dropna()
        dff10min = dff10min.dropna()
        dff15min = dff15min.dropna()
        dff20min = dff20min.dropna()
        dff30min = dff30min.dropna()
        dff60min = dff60min.dropna()
        
        
        #dff2min.to_csv('./data/test2min.csv')
        #dff5min.to_csv('./data/test5min.csv')
        #dff15min.to_csv('./data/test15min.csv')
        #dff20min.to_csv('./data/test20min.csv')
        
        dflist.append(dff2min)
        dflist.append(dff3min)
        dflist.append(dff4min)
        dflist.append(dff5min)
        dflist.append(dff10min)
        dflist.append(dff15min)
        dflist.append(dff20min)
        dflist.append(dff30min)
        dflist.append(dff60min)
        
        
        dt = dff.index.to_list()
        
        # 2min
        idx = dff2min.index[dff2min.index.get_indexer(dt, method='pad')]
        dff['datetime2min'] = idx
        dff['index2min'] = 0
        dff.index2min = dff.datetime2min.ne(dff.datetime2min.shift()).cumsum() - 1
        
        
        #3 min
        idx = dff3min.index[dff3min.index.get_indexer(dt, method='pad')]
        dff['datetime3min'] = idx
        dff['index3min'] = 0
        dff.index3min = dff.datetime3min.ne(dff.datetime3min.shift()).cumsum() - 1
        
        
        # 4 min
        idx = dff4min.index[dff4min.index.get_indexer(dt, method='pad')]
        dff['datetime4min'] = idx
        dff['index4min'] = 0
        dff.index4min = dff.datetime4min.ne(dff.datetime4min.shift()).cumsum() - 1
        
        
        # 5 min
        idx = dff5min.index[dff5min.index.get_indexer(dt, method='pad')]
        dff['datetime5min'] = idx
        dff['index5min'] = 0
        dff.index5min = dff.datetime5min.ne(dff.datetime5min.shift()).cumsum() - 1
        
        
        # 10 min
        idx = dff10min.index[dff10min.index.get_indexer(dt, method='pad')]
        dff['datetime10min'] = idx
        dff['index10min'] = 0
        dff.index10min = dff.datetime10min.ne(dff.datetime10min.shift()).cumsum() - 1
        
        
        # 15 min
        idx = dff15min.index[dff15min.index.get_indexer(dt, method='pad')]
        dff['datetime15min'] = idx
        dff['index15min'] = 0
        dff.index15min = dff.datetime15min.ne(dff.datetime15min.shift()).cumsum() - 1
        
        
        # 20 min
        idx = dff20min.index[dff20min.index.get_indexer(dt, method='pad')]
        dff['datetime20min'] = idx
        dff['index20min'] = 0
        dff.index20min = dff.datetime20min.ne(dff.datetime20min.shift()).cumsum() - 1
        
        
        # 30 min
        idx = dff30min.index[dff30min.index.get_indexer(dt, method='pad')]
        dff['datetime30min'] = idx
        dff['index30min'] = 0
        dff.index30min = dff.datetime30min.ne(dff.datetime30min.shift()).cumsum() - 1
        
        
        # 60 min
        idx = dff60min.index[dff60min.index.get_indexer(dt, method='pad')]
        dff['datetime60min'] = idx
        dff['index60min'] = 0
        dff.index60min = dff.datetime60min.ne(dff.datetime60min.shift()).cumsum() - 1
        
        #dff.to_csv('./data/test1min.csv')
        
        
    '''    
    try:
        filenm = './data/'+symbol+'_PRE.csv'
        dff.to_csv(filenm)
    except:
        print("imported data file write failed")
    '''        
    return dff, dflist






def update_candles(new_now=None, hisD=None, candles=None, append=False, useoffset=False):        
    now_ = new_now
    tz = pytz.timezone('US/Eastern')
    now=now_.astimezone(tz)
    
    minute=now.minute
    
    last_date = hisD[-1]['datetime']
    
    #print(last_date,  type(last_date))
    
    last_date_minute = last_date.minute
    
    #print(now, last_date)
    #print(minute, last_date_minute)
    
    offset=1
    
    #if useoffset and minute==last_date_minute:
    #    offset=2
    
    #global g_tick
    #if append is True:
    
    c = hisD[-offset]
    
    #print(hisD[-1]['datetime'])
    
    #else:
    # c=hisD[-1]
    dtnow = hisD[-1]['datetime']
    dtnow = dtnow.replace(year=now.year)
    dtnow = dtnow.replace(month=now.month)
    dtnow = dtnow.replace(day=now.day)
    dtnow = dtnow.replace(hour=now.hour)
    dtnow = dtnow.replace(minute=now.minute)
    
    #print(dtnow)
    
    if append is True:
        dt = dtnow
    else:
        dt = candles[-1]['datetime']
    
    #print(c)
    
    new_data = {'datetime': dt,
     'open': c['open'],
     'high': c['high'],
     'low': c['low'],
     'close': c['close'],
     'totalvolumeday': c['volume']}

    #print(new_data)

    #print(str(new_data['date']))

    new_candle = candles[-1].copy()
    
    if append is True:
        new_candle = create_candle()
    else:
        new_candle = candles[-1].copy()
        
    new_candle['datetime'] = new_data['datetime']
    new_candle['open'] = new_data['open']
    new_candle['high'] = new_data['high']
    new_candle['low'] = new_data['low']
    new_candle['close'] = new_data['close']
    new_candle['totalvolumeday'] = new_data['totalvolumeday']
    
    
    #print(new_candle)
    candle_exist  = candles[-1]['datetime'].minute==new_candle['datetime'].minute
    
    if append is True and (not candle_exist):
        candles.append(new_candle)
    else:
        candles[-1] = new_candle
    
    newbar = minute==last_date_minute
    
    #index_ = len(candles)-1
    candles[-1]['volume'] = new_data['totalvolumeday'] - candles[-2]['totalvolumeday']
    
    '''
    #------------5min candle-------------------------------------
    if candles[-1]['datetime'].minute%5==0:
        candles[-1]['open5min'] =  candles[-1]['open']
        candles[-1]['high5min'] =  candles[-1]['high']
        candles[-1]['low5min'] =  candles[-1]['low']
        candles[-1]['close5min'] =  candles[-1]['close']
    else:
        candles[-1]['open5min'] =  candles[-2]['open5min']
        candles[-1]['high5min'] =  max(candles[-1]['high'], candles[-2]['high5min'])
        candles[-1]['low5min'] =  min(candles[-1]['low'], candles[-2]['low5min'])
        candles[-1]['close5min'] =  candles[-1]['close']
    
    
    
    #------------------10min candle---------------------------------
    if candles[-1]['datetime'].minute%10==0:
        candles[-1]['open10min'] =  candles[-1]['open']
        candles[-1]['high10min'] =  candles[-1]['high']
        candles[-1]['low10min'] =  candles[-1]['low']
        candles[-1]['close10min'] =  candles[-1]['close']
    else:
        candles[-1]['open10min'] =  candles[-2]['open10min']
        candles[-1]['high10min'] =  max(candles[-1]['high'], candles[-2]['high10min'])
        candles[-1]['low10min'] =  min(candles[-1]['low'], candles[-2]['low10min'])
        candles[-1]['close10min'] =  candles[-1]['close']
    '''
    
    # consolidate old candle
    #if append is True:
    #    old_i = 2 if newbar else 1
    #    candles[-2]['open'] = hisD[-old_i]['open']
    #    candles[-2]['high'] = hisD[-old_i]['high']
    #    candles[-2]['low'] = hisD[-old_i]['low']
    #    candles[-2]['close'] = hisD[-old_i]['close']
    #    candles[-2]['volume'] = hisD[-old_i]['volume']
    
    
    return candles, newbar


def get_fno_stocks(param):
    instrumentList = pd.read_csv("https://api.kite.trade/instruments")
    param['instrumentDataFrame'] = instrumentList
    fno_stocks = list(set(instrumentList[instrumentList['segment'] == 'NFO-FUT']["name"].to_list()))
    equity = instrumentList[instrumentList['segment'] == 'NSE']
    filtered_stocks = equity[equity['tradingsymbol'].isin(fno_stocks)]
    
    #fnosymbol = list(filtered_stocks['tradingsymbol'])
    
    fno_stock_token_dict = dict(zip(filtered_stocks['tradingsymbol'], filtered_stocks['instrument_token']))
    token_dict = dict(zip(instrumentList['tradingsymbol'], instrumentList['instrument_token']))
    param['fno_stock_token_dict'] = fno_stock_token_dict 
    param['token_dict'] = token_dict
    #return instrumentList, fno_stock_token_dict, token_dict
    fno_stock_list = list(fno_stock_token_dict.keys())
    #globalvar.g_param = param
    return fno_stock_list


def get_fno_stock_option(name='IDEA', optiontype='CE', expiry='2024-12-26', param=None):
    #iL = pd.read_csv("https://api.kite.trade/instruments")
    #print(name, optiontype, expiry)
    iL = param['instrumentDataFrame']
    
    #print(iL[(iL['segment']=='NFO-OPT')])

    #print(iL[(iL['name']==name)])
    
    iLf = iL[(iL['segment']=='NFO-OPT') & (iL['instrument_type']==optiontype) & (iL['name']==name) & (iL['expiry']==expiry)]
    iLf = iLf.sort_values(by='strike', ascending=True)
    return iLf




def get_day_price_change(param):
    kite = globalvar.g_kite
    #instrument_token_df, instrument_token_dict, token_dict = get_fno_stocks()
    instrument_token_dict = param['fno_stock_token_dict']
    
    
    instrument_token_list=[]
    for key in instrument_token_dict.keys():
        v = instrument_token_dict[key]
        instrument_token_list.append(v) 

    #print(instrument_token_list)
    data = kite.ohlc(instrument_token_list)
    #print("typedata",type(data))
    
    ltp_dict = {}
    open_dict = {}
    gain_dict = {}
    gain_list = []
    for key in instrument_token_dict.keys():
        ltp = data[str(instrument_token_dict[key])]['last_price']
        open_price = data[str(instrument_token_dict[key])]['ohlc']['open']
        ltp_dict[key] = ltp
        open_dict[key] = open_price
        gain = round(100*(ltp / open_price - 1), 2)
        gain_dict[key] = gain
        gain_price = round(ltp - open_price, 2)
        row = {"Stock":key, "Gain":gain, "Open":open_price, "Change":gain_price, "LTP":ltp} 
        gain_list.append(row)
        #print(key, ltp, open_price, gain_dict[key])
    return gain_list





def update_underlying(new_bar=False):
    #try:
    if True:
        ins_list = list(globalvar.g_underinstrument_dict.keys())
        #print(ins_list)
        instrument_token_dict = globalvar.g_param['fno_stock_token_dict']
        
        reversed_dict = {value: key for key, value in instrument_token_dict.items()}
        #print(reversed_dict)
        
        #print(instrument_token_dict)
        instrument_token_list= list(reversed_dict.keys())#[]
        #for key in ins_list:
        #    v = instrument_token_dict[key]
        #    instrument_token_list.append(v) 
        #print(instrument_token_list)
        quotes = globalvar.g_kite.quote(instrument_token_list)
        #print(quotes)
        for k,q in quotes.items():
            #print(q)
            token = q['instrument_token']
            #print(token)
            key = reversed_dict[token]
            if key not in globalvar.g_underinstrument_dict.keys():continue
            #print(key)
            if new_bar==True:
                row = {'datetime':datetime.datetime.now()}
            else:
                row = globalvar.g_underinstrument_dict[key][-1]
            
            ltp = q['last_price']
            ltq = q['last_quantity']
            row['close'] = ltp
            if new_bar==True:
                row['open'] = ltp
                
            if new_bar==True:
                row['high'] = ltp
            else:
                row['high'] = max(row['high'],ltp)
    
            if new_bar==True:
                row['low'] = ltp
            else:
                row['low'] = min(row['low'],ltp)
    
            if new_bar==True:
                row['volume'] = ltq
            else:
                row['volume'] = row['volume'] + ltq

            #print(row)
            if new_bar==True:
                globalvar.g_underinstrument_dict[key].append(row)
    #except Exception as e:
    #    print("update_underlying error",e)
    #    return
    

def get_futures_instrument(param):
    kite = globalvar.g_kite
    if 'instrumentDataFrame' in param.keys():
        instruments = param['instrumentDataFrame']
    else:
        instruments = kite.instruments()
    df = pd.DataFrame(instruments)

    # get futures token
    #globalvar.g_futures_token_dict = {}
    
    today = datetime.datetime.now().date()
    results = []

    stock_list = list(param['fno_stock_token_dict'].keys())
    for stock in stock_list:
        futures = df[(df['segment'] == 'NFO-FUT') & (df['name'] == stock)]

        if not futures.empty:
            # Convert expiry to datetime
            futures['expiry'] = pd.to_datetime(futures['expiry'])
            
            # Filter valid (non-expired) futures
            valid_futures = futures[futures['expiry'].dt.date >= today]
            
            if not valid_futures.empty:
                # Find nearest expiry
                nearest_idx = valid_futures['expiry'].idxmin()
                nearest = valid_futures.loc[nearest_idx]

                globalvar.g_futures_dict[stock] = nearest
                globalvar.g_futures_token_dict[stock] = int(nearest['instrument_token']) 
                #results.append({
                #    'Stock Name': stock_name,
                #    'Trading Symbol': nearest['tradingsymbol'],
                #    'Instrument Token': nearest['instrument_token'],
                #    'Expiry Date': nearest['expiry'].date(),
                #    'Lot Size': nearest['lot_size']  # Optional: Add lot size for reference
                #})
            else:
                globalvar.g_futures_dict[stock] = None
                globalvar.g_futures_token_dict[stock] = None 
                #results.append({
                #    'Stock Name': stock_name,
                #    'Trading Symbol': 'No valid futures',
                #    'Instrument Token': 'N/A',
                #    'Expiry Date': 'N/A',
                #    'Lot Size': 'N/A'
                #})
        else:
            globalvar.g_futures_dict[stock] = None
            globalvar.g_futures_token_dict[stock] = None
            #results.append({
            #    'Stock Name': stock_name,
            #    'Trading Symbol': 'No futures found',
            #    'Instrument Token': 'N/A',
            #    'Expiry Date': 'N/A',
            #    'Lot Size': 'N/A'
            #})
    return

def get_instrument_history(param):
    kite = globalvar.g_kite
    #instrument_token_df, instrument_token_dict, token_dict = get_fno_stocks()
    
    futures_list = list(globalvar.g_futures_token_dict.keys())
    if len(futures_list)<1:
        get_futures_instrument(param)
        param['fno_stock_token_dict'] = {}
        param['fno_stock_token_dict'] = globalvar.g_futures_token_dict

    instrument_token_dict = param['fno_stock_token_dict']
    
    #param['stocks_to_trade_list']
    inskeylist = instrument_token_dict.keys()
    inskeylist_to_remove = []
    for key in inskeylist:
        if key not in param['stocks_to_trade_list']:
            inskeylist_to_remove.append(key)
    for key in inskeylist_to_remove:
        instrument_token_dict.pop(key,None)
        
    
    #print("instrument_token_dict length:",len(instrument_token_dict.keys()))
    #print("instrument_token_dict:",instrument_token_dict)
    
    
    instrument_token_list=[]
    for key in instrument_token_dict.keys():
        v = instrument_token_dict[key]
        instrument_token_list.append(v) 


    #lastdata = kite.ohlc(instrument_token_list)
    #lastdata = kite.
    #print("lastdata")
    #print(lastdata)
    #print(instrument_token_list)
    #data = kite.ohlc(instrument_token_list)
    #print("typedata",type(data))
    bd = pd.tseries.offsets.BusinessDay(param['stock_previous_day_offset'])
    from_date = datetime.datetime.now() - bd#datetime.timedelta(days=1)
    to_date = datetime.datetime.now()

    ##def fetch_threadpool(option_symbol_list, ins_token_dict, from_date,to_date,interval, kite, param, historyData_dict)
    # Fetch 1-minute historical data for each token
    data_dict = {}
    itf = "minute" if param['scan_timeframe']=="1" else param['scan_timeframe'] + "minute"
    #print("itf:", itf)
    #for token in instrument_token_list:
    for key in instrument_token_dict.keys():
        token = instrument_token_dict[key]
        #print("token:",token)
        if key not in globalvar.g_underinstrument_dict.keys():
            #print("history")
            print(key, "  token:",token)
            data = None
            data = kite.historical_data(
                instrument_token=token,
                from_date=from_date,
                to_date=to_date,
                interval=itf
            )
            #data_dict[token] = data
            #print(data)
            for d in data:
                if 'date' in d:
                    d['datetime'] = d.pop('date')
        
            globalvar.g_underinstrument_dict[key] = data
        else:
            #print("lastdata update")
            pass
            #ld = lastdata[str(token)]
            #print("ld",ld)
            #close = ld['last_price']
            #print(close)
            #globalvar.g_instrument_dict[key][-1]['date']
            #row = {'close':close}
            #(globalvar.g_underinstrument_dict[key]).append(row)
            #print((globalvar.g_underinstrument_dict[key][-1]))
    #print(data_dict)

    df1 = None
    df2 = None
    
    #for key in instrument_token_dict.keys():
    #    data = globalvar.g_instrument_dict[key]
    #    df = pd.DataFrame(data)
    #    print(df.head())

    for key in globalvar.g_underinstrument_dict.keys():
        token = instrument_token_dict[key]
        candles = globalvar.g_underinstrument_dict[key]
        #df = pd.DataFrame(data)
        #print(df.head())
        rsilength = param['stock_rsi_length']
        adxlength = param['stock_adx_length']
        emaperiod = param['stock_ema_period']
        vt1 = param['stock_volume_day_threshold']
        vt2 = param['stock_volume_hour_threshold']
        prt = param['stock_previous_day_offset']

        
        if 'rsi' not in candles[0].keys():
            index=0
            #if key=='360ONE':
            #    print("rsi NOT in keys", key, " : ", candles[0])
            #    if (len(candles)<10):print(candles)
            for candle in candles:
                techlib.calc_rsi(candles, index, rsilength, 'close')
                index+=1
        else:
            index = len(candles) - 1
            #if key=='360ONE':
            #    print("rsi IS in keys", key, candles[0])
            #    if (len(candles)<10):print(candles)
            techlib.calc_rsi(candles, index, rsilength, 'close', True)


        if 'adx' not in candles[0].keys():
            index=0
            for candle in candles:
                techlib.calc_adx(candles, index, adxlength)
                index+=1
        else:
            index = len(candles) - 1
            techlib.calc_adx(candles, index, adxlength)

        
        if 'ema' not in candles[0].keys():
            index=0
            for candle in candles:
                techlib.EMAKeyCandleKey(candles, index, emaperiod, 'close','ema')
                index+=1
        else:
            index = len(candles) - 1
            techlib.EMAKeyCandleKey(candles, index, emaperiod, 'close','ema')


        if 'vwapday' not in candles[0].keys():
            index=0
            for candle in candles:
                techlib.vwapday(candles, index)
                index+=1
        else:
            index = len(candles) - 1
            techlib.vwapday(candles, index)


        if 'totalvolumelastday' not in candles[0].keys():
            index=0
            for candle in candles:
                techlib.totalvolumelastday(candles, index)
                index+=1
        else:
            index = len(candles) - 1
            techlib.totalvolumelastday(candles, index)



        if 'totalvolumelasthour' not in candles[0].keys():
            index=0
            for candle in candles:
                techlib.totalvolumelasthour(candles, index)
                index+=1
        else:
            index = len(candles) - 1
            techlib.totalvolumelasthour(candles, index)

        
        if 'firstdayhigh' not in candles[0].keys():
            index=0
            for candle in candles:
                techlib.firstdayhigh(candles, index)
                index+=1
        else:
            index = len(candles) - 1
            techlib.firstdayhigh(candles, index, True)

        
        if 'firstdaylow' not in candles[0].keys():
            index=0
            for candle in candles:
                techlib.firstdaylow(candles, index)
                index+=1
        else:
            index = len(candles) - 1
            techlib.firstdaylow(candles, index, True)

    
    # scanning stocks
    
    long_stocks = []
    for key in globalvar.g_underinstrument_dict.keys():
        token = instrument_token_dict[key]
        candles = globalvar.g_underinstrument_dict[key]
        candle = candles[-1]
        ltp = candle['close']
        rsi = candle['rsi']
        ema = candle['ema']
        adx = candle['adx']
        vwapday = candle['vwapday']
        PDH = candle['firstdayhigh']

        volday = candle['averagevolumeday']
        vollastday = candle['averagevolumelastday']
        volhour = candle['averagevolumehour']
        vollasthour = candle['averagevolumelasthour']
        
        C1 = 1 if rsi>param['stock_rsi_top'] else 0
        C2 = 1 if ema<ltp else 0
        C3 = 1 if adx>param['stock_adx_threshold'] else 0
        C4 = 1 if ltp>vwapday else 0
        C5 = 1 if ltp>PDH else 0
        
        C61 = (volday)>(1+0.01*param['stock_volume_day_threshold'])*(vollastday)
        C62 = (volhour)>(1+0.01*param['stock_volume_hour_threshold'])*(vollasthour)
        C6 = 1 if (C61 or C62) else 0

        CT = C1 + C2 + C3 + C4 + C5 + C6
        CT_condition = CT >= param['stock_long_condition_count']

        
        trades_so_far = 0
        if 'trades_so_far' in param.keys():
            if key in param['trades_so_far'].keys():
                trades_so_far = param['trades_so_far'][key]
        if trades_so_far>0:
            CT_condition = CT >= param['stock_long_reentry_condition_count']
                
        
        if CT_condition:
            row = {"Stock":key, "LTP":ltp,'RSI':rsi, 'EMA':ema, 'ADX':adx, 'VWAP':vwapday, 'PDH':PDH , 'volday':volday, 'vollastday':vollastday, 'volhour':volhour, 'vollasthour':vollasthour}
            long_stocks.append(row)
    df1 = pd.DataFrame(long_stocks)


    
    short_stocks = []
    for key in globalvar.g_underinstrument_dict.keys():
        token = instrument_token_dict[key]
        candles = globalvar.g_underinstrument_dict[key]
        candles = globalvar.g_underinstrument_dict[key]
        candle = candles[-1]
        ltp = candle['close']
        rsi = candle['rsi']
        ema = candle['ema']
        adx = candle['adx']
        vwapday = candle['vwapday']
        PDL = candle['firstdaylow']

        volday = candle['averagevolumeday']
        vollastday = candle['averagevolumelastday']
        volhour = candle['averagevolumehour']
        vollasthour = candle['averagevolumelasthour']
        
        C1 = 1 if rsi<param['stock_rsi_bottom'] else 0
        C2 = 1 if ema>ltp else 0
        C3 = 1 if adx>param['stock_adx_threshold'] else 0
        C4 = 1 if ltp<vwapday else 0
        C5 = 1 if ltp<PDL else 0

        C61 = (volday)>(1+0.01*param['stock_volume_day_threshold'])*(vollastday)
        C62 = (volhour)>(1+0.01*param['stock_volume_hour_threshold'])*(vollasthour)
        C6 = 1 if (C61 or C62) else 0

        CT = C1 + C2 + C3 + C4 + C5 + C6
        CT_condition = CT >= param['stock_short_condition_count']

        
        trades_so_far = 0
        if 'trades_so_far' in param.keys():
            if key in param['trades_so_far'].keys():
                trades_so_far = param['trades_so_far'][key]
        if trades_so_far>0:
            CT_condition = CT >= param['stock_short_reentry_condition_count']
                
        
        if CT_condition:
            row = {"Stock":key, "LTP":ltp,'RSI':rsi, 'EMA':ema, 'ADX':adx, 'VWAP':vwapday, 'PDL':PDL, 'volday':volday, 'vollastday':vollastday, 'volhour':volhour, 'vollasthour':vollasthour}
            short_stocks.append(row)
    df2 = pd.DataFrame(short_stocks)
   
    #print(df1.tail())
    #print(df2.tail())
    return df1, df2
    


def find_closest_with_index(lst, target):
    closest_value = min(lst, key=lambda x: abs(x - target))
    closest_index = lst.index(closest_value)
    return closest_value, closest_index


def process_strings(string_list, optiontype='CE'):
    result = []
    T1 = ''
    T2 = ''
    if optiontype=='CE':
        T1 = 'O'
        T2 = 'I'
    else:
        T1 = 'I'
        T2 = 'O'
        
    for s in string_list:
        # Extract numbers from the string
        numbers = re.findall(r'\d+', s)
        if numbers:
            number = int(numbers[0])
            # Check for 'O' and 'I' in the string and apply the conditions
            if T1 in s:
                result.append(number)
            elif T2 in s:
                result.append(-number)
            else:
                result.append(0)
        else:
            result.append(0)
    return result

    
    

def run_scanner(param):
    #ld = get_day_price_change(param)
    df1_sorted, df2_sorted = get_instrument_history(param)
    #print(ld)
    #df = pd.DataFrame(ld)
    #df = pd.DataFrame(ld)#list(ld.items()), columns=['Stock', 'Gain'])

    # remove blacklist stocks
    stocks_to_remove=[]
    try:
        stocks_to_remove=param['selected_blacklist']
    except:
        pass
    
    
    if len(df1_sorted)>0:
        df1_sorted = df1_sorted[~df1_sorted['Stock'].isin(stocks_to_remove)]
    
        #----------------------------------gainer--------------------------------------------------------------------------
        param['scanned_stock_top_gainer'] = list(df1_sorted.head(len(df1_sorted))['Stock'])#list(df1_sorted['Stock'])
        
        max_sudden_change_stock = []
        max_sudden_change=0.0
        if param['allow_sudden_change_entry']==True:
            scem = param['sudden_change_entry_minute']
            scec = param['sudden_change_entry_count']
            for stock in list(df1_sorted['Stock']):
                if stock not in param['scanned_stock_top_gainer_close_dict'].keys():
                    param['scanned_stock_top_gainer_close_dict'][stock] = []
                price = df1_sorted.loc[df1_sorted['Stock']==stock,'LTP'].values[0]
                param['scanned_stock_top_gainer_close_dict'][stock].append(price)
                close_list = param['scanned_stock_top_gainer_close_dict'][stock]
                if len(close_list)>scem:
                    sudden_change = 100*(close_list[-1]/close_list[-4] - 1)
                    df1_sorted.loc[df1_sorted['Stock']==stock,'SuddenChange'] = round(sudden_change,2)
                    #if sudden_change>max_sudden_change:
                    #    max_sudden_change=sudden_change
                    #    max_sudden_change_stock.append(stock)
                        #if len( max_sudden_change_stock)>=scec:break
            if 'SuddenChange' in df1_sorted.columns:
                max_sudden_change_stock = list(df1_sorted.sort_values(by='SuddenChange', ascending=False).head(scec)['Stock'])
                for stock in max_sudden_change_stock:
                    if stock not in param['scanned_stock_top_gainer']:
                        param['scanned_stock_top_gainer'].append(stock)
                    
    
        
        stock_to_remove = []
        for stock in list(df1_sorted.head(len(df1_sorted))['Stock']):
            if stock not in param['scanned_stock_top_gainer_bound']:
                param['scanned_stock_top_gainer_bound'].append(stock)
        df1_sorted_bound = df1_sorted.head(len(df1_sorted))
        scanned_stock_top_gainer_bound = list(df1_sorted_bound['Stock'])
        for stock in param['scanned_stock_top_gainer_bound']:
            if stock not in param['scanned_stock_top_gainer']:
                if stock not in scanned_stock_top_gainer_bound:
                    stock_to_remove.append(stock)
        for stock in stock_to_remove:
            param['scanned_stock_top_gainer_bound'].remove(stock)
    else:
        param['scanned_stock_top_gainer'] = []
        param['scanned_stock_top_gainer_bound'] = []
        
    param['stock_top_gainer_w'].data = df1_sorted
    


    #-------------------loser-----------------------------------------------------------------------------------
    if len(df2_sorted)>0:
        df2_sorted = df2_sorted[~df2_sorted['Stock'].isin(stocks_to_remove)]
    
        param['scanned_stock_top_loser'] = list(df2_sorted.head(param['stock_top_loser_count'])['Stock'])#list(df2_sorted['Stock'])
    
        '''    
        if param['allow_sudden_change_entry']==True:
            for stock in param['scanned_stock_top_loser_bound']:
                if stock not in param['scanned_stock_top_loser_close_dict'].keys():
                    param['scanned_stock_top_loser_close_dict'][stock] = []
                #price = df2_sorted[df2_sorted['Stock']==stock]['LTP'].value
                price = df2_sorted.loc[df2_sorted['Stock']==stock,'LTP'].values[0]
                param['scanned_stock_top_loser_close_dict'][stock].append(price)
        '''
        max_sudden_change_stock = []
        max_sudden_change=0.0
        if param['allow_sudden_change_entry']==True:
            scem = param['sudden_change_entry_minute']
            scec = param['sudden_change_entry_count']
            for stock in list(df2_sorted['Stock']):#param['scanned_stock_top_loser']:
                if stock not in param['scanned_stock_top_loser_close_dict'].keys():
                    param['scanned_stock_top_loser_close_dict'][stock] = []
                price = df2_sorted.loc[df2_sorted['Stock']==stock,'LTP'].values[0]
                param['scanned_stock_top_loser_close_dict'][stock].append(price)
                close_list = param['scanned_stock_top_loser_close_dict'][stock]
                if len(close_list)>scem:
                    sudden_change = 100*(close_list[-1]/close_list[-4] - 1)
                    df2_sorted.loc[df2_sorted['Stock']==stock,'SuddenChange'] = round(sudden_change,2)
                    #if sudden_change<max_sudden_change:
                    #    max_sudden_change=sudden_change
                    #    #max_sudden_change_stock.append(stock)
            if 'SuddenChange' in df2_sorted.columns:
                max_sudden_change_stock = list(df2_sorted.sort_values(by='SuddenChange', ascending=True).head(scec)['Stock'])
                for stock in max_sudden_change_stock:
                    if stock not in param['scanned_stock_top_loser']:
                        param['scanned_stock_top_loser'].append(stock)
            #param['scanned_stock_top_loser_bound'].append(stock)
    
        
        stock_to_remove = []
        for stock in list(df2_sorted.head(len(df2_sorted))['Stock']):
            if stock not in param['scanned_stock_top_loser_bound']:
                param['scanned_stock_top_loser_bound'].append(stock)
        df2_sorted_bound = df2_sorted.head(len(df2_sorted))
        scanned_stock_top_loser_bound = list(df2_sorted_bound['Stock'])
        for stock in param['scanned_stock_top_loser_bound']:
            if stock not in param['scanned_stock_top_loser']:
                if stock not in scanned_stock_top_loser_bound:
                    stock_to_remove.append(stock)
        for stock in stock_to_remove:
            param['scanned_stock_top_loser_bound'].remove(stock)
    else:
        param['scanned_stock_top_loser'] = []
        param['scanned_stock_top_loser_bound'] = []

    param['stock_top_loser_w'].data = df2_sorted



    
    #----------------------------scanned option--------------------------------------------------------   
    param['scanned_option_top_gainer_token'] = []
    param['scanned_option_top_gainer'] = []
    #param['option_top_gainer_w'].data = pd.DataFrame()
    #print("param['stock_top_gainer_count']=",param['stock_top_gainer_count'])
    selected_strike_list = param['selected_strike']
    #strings = globalvar.g_stockparam['selected_strike'] 
    call_selected_strike_list_index = process_strings(selected_strike_list, 'CE')
    
    
    put_selected_strike_list_index = process_strings(selected_strike_list, 'PE')
    
    if 'frozen_option' not in list(param.keys()):
        param['frozen_option'] = {}
    #print("selected_strike_list: ",selected_strike_list)
    #print("call_selected_strike_list_index: ",call_selected_strike_list_index)
    #print("put_selected_strike_list_index: ",put_selected_strike_list_index)
    dbg_check=False
    if len(df1_sorted)>0:
        for i in range(len(df1_sorted)):
            #name=param['stock_top_gainer_w'].data['Stock'].iloc[i]
            name=df1_sorted['Stock'].iloc[i]
            price=df1_sorted['LTP'].iloc[i]
            
            optiontype='CE'
            expiry = get_stock_expiry(param)#'2024-11-28'
            if dbg_check: print("expiry:", expiry)
            
            #if name in list(param['frozen_option'].keys()):
            #    df = param['frozen_option'][name]
            #else:
            #    df = get_fno_stock_option(name=name, optiontype=optiontype, expiry=expiry, param=param) 
            #    param['frozen_option'][name] = df
            
            df = get_fno_stock_option(name=name, optiontype=optiontype, expiry=expiry, param=param)
            
            if dbg_check: print("CE:",df)
            
            #price = (df['strike'].iloc[0] + df['strike'].iloc[-1])/2
            
            dfstrikelist = list(df['strike'])
            atm_strike, atm_index = find_closest_with_index(dfstrikelist, price)
    
            dfselectedstrikelist = []
            for k in call_selected_strike_list_index:
                z = atm_index+k
                z = max(z,0)
                z = min(z, len(dfstrikelist)-1)
                strike = dfstrikelist[z]
                dfselectedstrikelist.append(strike)
    
            df1 = df[df['strike'].isin(dfselectedstrikelist)]
            #si = price*0.2
            #df1 = df[abs(df['strike']-price)<si] 
        
            cols = ['tradingsymbol','name','instrument_token','expiry','strike','lot_size']
            dff = df1[cols]
            
            #param['scanned_option_top_gainer'] = param['scanned_option_top_gainer'] + list(dff['tradingsymbol'])
            for index, row in dff.iterrows():
                #print(row)
                tradingsymbol = row['tradingsymbol']
                token = row['instrument_token']
                #print(tradingsymbol)
                param['scanned_option_top_gainer_token'].append(token)
                #param['scanned_option_top_gainer'][tradingsymbol] = {'instrument_token':token, 
                #                                                     'expiry':row['expiry'],'lot_size':row['lot_size']}
            #if i==0: param['option_top_gainer_w'].data = dff.copy()
            #else:  param['option_top_gainer_w'].data =  param['option_top_gainer_w'].data.append(dff.copy(), ignore_index=True)
            if i==0: dft = dff.copy()
            else:  dft = pd.concat([dft, dff], ignore_index=True)#dft =  dft.append(dff.copy(), ignore_index=True)
                
        #print(param['scanned_option_top_gainer'])
        if(len(df1_sorted)>0):
            dfv = get_gainer_option_volume(dft, param)
            param['scanned_option_top_gainer'] = list(dfv['tradingsymbol'])
            param['option_top_gainer_w'].data = dfv.copy()
            param['scanned_option_top_gainer_data'] = dfv.set_index('tradingsymbol').to_dict(orient='index')
    else:
        param['scanned_option_top_gainer_token'] = []
        param['scanned_option_top_gainer'] = []
        param['scanned_option_top_gainer_data'] = []
        param['option_top_gainer_w'].data = pd.DataFrame()


    
    
    param['scanned_option_top_loser_token'] = []
    param['scanned_option_top_loser'] = []
    
    if len(df2_sorted)>0:    
        for i in range(len(df2_sorted)):
            name=df2_sorted['Stock'].iloc[i]
            #print("name: ",name)
            price=df2_sorted['LTP'].iloc[i]
            
            optiontype='PE'
            expiry = get_stock_expiry(param)#'2024-11-28'
            df = get_fno_stock_option(name=name, optiontype=optiontype, expiry=expiry, param=param)
            #print("PE:",df)
            
            dfstrikelist = list(df['strike'])
            #print("dfstrikelist: ",dfstrikelist)
            atm_strike, atm_index = find_closest_with_index(dfstrikelist, price)
            #print("atm_strike, atm_index",atm_strike, atm_index)
            dfselectedstrikelist = []
            for k in put_selected_strike_list_index:
                z = atm_index+k
                z = max(z,0)
                z = min(z, len(dfstrikelist)-1)
                strike = dfstrikelist[z]
                dfselectedstrikelist.append(strike)
    
            df1 = df[df['strike'].isin(dfselectedstrikelist)]
            #price = (df['strike'].iloc[0] + df['strike'].iloc[-1])/2
            #si = price*0.05
            #df1 = df[abs(df['strike']-price)<si] 
        
            cols = ['tradingsymbol','name','instrument_token','expiry','strike','lot_size']
            dff = df1[cols]
    
            for index, row in dff.iterrows():
                tradingsymbol = row['tradingsymbol']
                token = row['instrument_token']
                #param['scanned_option_top_loser'].append(tradingsymbol)
                param['scanned_option_top_loser_token'].append(token)
                
            #param['scanned_option_top_loser'] = param['scanned_option_top_loser'] + list(dff['tradingsymbol'])
            #param['option_top_loser_w'].data = dff.copy()
            if i==0: dft2 = dff.copy()
            else:  dft2 = pd.concat([dft2, dff], ignore_index=True)#dft2 = dft2.append(dff.copy(), ignore_index=True)
    
        if(len(df2_sorted)>0):
            dfv2 = get_loser_option_volume(dft2, param)
            param['scanned_option_top_loser'] = list(dfv2['tradingsymbol'])
            param['option_top_loser_w'].data = dfv2.copy()
            param['scanned_option_top_loser_data'] = dfv2.set_index('tradingsymbol').to_dict(orient='index')
    else:
        param['scanned_option_top_loser_token'] = []
        param['scanned_option_top_loser'] = []
        param['scanned_option_top_loser_data'] = []
        param['option_top_loser_w'].data = pd.DataFrame()
    
    
    # scanned option data
    if(len(df1_sorted)>0 and len(df2_sorted)>0):
        param['scanned_option_data'] = {**param['scanned_option_top_gainer_data'], **param['scanned_option_top_loser_data']}
    elif(len(df1_sorted)>0):
        param['scanned_option_data'] = param['scanned_option_top_gainer_data']
    elif(len(df2_sorted)>0):
        param['scanned_option_data'] = param['scanned_option_top_loser_data']
    
    #display data
    #print("param['scanned_stock_top_gainer_bound']",param['scanned_stock_top_gainer_bound'])
    #print("param['scanned_stock_top_loser_bound']",param['scanned_stock_top_loser_bound'])
    #print("param['scanned_stock_top_gainer_close_dict']",param['scanned_stock_top_gainer_close_dict'])
    #print("param['scanned_stock_top_loser_close_dict']",param['scanned_stock_top_loser_close_dict'])
    return











def run_scanner_old(param):
    ld = get_day_price_change(param)
    #ld = get_instrument_history(param)
    #print(ld)
    #df = pd.DataFrame(ld)
    df = pd.DataFrame(ld)#list(ld.items()), columns=['Stock', 'Gain'])

    # remove blacklist stocks
    stocks_to_remove=[]
    try:
        stocks_to_remove=param['selected_blacklist']
    except:
        pass
    df = df[~df['Stock'].isin(stocks_to_remove)]

    
    df1_sorted = df.sort_values(by='Gain', ascending=False).head(100)
    df2_sorted = df.sort_values(by='Gain', ascending=True).head(100)
    #print(df1_sorted)

    #df1_sorted['Stock'].iloc[i]


    #----------------------------------gainer--------------------------------------------------------------------------
    param['scanned_stock_top_gainer'] = list(df1_sorted.head(param['stock_top_gainer_count'])['Stock'])#list(df1_sorted['Stock'])
    
    max_sudden_change_stock = []
    max_sudden_change=0.0
    if param['allow_sudden_change_entry']==True:
        scem = param['sudden_change_entry_minute']
        scec = param['sudden_change_entry_count']
        for stock in list(df1_sorted['Stock']):
            if stock not in param['scanned_stock_top_gainer_close_dict'].keys():
                param['scanned_stock_top_gainer_close_dict'][stock] = []
            price = df1_sorted.loc[df1_sorted['Stock']==stock,'LTP'].values[0]
            param['scanned_stock_top_gainer_close_dict'][stock].append(price)
            close_list = param['scanned_stock_top_gainer_close_dict'][stock]
            if len(close_list)>scem:
                sudden_change = 100*(close_list[-1]/close_list[-4] - 1)
                df1_sorted.loc[df1_sorted['Stock']==stock,'SuddenChange'] = round(sudden_change,2)
                #if sudden_change>max_sudden_change:
                #    max_sudden_change=sudden_change
                #    max_sudden_change_stock.append(stock)
                    #if len( max_sudden_change_stock)>=scec:break
        if 'SuddenChange' in df1_sorted.columns:
            max_sudden_change_stock = list(df1_sorted.sort_values(by='SuddenChange', ascending=False).head(scec)['Stock'])
            for stock in max_sudden_change_stock:
                if stock not in param['scanned_stock_top_gainer']:
                    param['scanned_stock_top_gainer'].append(stock)
                

    
    stock_to_remove = []
    for stock in list(df1_sorted.head(param['stock_top_gainer_count'])['Stock']):
        if stock not in param['scanned_stock_top_gainer_bound']:
            param['scanned_stock_top_gainer_bound'].append(stock)
    df1_sorted_bound = df1_sorted.head(param['stock_top_gainer_bound'])
    scanned_stock_top_gainer_bound = list(df1_sorted_bound['Stock'])
    for stock in param['scanned_stock_top_gainer_bound']:
        if stock not in param['scanned_stock_top_gainer']:
            if stock not in scanned_stock_top_gainer_bound:
                stock_to_remove.append(stock)
    for stock in stock_to_remove:
        param['scanned_stock_top_gainer_bound'].remove(stock)

    
    param['stock_top_gainer_w'].data = df1_sorted
    


    #-------------------loser-----------------------------------------------------------------------------------
    
    param['scanned_stock_top_loser'] = list(df2_sorted.head(param['stock_top_loser_count'])['Stock'])#list(df2_sorted['Stock'])

    '''    
    if param['allow_sudden_change_entry']==True:
        for stock in param['scanned_stock_top_loser_bound']:
            if stock not in param['scanned_stock_top_loser_close_dict'].keys():
                param['scanned_stock_top_loser_close_dict'][stock] = []
            #price = df2_sorted[df2_sorted['Stock']==stock]['LTP'].value
            price = df2_sorted.loc[df2_sorted['Stock']==stock,'LTP'].values[0]
            param['scanned_stock_top_loser_close_dict'][stock].append(price)
    '''
    max_sudden_change_stock = []
    max_sudden_change=0.0
    if param['allow_sudden_change_entry']==True:
        scem = param['sudden_change_entry_minute']
        scec = param['sudden_change_entry_count']
        for stock in list(df2_sorted['Stock']):#param['scanned_stock_top_loser']:
            if stock not in param['scanned_stock_top_loser_close_dict'].keys():
                param['scanned_stock_top_loser_close_dict'][stock] = []
            price = df2_sorted.loc[df2_sorted['Stock']==stock,'LTP'].values[0]
            param['scanned_stock_top_loser_close_dict'][stock].append(price)
            close_list = param['scanned_stock_top_loser_close_dict'][stock]
            if len(close_list)>scem:
                sudden_change = 100*(close_list[-1]/close_list[-4] - 1)
                df2_sorted.loc[df2_sorted['Stock']==stock,'SuddenChange'] = round(sudden_change,2)
                #if sudden_change<max_sudden_change:
                #    max_sudden_change=sudden_change
                #    #max_sudden_change_stock.append(stock)
        if 'SuddenChange' in df2_sorted.columns:
            max_sudden_change_stock = list(df2_sorted.sort_values(by='SuddenChange', ascending=True).head(scec)['Stock'])
            for stock in max_sudden_change_stock:
                if stock not in param['scanned_stock_top_loser']:
                    param['scanned_stock_top_loser'].append(stock)
        #param['scanned_stock_top_loser_bound'].append(stock)

    
    stock_to_remove = []
    for stock in list(df2_sorted.head(param['stock_top_loser_count'])['Stock']):
        if stock not in param['scanned_stock_top_loser_bound']:
            param['scanned_stock_top_loser_bound'].append(stock)
    df2_sorted_bound = df2_sorted.head(param['stock_top_loser_bound'])
    scanned_stock_top_loser_bound = list(df2_sorted_bound['Stock'])
    for stock in param['scanned_stock_top_loser_bound']:
        if stock not in param['scanned_stock_top_loser']:
            if stock not in scanned_stock_top_loser_bound:
                stock_to_remove.append(stock)
    for stock in stock_to_remove:
        param['scanned_stock_top_loser_bound'].remove(stock)


    param['stock_top_loser_w'].data = df2_sorted



    
    #----------------------------scanned option--------------------------------------------------------   
    param['scanned_option_top_gainer_token'] = []
    param['scanned_option_top_gainer'] = []
    #param['option_top_gainer_w'].data = pd.DataFrame()
    #print("param['stock_top_gainer_count']=",param['stock_top_gainer_count'])
    selected_strike_list = param['selected_strike']
    #strings = globalvar.g_stockparam['selected_strike'] 
    call_selected_strike_list_index = process_strings(selected_strike_list, 'CE')
    
    
    put_selected_strike_list_index = process_strings(selected_strike_list, 'PE')
    
    
    #print("selected_strike_list: ",selected_strike_list)
    #print("call_selected_strike_list_index: ",call_selected_strike_list_index)
    #print("put_selected_strike_list_index: ",put_selected_strike_list_index)
    dbg_check=False  
    for i in range(param['stock_top_gainer_count']):
        #name=param['stock_top_gainer_w'].data['Stock'].iloc[i]
        name=df1_sorted['Stock'].iloc[i]
        price=df1_sorted['LTP'].iloc[i]
        
        optiontype='CE'
        expiry = get_stock_expiry(param)#'2024-11-28'
        if dbg_check: print("expiry:", expiry)
        df = get_fno_stock_option(name=name, optiontype=optiontype, expiry=expiry, param=param)
        if dbg_check: print("CE:",df)
        
        #price = (df['strike'].iloc[0] + df['strike'].iloc[-1])/2
        
        dfstrikelist = list(df['strike'])
        atm_strike, atm_index = find_closest_with_index(dfstrikelist, price)

        dfselectedstrikelist = []
        for k in call_selected_strike_list_index:
            z = atm_index+k
            z = max(z,0)
            z = min(z, len(dfstrikelist)-1)
            strike = dfstrikelist[z]
            dfselectedstrikelist.append(strike)

        df1 = df[df['strike'].isin(dfselectedstrikelist)]
        #si = price*0.2
        #df1 = df[abs(df['strike']-price)<si] 
    
        cols = ['tradingsymbol','name','instrument_token','expiry','strike','lot_size']
        dff = df1[cols]
        
        #param['scanned_option_top_gainer'] = param['scanned_option_top_gainer'] + list(dff['tradingsymbol'])
        for index, row in dff.iterrows():
            #print(row)
            tradingsymbol = row['tradingsymbol']
            token = row['instrument_token']
            #print(tradingsymbol)
            param['scanned_option_top_gainer_token'].append(token)
            #param['scanned_option_top_gainer'][tradingsymbol] = {'instrument_token':token, 
            #                                                     'expiry':row['expiry'],'lot_size':row['lot_size']}
        #if i==0: param['option_top_gainer_w'].data = dff.copy()
        #else:  param['option_top_gainer_w'].data =  param['option_top_gainer_w'].data.append(dff.copy(), ignore_index=True)
        if i==0: dft = dff.copy()
        else:  dft = pd.concat([dft, dff], ignore_index=True)#dft =  dft.append(dff.copy(), ignore_index=True)
            
    #print(param['scanned_option_top_gainer'])
    if(param['stock_top_gainer_count']>0):
        dfv = get_gainer_option_volume(dft, param)
        param['scanned_option_top_gainer'] = list(dfv['tradingsymbol'])
        param['option_top_gainer_w'].data = dfv.copy()
        param['scanned_option_top_gainer_data'] = dfv.set_index('tradingsymbol').to_dict(orient='index')
    

    
 



    
    
    param['scanned_option_top_loser_token'] = []
    param['scanned_option_top_loser'] = []
    for i in range(param['stock_top_loser_count']):
        name=df2_sorted['Stock'].iloc[i]
        #print("name: ",name)
        price=df2_sorted['LTP'].iloc[i]
        
        optiontype='PE'
        expiry = get_stock_expiry(param)#'2024-11-28'
        df = get_fno_stock_option(name=name, optiontype=optiontype, expiry=expiry, param=param)
        #print("PE:",df)
        
        dfstrikelist = list(df['strike'])
        #print("dfstrikelist: ",dfstrikelist)
        atm_strike, atm_index = find_closest_with_index(dfstrikelist, price)
        #print("atm_strike, atm_index",atm_strike, atm_index)
        dfselectedstrikelist = []
        for k in put_selected_strike_list_index:
            z = atm_index+k
            z = max(z,0)
            z = min(z, len(dfstrikelist)-1)
            strike = dfstrikelist[z]
            dfselectedstrikelist.append(strike)

        df1 = df[df['strike'].isin(dfselectedstrikelist)]
        #price = (df['strike'].iloc[0] + df['strike'].iloc[-1])/2
        #si = price*0.05
        #df1 = df[abs(df['strike']-price)<si] 
    
        cols = ['tradingsymbol','name','instrument_token','expiry','strike','lot_size']
        dff = df1[cols]

        for index, row in dff.iterrows():
            tradingsymbol = row['tradingsymbol']
            token = row['instrument_token']
            #param['scanned_option_top_loser'].append(tradingsymbol)
            param['scanned_option_top_loser_token'].append(token)
            
        #param['scanned_option_top_loser'] = param['scanned_option_top_loser'] + list(dff['tradingsymbol'])
        #param['option_top_loser_w'].data = dff.copy()
        if i==0: dft2 = dff.copy()
        else:  dft2 = pd.concat([dft2, dff], ignore_index=True)#dft2 = dft2.append(dff.copy(), ignore_index=True)

    if(param['stock_top_loser_count']>0):
        dfv2 = get_loser_option_volume(dft2, param)
        param['scanned_option_top_loser'] = list(dfv2['tradingsymbol'])
        param['option_top_loser_w'].data = dfv2.copy()
        param['scanned_option_top_loser_data'] = dfv2.set_index('tradingsymbol').to_dict(orient='index')
    
    
    
    # scanned option data
    if(param['stock_top_gainer_count']>0 and param['stock_top_loser_count']>0):
        param['scanned_option_data'] = {**param['scanned_option_top_gainer_data'], **param['scanned_option_top_loser_data']}
    elif(param['stock_top_gainer_count']>0):
        param['scanned_option_data'] = param['scanned_option_top_gainer_data']
    elif(param['stock_top_loser_count']>0):
        param['scanned_option_data'] = param['scanned_option_top_loser_data']
    
    #display data
    print("param['scanned_stock_top_gainer_bound']",param['scanned_stock_top_gainer_bound'])
    print("param['scanned_stock_top_loser_bound']",param['scanned_stock_top_loser_bound'])
    #print("param['scanned_stock_top_gainer_close_dict']",param['scanned_stock_top_gainer_close_dict'])
    #print("param['scanned_stock_top_loser_close_dict']",param['scanned_stock_top_loser_close_dict'])
    return


#self.option_minimum_volume_in_lot_w
def get_gainer_option_volume(df, param):
    #print("get option volume")
    minlot = param['option_minimum_volume_in_lot']
    option_top_gainer_count = param['option_top_gainer_count']
    instrument_token_list = param['scanned_option_top_gainer_token']
    #print(instrument_token_list)
    quote = globalvar.g_kite.quote(instrument_token_list)
    #df = param['option_top_gainer_w'].data
    df['volume'] = 0
    #df = param['option_top_gainer_w'].data
    #print(df)
    for q,v in quote.items():
        token = v['instrument_token']
        volume = v['volume']
        condition = (df['instrument_token']==token)
        df.loc[condition,'volume'] = volume
    
    #df = df.sort_values(by='volume', ascending=False)
    #df = df[:option_top_gainer_count]
    df_filtered = df[df['volume'] > df['lot_size'] * minlot]
    df_top = df_filtered.groupby('name').apply(lambda x: x.nlargest(option_top_gainer_count, 'volume')).reset_index(drop=True)
    #param['option_top_gainer_w'].data = df_top.copy()
    
    #display(param['option_top_gainer_w'].data)
    return df_top


def get_loser_option_volume(df, param):
    #print("get option volume")
    minlot = param['option_minimum_volume_in_lot']
    option_top_loser_count = param['option_top_loser_count']
    instrument_token_list = param['scanned_option_top_loser_token']
    #print(instrument_token_list)
    quote = globalvar.g_kite.quote(instrument_token_list)
    #df = param['option_top_loser_w'].data
    df['volume'] = 0
    #df = param['option_top_gainer_w'].data
    #print(df)
    for q,v in quote.items():
        token = v['instrument_token']
        volume = v['volume']
        condition = (df['instrument_token']==token)
        df.loc[condition,'volume'] = volume
    
    #df = df.sort_values(by='volume', ascending=False)
    #df = df[:option_top_gainer_count]
    df_filtered = df[df['volume'] > df['lot_size'] * minlot]
    df_top = df_filtered.groupby('name').apply(lambda x: x.nlargest(option_top_loser_count, 'volume')).reset_index(drop=True)
    #param['option_top_loser_w'].data = df_top.copy()
    #display(param['option_top_gainer_w'].data)
    return df_top



def check_holiday(timenow):
    DEFAULT_DATA_FILE = '../default_data.xlsx'
    df = pd.read_excel(DEFAULT_DATA_FILE, sheet_name='HOLIDAYS', index_col=0)
    #print(timenow)
    date = timenow#.date()
    #print(date)
    dfl = list(pd.to_datetime(df.index).date)
    #print(dfl)
    if date in dfl:
        return True
    return False



def prune(candles_dict, prune_length=2):
    for key in list(candles_dict.keys()):
        candles = candles_dict[key]
        if len(candles)>prune_length:
            candles_dict[key] = candles[-prune_length:]




#END
