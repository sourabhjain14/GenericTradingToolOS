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
import traceback

import globalvar
import zerodha

def add_buy_order(candle, security, param, position=0, tag='', symbol=None, portfolio=None):
    #print("buy order: ", symbol, candle)
    margin = 0
    now_ = datetime.now().replace(microsecond=0)
    now = now_ if param['live_trading']==True else candle['datetime']
    #seconds_truncated = round(now.second + now.microsecond / 1_000_000, 2)
    #now_truncated = now.replace(second=int(seconds_truncated), microsecond=int((seconds_truncated % 1) * 1_000_000))
    #if lot==0:
    #    lot = param['lot']
    if 'lot_size' in security.keys():
        lot_size = security['lot_size']
    else:
        lot_size = param['lot']

    
    if position==0:    
        if param['useLot']==True:
            position = param['lot_size']#security['trade_capital']
        else:
            if candle['close'] < param['lower_exposure_price']:
                trade_cap = param['lower_exposure_trade_capital']
            else:
                trade_cap = param['trade_capital']#security['trade_capital']
            position = math.floor(trade_cap/(lot_size*candle['close']))
            #trade_cap = 0.01*security['trade_capital_percent']*param['account_capital']
            #position = math.floor(trade_cap/security['entryprice'])
    #print("position:",position)
    if position<1: return


    if param['use_X2']==True:
        position = position + position
        security['X2count'] = 1
    elif param['use_martingale']==True:
        position = position + position
        mcount = 1
        trade_table = param['trade_table']
        for z in range(len(trade_table)-1,-1,-1):
            trade = trade_table[z]
            spnl_ = trade['realizedPnL']
            if trade['remaining_position']==0:
                if spnl_<0:
                    position = position + position
                    mcount+=1
                    if  mcount>=param['martingale_length']:break
                else:
                    break
        security['martingale'] = mcount
        
    
    security['long_signal_fired'] = 1
    security['trade_in'] = 1

    tick_size = 0.05
    if symbol in globalvar.g_instrument_dict.keys():
        if 'tick_size' in globalvar.g_instrument_dict[symbol].keys():
            tick_size = globalvar.g_instrument_dict[symbol]['tick_size']
    tm = round(1.0/tick_size,0)
    
    entryprice = candle['close'] if 'ask' not in candle.keys() else candle['ask']
    entryprice_r = round(entryprice * tm) / tm + tick_size #entryprice#round( (entryprice//tick_size)*tick_size, 2)
    security['entryprice'] = round(entryprice_r,2)  if 'ask' not in candle.keys() else entryprice
    
    security['TSLPrice'] = 0.0
    security['trade_today'] += 1
    security['trade_in_time'] = datetime.now()

    if param['show_detail_log']: print(str(candle['datetime'])+'\t'+'LONG strategy Entry: '+str(security['entryprice']))

    
    
    added_position = position# - security['position']
    
    security['position'] = position
    
    security['holdingvalue'] = security['holdingvalue'] + security['entryprice']*added_position*lot_size
    #security['cumPnL'] = security['cumPnL'] + added_position*(security['averageprice'] - security['exitprice'])
    try:
        security['averageprice'] = security['holdingvalue'] / (lot_size*security['position'])
    except:
        security['holdingvalue'] = 0#security['averageprice'] = security['entryprice']
        

    comment = 'LONG strategy Entry: '+str(security['entryprice'])
    if tag!='': comment+=tag
    candle['comment']+=comment

    brick_size = 0
    if 'brick_size' in security.keys():
         brick_size = security['brick_size']

    jurikma = 0
    if 'jurikma' in security.keys():
        jurikma = security['jurikma']
    
    atr_brick = 0
    if 'atr_brick' in security.keys():
        atr_brick = security['atr_brick']
    
    price_delta = 0
    if 'price_delta' in security.keys():
        price_delta = security['price_delta']


    id = len(param['signal_list'])
    security['signal_id'] = id
    
    signal = {'id':id, 'TradeDirection':'BUY','symbol':symbol,'portfolio':portfolio,'datetime':now,'Long':True,
              'CloseLong':False, 'LongPrice':security['entryprice'],\
              'position':security['position'], 'unrealized_pnl':0.0,'PnL':0.0,'cumPnL':security['cumPnL'],'EntryPrice':security['entryprice'],
              'holdingvalue':round(security['holdingvalue'],2),'status_open':True,'margin':margin,'lot_size':lot_size,
              'comment':comment,'live':param['signal_live'], 'brick_size':brick_size,'jurikma':jurikma, 'atr_brick':atr_brick,'price_delta':price_delta}
    security['signal'].append(signal)
    
    param['signal_list'].append(signal)
    #siglen = len(globalvar.g_signal_dict[param['index_symbol']])

        

def add_short_order(candle, security, param, position=0, tag='', symbol=None, portfolio=None):
    now_ = datetime.now().replace(microsecond=0)
    now = now_ if param['live_trading']==True else candle['datetime']
    #seconds_truncated = round(now.second + now.microsecond / 1_000_000, 2)
    #now_truncated = now.replace(second=int(seconds_truncated), microsecond=int((seconds_truncated % 1) * 1_000_000))
    if 'lot_size' in security.keys():
        lot_size = security['lot_size']
    else:
        lot_size = param['lot']

    if position==0:    
        if param['useLot']==True:
            position = -param['lot_size']
        else:
            if candle['close'] < param['lower_exposure_price']:
                trade_cap = param['lower_exposure_trade_capital']
            else:
                trade_cap = param['trade_capital']#security['trade_capital']
            position = -math.floor(trade_cap/(lot_size*candle['close']))
            #trade_cap = 0.01*security['trade_capital_percent']*param['account_capital']
            #position = math.floor(trade_cap/security['entryprice'])
    #print("position:",position)
    
    
    # check margin requirements
    try:
        exchange = param['index_exchange']
        quantity = -position*lot_size
        price = round(candle['close'],2)
        margin = zerodha.get_margin(symbol, exchange, quantity, price)
        print("margin:",margin) 
    except:
        margin=0
    
    if abs(position)<1: return

    if param['use_X2']==True:
        position = position + position
        security['X2count'] = 1
    elif param['use_martingale']==True:
        position = position + position
        mcount = 1
        trade_table = param['trade_table']
        for z in range(len(trade_table)-1,-1,-1):
            trade = trade_table[z]
            spnl_ = trade['realizedPnL']
            if trade['remaining_position']==0:
                if spnl_<0:
                    position = position + position
                    mcount+=1
                    if  mcount>=param['martingale_length']:break
                else:
                    break
        security['martingale'] = mcount
        
    security['short_signal_fired'] = 1
    security['trade_in'] = -1
    security['entryprice'] = candle['close']
    security['TSLPrice'] = 0.0
    security['trade_today'] += 1
    security['trade_in_time'] = datetime.now()

    if param['show_detail_log']: print(str(candle['datetime'])+'\t'+'SHORT strategy Entry: '+str(security['entryprice']))

    
    
    added_position = position# - security['position']
    
    security['position'] = position
    
    security['holdingvalue'] = security['holdingvalue'] + security['entryprice']*added_position*lot_size
    #security['cumPnL'] = security['cumPnL'] + added_position*(security['averageprice'] - security['exitprice'])
    #security['holdingvalue'] = margin
    
    
    
    try:
        security['averageprice'] = security['holdingvalue'] / (lot_size*security['position'])
    except:
        security['holdingvalue'] = 0#security['averageprice'] = security['entryprice']
        

    comment = 'SHORT strategy Entry: '+str(security['entryprice'])
    if tag!='': comment+=tag
    candle['comment']+=comment

    
    brick_size = 0
    if 'brick_size' in security.keys():
         brick_size = security['brick_size']

    jurikma = 0
    if 'jurikma' in security.keys():
        jurikma = security['jurikma']
    
    atr_brick = 0
    if 'atr_brick' in security.keys():
        atr_brick = security['atr_brick']
    
    price_delta = 0
    if 'price_delta' in security.keys():
        price_delta = security['price_delta']

    id = len(param['signal_list'])
    security['signal_id'] = id
    
    signal = {'id':id, 'TradeDirection':'SHORT','symbol':symbol,'portfolio':portfolio,'datetime':now,'Short':True,
              'CloseShort':False, 'ShortPrice':security['entryprice'],\
              'position':security['position'], 'unrealized_pnl':0.0,'PnL':0.0,'cumPnL':security['cumPnL'],'EntryPrice':security['entryprice'],
              'holdingvalue':round(security['holdingvalue'],2),'status_open':True,'margin':margin,'lot_size':lot_size,
              'comment':comment,'live':param['signal_live'], 'brick_size':brick_size,'jurikma':jurikma, 'atr_brick':atr_brick,'price_delta':price_delta}
    security['signal'].append(signal)
    
    param['signal_list'].append(signal)
    #siglen = len(globalvar.g_signal_dict[param['index_symbol']])



        
def add_sell_order(candle, security, param, position=0, tag='', symbol=None, portfolio=None):
    #print("sell order: ", symbol, candle)
    
    now_ = datetime.now().replace(microsecond=0)
    now = now_ if param['live_trading']==True else candle['datetime']

    if 'lot_size' in security.keys():
        lot_size = security['lot_size']
    else:
        lot_size = param['lot']
        
    security['close_long_signal_fired'] = 1
    
    
    #security['exitprice'] = candle['close']  if 'bid' not in candle.keys() else candle['bid']
    tick_size = 0.05
    if symbol in globalvar.g_instrument_dict.keys():
        if 'tick_size' in globalvar.g_instrument_dict[symbol].keys():
            tick_size = globalvar.g_instrument_dict[symbol]['tick_size']
    tm = round(1.0/tick_size,0)
    
    exitprice = candle['close'] if 'bid' not in candle.keys() else candle['bid']
    exitprice_r = round(exitprice * tm) / tm - tick_size
    security['exitprice'] = round(exitprice_r,2)  if 'bid' not in candle.keys() else exitprice



    
    if position==0:position=security['position']
    if position>security['position']:position=security['position']
    '''
    if position==0:    
        if param['useLot']==True:
            position = security['trade_capital']
        else:
            trade_cap = 0.01*security['trade_capital_percent']*param['account_capital']
    '''
    
    added_position = -position# - security['position']
    
    security['position'] = security['position'] + added_position
    if abs(security['position'])<0.01:
        security['trade_in'] = 0
    
    
    security['holdingvalue'] = security['holdingvalue'] + lot_size*security['exitprice']*added_position
    
    PnL = lot_size*added_position*(security['averageprice'] - security['exitprice'])
    
    security['cumPnL'] = security['cumPnL'] + PnL#added_position*(security['averageprice'] - security['exitprice'])
    if security['position']==0: security['holdingvalue'] = 0
    #try:
    #    security['averageprice'] = security['holdingvalue'] / security['position']
    #except:
    #    security['holdingvalue'] = 0#security['averageprice'] = security['exitprice']
    
    
    
    if param['show_detail_log']: print(str(candle['datetime'])+'\t'+'LONG strategy Exit: '+str(security['exitprice']))
    comment='LONG strategy Exit: '+str(security['exitprice'])
    if tag!='': comment+=tag
    candle['comment']+=comment

    brick_size = 0
    if 'brick_size' in security.keys():
         brick_size = security['brick_size']
    
    jurikma = 0
    if 'jurikma' in security.keys():
        jurikma = security['jurikma']

    id = len(param['signal_list'])
    security['signal_id'] = id
    
    signal = {'id':id, 'TradeDirection':'SELL','symbol':symbol,'portfolio':portfolio,'datetime':now,'Long':False,'CloseLong':True,\
                  'CloseLongPrice':security['exitprice'],'ExitPrice':security['exitprice'], 'position':position,'unrealized_pnl':0.0,
              'PnL':round(PnL,2),'cumPnL':round(security['cumPnL'],2),'holdingvalue':security['holdingvalue'],'lot_size':lot_size,
              'status_open':False, 'comment':comment,'live':param['signal_live'], 'brick_size':brick_size,'jurikma':jurikma}
    
    security['signal'].append(signal)
    param['signal_list'].append(signal)




def add_cover_order(candle, security, param, position=0, tag='', symbol=None, portfolio=None):
    now_ = datetime.now().replace(microsecond=0)
    now = now_ if param['live_trading']==True else candle['datetime']

    if 'lot_size' in security.keys():
        lot_size = security['lot_size']
    else:
        lot_size = param['lot']
        
    #position = -position

    
    security['close_short_signal_fired'] = 1
    security['exitprice'] = candle['close']
    
    if position==0:position=security['position']
    if position<security['position']:position=security['position']
    '''
    if position==0:    
        if param['useLot']==True:
            position = security['trade_capital']
        else:
            trade_cap = 0.01*security['trade_capital_percent']*param['account_capital']
    '''
    
    added_position = -position# - security['position']
    
    security['position'] = security['position'] + added_position
    if abs(security['position'])<0.01:
        security['trade_in'] = 0
    
    
    security['holdingvalue'] = security['holdingvalue'] + lot_size*security['exitprice']*added_position
    
    PnL = lot_size*added_position*(security['averageprice'] - security['exitprice'])
    
    security['cumPnL'] = security['cumPnL'] + PnL#added_position*(security['averageprice'] - security['exitprice'])
    if security['position']==0: security['holdingvalue'] = 0
    #try:
    #    security['averageprice'] = security['holdingvalue'] / security['position']
    #except:
    #    security['holdingvalue'] = 0#security['averageprice'] = security['exitprice']
    
    
    
    if param['show_detail_log']: print(str(candle['datetime'])+'\t'+'SHORT strategy Exit: '+str(security['exitprice']))
    comment='SHORT strategy Exit: '+str(security['exitprice'])
    if tag!='': comment+=tag
    candle['comment']+=comment

    brick_size = 0
    if 'brick_size' in security.keys():
         brick_size = security['brick_size']
    
    jurikma = 0
    if 'jurikma' in security.keys():
        jurikma = security['jurikma']


    id = len(param['signal_list'])
    security['signal_id'] = id
    
    signal = {'id':id,'TradeDirection':'COVER','symbol':symbol,'portfolio':portfolio,'datetime':now,'Short':False,'CloseShort':True,\
                  'CloseShortPrice':security['exitprice'],'ExitPrice':security['exitprice'], 'position':position,'unrealized_pnl':0.0,
              'PnL':round(PnL,2),'cumPnL':round(security['cumPnL'],2),'holdingvalue':security['holdingvalue'],'lot_size':lot_size,
              'status_open':False, 'comment':comment,'live':param['signal_live'], 'brick_size':brick_size,'jurikma':jurikma}
    
    security['signal'].append(signal)
    param['signal_list'].append(signal)
            
            
'''        
def add_short_order(candle, security, param, position=0):
    if position==0:    
        if param['useLot']==True:
            position = -security['trade_capital']
        else:
            trade_cap = security['trade_capital']
            position = -math.floor(trade_cap/(param['lot']*candle['close']))
            #trade_cap = 0.01*security['trade_capital_percent']*param['account_capital']
            #position = -math.floor(trade_cap/security['entryprice'])
    
    if abs(position)<1: return
    
    security['short_signal_fired'] = 1
    security['trade_in'] = -1
    security['entryprice'] = candle['close']
    security['TSLPrice'] = 0.0
    security['trade_today'] += 1
    security['trade_in_time'] = datetime.now()

    if param['show_detail_log']: print(str(candle['datetime'])+'\t'+'SHORT strategy Entry: '+str(security['entryprice']))

    

        
    added_position = position - security['position']
    
    security['position'] = position
    
    security['holdingvalue'] = security['holdingvalue'] + security['entryprice']*added_position
    try:
        security['averageprice'] = security['holdingvalue'] / security['position']
    except:
        security['holdingvalue'] = 0#security['averageprice'] = security['entryprice']

    comment = 'SHORT strategy Entry: '+str(security['entryprice'])
    candle['comment']+=comment
    signal = {'datetime':candle['datetime'],'Short':True, 'ShortPrice':security['entryprice'],\
              'position':security['position'],'PnL':0.0,'cumPnL':security['cumPnL'],'comment':comment}
    security['signal'].append(signal)
'''        
        
    
    
    
def add_cover_order_old(candle, security, param, position=0):
    security['close_short_signal_fired'] = 1
    security['exitprice'] = candle['close']
    '''
    if position==0:    
        if param['useLot']==True:
            position = security['trade_capital']
        else:
            trade_cap = 0.01*security['trade_capital_percent']*param['account_capital']
    '''
    
    added_position = position - security['position']
    
    security['position'] = position
    if security['position']>=0:
        security['trade_in'] = 0
    
    
    security['holdingvalue'] = security['holdingvalue'] + security['exitprice']*added_position
    PnL = added_position*(security['averageprice'] - security['exitprice'])
    security['cumPnL'] = security['cumPnL'] + added_position*(security['averageprice'] - security['exitprice'])
    if security['position']==0: security['holdingvalue'] = 0
    '''    
    try:
        security['averageprice'] = security['holdingvalue'] / security['position']
    except:
        security['holdingvalue'] = 0#security['averageprice'] = security['exitprice']
    '''    
        
    if param['show_detail_log']: print(str(candle['datetime'])+'\t'+'SHORT strategy Exit: '+str(security['exitprice']))
    comment='SHORT strategy Exit: '+str(security['exitprice'])
    candle['comment']+=comment
    
    #security['cumPnL'] = security['cumPnL'] + (security['entryprice'] - security['exitprice'])
    
    
    signal = {'datetime':candle['datetime'],'CloseShort':True,\
                  'CloseShortPrice':security['exitprice'], 'position':security['position'],'PnL':PnL,'cumPnL':security['cumPnL'],'comment':comment}
    
    security['signal'].append(signal)    
    
    
    
#---------------------------------- risk management----------------------------------------------------    
    
    
def add_stop_loss(param, security):
    if param['stop_loss_type']=='Percentage':
        if security['position']*security['trade_in']>0:
            security['SLPrice'] = security['entryprice']*(1.0-param['SL']/100.0)
        elif security['position']*security['trade_in']<0:
            security['SLPrice'] = security['entryprice']*(1.0+param['SL']/100.0) 
    elif param['stop_loss_type']=='Points':
        if security['position']*security['trade_in']>0:
            security['SLPrice'] = security['entryprice'] - param['SL']   
        elif security['position']*security['trade_in']<0:
            security['SLPrice'] = security['entryprice'] + param['SL']
    elif param['stop_loss_type']=='Rupee':
        if security['position']*security['trade_in']>0:
            security['SLPrice'] = round((security['holdingvalue'] - param['SL'])/(param['lot']*security['position']), 2)   
        elif security['position']*security['trade_in']<0:
            security['SLPrice'] = round((security['holdingvalue'] + param['SL'])/(param['lot']*security['position']), 2)
    elif param['stop_loss_type']=='BoxCount':
        if security['position']*security['trade_in']>0:
            security['SLPrice'] = security['entryprice'] - param['SL']*security['brick_size']
        elif security['position']*security['trade_in']<0:
            security['SLPrice'] = security['entryprice'] + param['SL']*security['brick_size']
    security['SLPrice'] = max(0.05,security['SLPrice'])
            
    
    
    
def add_target(param, security):
    if param['target_type']=='Percentage':
        if security['position']*security['trade_in']>0:
            security['TargetPrice'] = security['entryprice']*(1.0+param['target']/100.0)   
        elif security['position']*security['trade_in']<0:
            security['TargetPrice'] = security['entryprice']*(1.0-param['target']/100.0) 
    elif param['target_type']=='Points':
        if security['position']*security['trade_in']>0:
            security['TargetPrice'] = security['entryprice'] + param['target']   
        elif security['position']*security['trade_in']<0:
            security['TargetPrice'] = security['entryprice'] - param['target'] 
    elif param['target_type']=='Rupee':
        if security['position']*security['trade_in']>0:
            security['TargetPrice'] = round((security['holdingvalue'] + param['target'])/(param['lot']*security['position']), 2)   
        elif security['position']*security['trade_in']<0:
            security['TargetPrice'] = round((security['holdingvalue'] - param['target'])/(param['lot']*security['position']), 2)
    elif param['target_type']=='BoxCount':
        if security['position']*security['trade_in']>0:
            security['TargetPrice'] = security['entryprice'] + param['target']*security['brick_size']
        elif security['position']*security['trade_in']<0:
            security['TargetPrice'] = security['entryprice'] - param['target']*security['brick_size']
    security['TargetPrice'] = max(0.05,security['TargetPrice'])        


def add_target_custom(param, security, value, tag):
    if security['position']>0:
        #security['TargetPrice'] = security['entryprice'] + value
        security[tag] = security['entryprice'] + value
    elif security['position']<0:
        #security['TargetPrice'] = security['entryprice'] - value
        security[tag] = security['entryprice'] - value
    else:
        return
    #security['TargetPrice'] = max(0.05,security['TargetPrice']) 
    security[tag] = max(0.05,security[tag])
    
            
def add_trail_stop_loss(param, security, close):
    if param['trail_type']=='Percentage':
        if security['position']*security['trade_in']>0:
            pnl = 100*(close / security['entryprice'] - 1)>=param['trail_by']
            TSLPrice = close - security['entryprice']*(param['trail_by']/100.0)
            if pnl and security['TSLPrice']<0.01:
                security['TSLPrice']=TSLPrice
            if security['TSLPrice']>0:
                security['TSLPrice'] = max(TSLPrice, security['TSLPrice'])
        elif security['position']*security['trade_in']<0:
            pnl = 100*(security['entryprice'] / close - 1)>=param['trail_by']
            TSLPrice = close + close*(param['trail_by']/100.0)
            if security['TSLPrice']<0.01:
                security['TSLPrice']=TSLPrice
            if security['TSLPrice']>0:
                security['TSLPrice'] = min(TSLPrice, security['TSLPrice']) 
    elif param['trail_type']=='Points':
        if security['position']*security['trade_in']>0:
            pnl = close - security['entryprice'] >=param['trail_by']
            TSLPrice = close - param['trail_by']
            if pnl and security['TSLPrice']<0.01:
                security['TSLPrice']=TSLPrice
            if security['TSLPrice']>0:# and (close-(security['TSLPrice']+param['trail_by']))>param['trail_step']:
                security['TSLPrice'] = max(TSLPrice, security['TSLPrice'])   
        elif security['position']*security['trade_in']<0:
            pnl = security['entryprice'] - close >=param['trail_by']
            TSLPrice = close + param['trail_by']
            if security['TSLPrice']<0.01:
                security['TSLPrice']=TSLPrice
            if security['TSLPrice']>0:
                security['TSLPrice'] = min(TSLPrice, security['TSLPrice'])
    elif param['trail_type']=='Rupee':
        if security['position']*security['trade_in']>0:
            #security['SLPrice'] = round((security['holdingvalue'] - param['SL'])/(param['lot']*security['position']), 2)
            pnl = (close*param['lot']*security['position']) - security['holdingvalue'] >= param['trail_by']
            #TSLPrice = close - param['trail_by']
            TSLPrice = round(((close*param['lot']*security['position']) - param['trail_by'])/(param['lot']*security['position']), 2)
            if pnl and security['TSLPrice']<0.01:
                security['TSLPrice']=TSLPrice
            if security['TSLPrice']>0:# and (close-(security['TSLPrice']+param['trail_by']))>param['trail_step']:
                security['TSLPrice'] = max(TSLPrice, security['TSLPrice'])   
        elif security['position']*security['trade_in']<0:
            pnl =  security['holdingvalue'] - (close*param['lot']*security['position']) >= param['trail_by']
            TSLPrice = round(((close*param['lot']*security['position']) + param['trail_by'])/(param['lot']*security['position']), 2)
            if security['TSLPrice']<0.01:
                security['TSLPrice']=TSLPrice
            if security['TSLPrice']>0:
                security['TSLPrice'] = min(TSLPrice, security['TSLPrice'])
    elif param['trail_type']=='BoxCount':
        if security['position']*security['trade_in']>0:
            pnl = close - security['entryprice'] >=param['trail_by']*security['brick_size']
            TSLPrice = close - param['trail_by']*security['brick_size']
            if pnl and security['TSLPrice']<0.01:
                security['TSLPrice']=TSLPrice
            if security['TSLPrice']>0:# and (close-(security['TSLPrice']+param['trail_by']))>param['trail_step']:
                security['TSLPrice'] = max(TSLPrice, security['TSLPrice'])   
        elif security['position']*security['trade_in']<0:
            pnl = security['entryprice'] - close >=param['trail_by']*security['brick_size']
            TSLPrice = close + param['trail_by']*security['brick_size']
            if security['TSLPrice']<0.01:
                security['TSLPrice']=TSLPrice
            if security['TSLPrice']>0:
                security['TSLPrice'] = min(TSLPrice, security['TSLPrice'])
                
    


'''
signal = {'TradeDirection':'BUY','symbol':symbol,'portfolio':portfolio,'datetime':now,'Long':True,'CloseLong':False, 'LongPrice':security['entryprice'],\
              'position':security['position'], 'unrealized_pnl':0.0,'PnL':0.0,'cumPnL':security['cumPnL'],'EntryPrice':security['entryprice'],
              'holdingvalue':round(security['holdingvalue'],2),'status_open':True,'margin':margin,
              'comment':comment,'live':param['signal_live'], 'brick_size':brick_size,'jurikma':jurikma, 'atr_brick':atr_brick,'price_delta':price_delta}
'''

def update_security(param, security, price, transaction_type=None):
    if transaction_type=='B': 
        security['entryprice'] = price
        security['holdingvalue'] = security['entryprice']*security['position']*security['lot_size']  
        if(param['use_target']==True):
            add_target(param, security)
        if(param['use_stop_loss']==True):
            add_stop_loss(param, security)
        if security['martingale'] > 0:
            value = security['brick_size']
            add_target_custom(param, security, value, 'MartingaleTargetPrice')
        if security['X2count'] > 0:
            value = param['X2_target']*security['brick_size']
            add_target_custom(param, security, value, 'X2TargetPrice')
    else:
        security['exitprice'] = price
    


def update_signal_list(param, portfolio_dict):
    signal_list = param['signal_list']
    numsignal = len(signal_list)
    ignore_list = []
    for i in range(numsignal-1,-1,-1):
        signal = signal_list[i]
        id = signal['id']
        signal_symbol = signal['symbol']
        portfolio = signal['portfolio']
        trade_direction = signal['TradeDirection']
        
        security = portfolio_dict[portfolio][signal_symbol]
        signal_id = security['signal_id']
        position = security['position']
        
        id_match = id==signal_id
        if id_match and trade_direction=='BUY':
            if signal_symbol not in ignore_list:
                ignore_list.append(signal_symbol)
                signal['EntryPrice'] = security['entryprice']
                signal['holdingvalue'] = security['holdingvalue']
        elif id_match and trade_direction=='SELL':
            if signal_symbol not in ignore_list:
                ignore_list.append(signal_symbol)
                signal['ExitPrice'] = security['exitprice']
                signal['PnL'] = -security['lot_size']*signal['position']*(security['entryprice'] - security['exitprice'])
                print("updating exit: ", signal['PnL'], security['lot_size'], signal['position'], security['entryprice'] , security['exitprice'])
        elif id_match and trade_direction=='SHORT':
            if signal_symbol not in ignore_list:
                ignore_list.append(signal_symbol)
                signal['EntryPrice'] = security['entryprice']
                signal['holdingvalue'] = security['holdingvalue']
        elif id_match and trade_direction=='COVER':
            if signal_symbol not in ignore_list:
                ignore_list.append(signal_symbol)
                signal['ExitPrice'] = security['exitprice']
                signal['PnL'] = -security['lot_size']*signal['position']*(security['entryprice'] - security['exitprice'])




    

def get_state_analysis(symbol, candles, index, portfolio_dict, portfolio, param, live):
    return
    
    candle = candles[index]
    security = portfolio_dict[portfolio][symbol]
    
    if index<1:
        candle[portfolio+'trade_in'] = 0
        candle[portfolio+'position'] = 0
        candle[portfolio+'entryprice'] = 0.0
        candle[portfolio+'exitprice'] = 0.0
        candle[portfolio+'exit_flag'] = 0
        candle[portfolio+'sum_PnL_long_trades'] = 0.0
        candle[portfolio+'sum_PnL_short_trades'] = 0.0
        return
    
    previous = candles[index-1]
    
    
    candle[portfolio+'trade_in'] = security['trade_in']
    candle[portfolio+'position'] = security['position']
    
    candle[portfolio+'entryprice'] = security['entryprice']
    candle[portfolio+'exitprice'] = security['exitprice']
    
    
    sgn = math.copysign(1,candle[portfolio+'trade_in'])
    sgn1 = math.copysign(1,previous[portfolio+'trade_in'])
    
    sgnentry = candle[portfolio+'trade_in'] != previous[portfolio+'trade_in'] and abs(candle[portfolio+'trade_in'])==1
    sgntrade = candle[portfolio+'trade_in'] == previous[portfolio+'trade_in'] and previous[portfolio+'trade_in']!=0
    sgnexit = candle[portfolio+'trade_in'] != previous[portfolio+'trade_in'] and previous[portfolio+'trade_in']!=0
    
    #print(candle[portfolio+'trade_in'], sgnentry, sgntrade, sgnexit)
    
    pos = candle[portfolio+'position']
    pos1 = previous[portfolio+'position']
    
    changePnL = sgn1*pos1*(candle[portfolio+'exitprice'] - previous['close']) + sgn*pos*(candle['close'] - candle[portfolio+'exitprice'])
    
    pnl = 0.0
    if sgnentry:
        pnl = sgn*pos*(candle['close']-candle[portfolio+'entryprice'])
        candle[portfolio+'sum_PnL_long_trades'] = pnl if sgn==1 else 0.0
        candle[portfolio+'sum_PnL_short_trades'] = pnl if sgn==-1 else 0.0
    elif sgntrade:
        pnl = sgn*pos*(candle['close']-previous['close'])
        candle[portfolio+'sum_PnL_long_trades'] = previous[portfolio+'sum_PnL_long_trades']+pnl  if sgn==1 else 0.0
        candle[portfolio+'sum_PnL_short_trades'] = previous[portfolio+'sum_PnL_short_trades']+pnl  if sgn==-1 else 0.0
    elif sgnexit:
        pnl = changePnL
        candle[portfolio+'sum_PnL_long_trades'] = previous[portfolio+'sum_PnL_long_trades']+pnl  if sgn==1 else 0.0
        candle[portfolio+'sum_PnL_short_trades'] = previous[portfolio+'sum_PnL_short_trades']+pnl  if sgn==-1 else 0.0
    else:
        pnl = 0.0
        candle[portfolio+'sum_PnL_long_trades'] =  0.0
        candle[portfolio+'sum_PnL_short_trades'] =  0.0
    
    #print(pnl)
    
    
    candle[portfolio+'PnL'] = pnl
    
    
    if 'stoplossprice' in security.keys():
        candle[portfolio+'stoplossprice'] = security['stoplossprice']
        
    if 'takeprofitprice' in security.keys():
        candle[portfolio+'takeprofitprice'] = security['takeprofitprice'] 
   
        


    
def status_intraday_squareoff(candles, index, param):
    candle = candles[index]
    #security =  portfolio_dict[portfolio][symbol]
   
    now=candle['datetime']
    hour = now.hour
    minute = now.minute
    clocktime = 100*hour+minute
    
    tradeSquareOff = False
    tradeSquareOff = param['tradeSquare'] == True and \
    param['tradeSquareTime'] <= clocktime
    
    return tradeSquareOff
    
    
    
    


def check_tradewindow(candles, index, param):  
    now=candles[index]['datetime']
    hour = now.hour
    minute = now.minute
    clocktime = 100*hour+minute
    
    '--------------check trade window-----------------------'
    tradeWindow = True
    if param['useTradewindow'] == True:
        tradeWindow = param['tradewindowStart'] <= clocktime and param['tradewindowEnd'] >= clocktime    
    
    return tradeWindow
    


def calc_position(price, security, param):
    #print(param)
    #print(security)
    if param['quantity_configuration'] == 'Risk per trade':
        position = int(param['risk_per_trade']/(price*0.01*param['SL']*100))
    else:
        position = param['no_of_lots']
            
    position = min(position, param['max_no_of_lots'])
    
    if security['runningpnl']<globalvar.max_loss:
        position = 0
        
    if security['runningpnl']>globalvar.max_profit:
        position = 0
    
    #print(position, security['runningpnl'])
    return position


def close_all_positions(candle, security, param):
    candletime = candle['datetime'].strftime("%Y-%m-%d %H:%M:%S")
    candleclock = candle['datetime'].hour*100+candle['datetime'].minute 
    
    price = round(candle['close'],2)
    
    if True:
        for symbolo in security['option'].keys():
            optionprice = candle[symbolo]
            optsym = symbolo.replace('_close','')
            
            if security['option'][symbolo]['trade_in']==1:
                add_close_long(security['option'][symbolo], optionprice)
                
                security['totalpnl'] +=security['option'][symbolo]['pnl'] 
                print("Max PnL long exit: ",candleclock, price, symbolo, optionprice,'\n')
                
                bd = {"datetime":candletime,"comment":"Long Exit:Max PnL","Symbol":optsym,"EntryPrice":None,"ExitPrice":security['option'][symbolo]['exitprice'], "Position":0, "EntryValue":security['option'][symbolo]['entryvalue'], "ExitValue":security['option'][symbolo]['exitvalue'],"PNL":security['option'][symbolo]['pnl'],"SUM_PNL":security['option'][symbolo]['sumpnl'],"TOTAL_PNL":security['totalpnl'],"IndexValue":price}
                security['backdata'].append(bd)
                
            if security['option'][symbolo]['trade_in']==-1:
                add_close_short(security['option'][symbolo], optionprice)
                
                security['totalpnl'] +=security['option'][symbolo]['pnl']
                print("Max PnL short exit: ",candleclock, price, symbolo, optionprice,'\n')
                
                bd = {"datetime":candletime,"comment":"Short Exit:Max PnL","Symbol":optsym,"EntryPrice":None,"ExitPrice":security['option'][symbolo]['exitprice'], "Position":0, "EntryValue":security['option'][symbolo]['entryvalue'], "ExitValue":security['option'][symbolo]['exitvalue'],"PNL":security['option'][symbolo]['pnl'],"SUM_PNL":security['option'][symbolo]['sumpnl'],"TOTAL_PNL":security['totalpnl'],"IndexValue":price}
                security['backdata'].append(bd)
               
        

def get_option_symbol(symbol, expiry, strike, optiontype):
    expy = expiry.replace('-','')[2:]
    prlen = len(str(int(strike)))
    cprlen = 5 - prlen
    zerostr = ''
    zerostr2 = '000'
    for z in range(cprlen):
        zerostr = zerostr+'0'
    optsym = symbol+expy+optiontype+zerostr+str(int(strike))+zerostr2
    return optsym
            
        
        
def open_collateral_position(optionType, symbol, trade_dict, candle, security, param, position):
    #security['collateral'] = {}
    price = round(candle['close'],2)
    candleclock = candle['datetime'].hour*100+candle['datetime'].minute
    candletime = candle['datetime'].strftime("%Y-%m-%d %H:%M:%S")
    
    calloptionholding = 0
    for opc in security['option'].keys():
        opcpos = security['option'][opc]['position']
        opctradein = security['option'][opc]['trade_in']
        opctype = security['option'][opc]['optionType']
        if opcpos>0 and opctradein==-1 and opctype==optionType:
            calloptionholding+=opcpos

    callcollateralholding = 0
    for opc in security['collateral'].keys():
        opcpos = security['collateral'][opc]['position']
        opctradein = security['collateral'][opc]['trade_in']
        opctype = security['collateral'][opc]['optionType']
        if opcpos>0 and opctradein==1 and opctype==optionType:
            callcollateralholding+=opcpos

    if callcollateralholding <= calloptionholding:
        expiry = candle['expiry']
        collateral_close_near_one = 1000.0
        collateralOTMcall = security['optionOTMcall'].copy() if optionType=='C' else security['optionOTMput'].copy()
        collateralOTMcallLast = collateralOTMcall[-1]
        #print(collateralOTMcall)
        for i in range(10):
            if optionType=='C':collateralOTMcallLast+=5
            else:collateralOTMcallLast-=5    
            if param['live_trading']==False:
                for elem in param['instrument_option_list']:
                    if str(collateralOTMcallLast)+'000' in elem:
                        collateralOTMcall.append(collateralOTMcallLast)
            else:
                collateralOTMcall.append(collateralOTMcallLast)
                
        print(collateralOTMcall)

        for strike in collateralOTMcall:
            optsymc = get_option_symbol(symbol, expiry, strike, optionType)
            symbolc = optsymc+'_close'
            #print(symbolc)
            collateral_close_near_one_symbol = symbolc
            if param['live_trading']==True:
                if symbolc in candle.keys():
                    collateral_close = candle[symbolc]
                else:
                    collateral_close = get_quote(param['ibprogram'], 'SPX', 'Option', 'CBOE', expiry.replace('-',''), strike, optionType)
            else:
                collateral_close = candle[symbolc]
            
            collateral_close_near_one = min(collateral_close_near_one, collateral_close)
            collateral_close_near_one_strike = strike
            if collateral_close_near_one<1.0:
                break

        if symbolc not in security['collateral'].keys(): security['collateral'][symbolc] = {}
        #collateral_close_near_one_symbol = get_option_symbol(symbol, expiry, collateral_close_near_one_strike, 'C')

        trade_dict[collateral_close_near_one_symbol] = {'expiry':candle['expiry'], 'strike':collateral_close_near_one_strike, 'optionType':optionType, 'tradingClass':'SPXW'}   
        add_long(security['collateral'][symbolc], symbolc, collateral_close_near_one, position, trade_dict)

        #print(optionType, "long entry time: ",candleclock,"Index:",price, optsymc,' dailyvwap',candle[optsymc+'_atp'],'\n')
        bd = {"datetime":candletime,"comment":"Long Entry:Collateral","Symbol":optsymc,"EntryPrice":security['collateral'][symbolc]['entryprice'],"ExitPrice":None, "Position":security['collateral'][symbolc]['position'], "EntryValue":100*security['collateral'][symbolc]['entryprice']*security['collateral'][symbolc]['position'], "ExitValue":None,"PNL":0.0,"SUM_PNL":0.0,"TOTAL_PNL":security['totalpnl'],"IndexValue":price}
        security['backdata'].append(bd)


def build_trade_table(param):
    c=0
    trade_table=[]
    dflist = param['signal_list']
    
    #print(dflist)
    for k in range(len(dflist)):
        trade_ = dflist[k]
        trade = trade_.copy()
        #if c>10:break
        c+=1
        #print(trade)
        #if(len(trade_table)>1):print(trade_table[1])
        #print(c, trade['symbol'],trade['TradeDirection'],trade['datetime'],trade['position'])#,trade['remaining_position'])
        if trade['TradeDirection']=="BUY":
            #print(c, trade['symbol'],trade['TradeDirection'],trade['datetime'],trade['position'])#,trade['remaining_position'])
            trade['remaining_position'] = trade['position']
            trade['EntryDateTime'] = trade['datetime']
            trade['EntryPosition'] = trade['position']
            trade['EntryHoldingValue'] = trade['holdingvalue']
            trade['EntryMessage'] = trade['comment']
            trade_table.append(trade)
        elif trade['TradeDirection']=="SHORT":
            #print(c, trade['symbol'],trade['TradeDirection'],trade['datetime'],trade['position'])#,trade['remaining_position'])
            trade['remaining_position'] = trade['position']
            trade['EntryDateTime'] = trade['datetime']
            trade['EntryPosition'] = trade['position']
            trade['EntryHoldingValue'] = trade['holdingvalue']
            trade['EntryMessage'] = trade['comment']
            trade_table.append(trade)
        else:
            #continue
            #print(c, trade['symbol'],trade['TradeDirection'],trade['datetime'],trade['position'])#,trade['remaining_position'])
            #print(trade)
            for i in range(len(trade_table)-1,-1,-1):
                trade_last = trade_table[i]
                if trade_last['symbol']==trade['symbol'] and (trade_last['TradeDirection']=="BUY" or trade_last['TradeDirection']=="SHORT"):
                    if abs(trade_last['remaining_position'])>0:
                        trade_last['remaining_position'] = trade_last['remaining_position'] - trade['position']
                        if 'ExitDateTime' not in trade_last.keys():
                            trade_last['ExitDateTime'] = trade['datetime']
                        else:
                            trade_last['ExitDateTime2'] = trade['datetime']
                        if 'ExitPosition' not in trade_last.keys():
                            trade_last['ExitPosition'] = trade['position']
                        else:
                            trade_last['ExitPosition2'] = trade['position']
                        if 'ExitPrice' not in trade_last.keys():
                            #if math.isnan(trade_last['ExitPrice']):
                            trade_last['ExitPrice'] = trade['ExitPrice']
                        else:
                            trade_last['ExitPrice2'] = trade['ExitPrice']
                        if 'ExitMessage' not in trade_last.keys():
                            trade_last['ExitMessage'] = trade['comment']
                        else:
                            trade_last['ExitMessage2'] = trade['comment']
                        if 'ExitPnL' not in trade_last.keys():
                            trade_last['ExitPnL'] = trade['PnL']
                        else:
                            trade_last['ExitPnL2'] = trade['PnL']
                        if 'ExitHoldingValue' not in trade_last.keys():
                            trade_last['ExitHoldingValue'] = trade['holdingvalue']
                        else:
                            trade_last['ExitHoldingValue2'] = trade['holdingvalue']
                #print(i,trade_last)
        #if(len(trade_table)>1):print(c,trade_table[1])
    #print(trade_table)
    totalPnL=0
    for trade in trade_table:
        spnl_=0
        if 'ExitPrice' in trade.keys():
            spnl_ = trade['ExitPnL']
            if 'ExitPrice2' in trade.keys():
                spnl_ = spnl_ + trade['ExitPnL2']
        trade['realizedPnL'] = spnl_
        totalPnL+=spnl_
        trade['cumuRealizedPnL']=totalPnL
    
    param['trade_table'] = trade_table
    
    
    
    '''
    try:
        dftrade = pd.DataFrame(trade_table)
        c1 = ['symbol','EntryDateTime','EntryPrice','EntryPosition','EntryHoldingValue','EntryMessage',
                           'ExitDateTime','ExitPrice','ExitPosition','ExitHoldingValue','ExitMessage','ExitPnL']
        #print(type(list(dftrade.columns)),list(dftrade.columns))
        if 'ExitDateTime2' in list(dftrade.columns):
            c1=c1+['ExitDateTime2','ExitPrice2','ExitPosition2','ExitHoldingValue2','ExitMessage2','ExitPnL2']
        c1 = c1+['remaining_position']
        #print(c1)
        dftrade = dftrade[c1]
        #display(dftrade)
        dftrade.to_csv('TradeTable.csv')
    except Exception as e:
        traceback.print_exc()
    '''
    return
    

def calc_universal_profit():
    if 'profit' in globalvar.g_universalparam.keys():
        return globalvar.g_universalparam['profit']
    else:
        return 0


def calc_runtime_summary(param):
    profit = globalvar.g_universalparam['profit']
    
    variable_list = ["LIVE PNL"]
    value_list = [profit]
    
    df = param['runtime_summary_w'].data
    
    try:
        maxpnl = df.loc[df['Variable'] == 'MaxPnL', 'Value'].values[0]
        maxpnl = max(maxpnl, profit)
        variable_list.append('MaxPnL')
        value_list.append(maxpnl)
    except Exception as e:
        #print(e)
        variable_list.append('MaxPnL')
        value_list.append(profit)

    try:
        minpnl = df.loc[df['Variable'] == 'MinPnL', 'Value'].values[0]
        minpnl = min(minpnl, profit)
        variable_list.append('MinPnL')
        value_list.append(minpnl)
    except Exception as e:
        #print(e)
        variable_list.append('MinPnL')
        value_list.append(profit)


    try:
        shv = 0.0
        if 'trade_table' in param.keys():
            trade_table = param['trade_table']
            for trade in trade_table:
                hv = trade['EntryHoldingValue']
                rpos = trade['remaining_position']
                if rpos>0: shv += hv
        variable_list.append('FundUtilized')
        value_list.append(shv)
    except Exception as e:
        #print(e)
        variable_list.append('FundUtilized')
        value_list.append(0.0)

    try:
        fundu = shv #df.loc[df['Variable'] == 'FundUtilized', 'Value'].values[0]
        maxfundu = df.loc[df['Variable'] == 'MaxFundUtilized', 'Value'].values[0]
        maxfundu = max(maxfundu, fundu)
        variable_list.append('MaxFundUtilized')
        value_list.append(maxfundu)
    except Exception as e:
        #print(e)
        variable_list.append('MaxFundUtilized')
        value_list.append(0.0)

    try:
        pnlpercent = round(100*(profit/maxfundu),2)
        variable_list.append('PnLPercent')
        value_list.append(pnlpercent)
    except Exception as e:
        #print(e)
        variable_list.append('PnLPercent')
        value_list.append(0.0)


    try:
        maxpnlpercent = round(100*(maxpnl/maxfundu),2)
        variable_list.append('MaxPnLPercent')
        value_list.append(maxpnlpercent)
    except Exception as e:
        #print(e)
        variable_list.append('MaxPnLPercent')
        value_list.append(0.0)

    
    r = {"Variable":variable_list, "Value":value_list}
    dfr = pd.DataFrame(r)
    param['runtime_summary_w'].data = dfr


#END
    