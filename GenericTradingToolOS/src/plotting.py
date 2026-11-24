"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import datetime
import time
from decimal import Decimal
import numpy as np
import pandas as pd
import requests
from datetime import date,timedelta
#import simplejson as json
import os
import os.path
import inspect

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
        
        
def plot_backtest_charts(portfolio=None, symbol='AAPL', timeframe='minute', frequency='1', periodType='day', period='2', params=None, tradeDirection="LONG", extended_hours=False, candles_dict=None, indicator_list=None, portfolio_dict=None):
    if candles_dict is None:
        return
    
    if extended_hours==True:
        needExtendedHoursData = 'true'
    else:
        needExtendedHoursData = 'false'
    
    
    security = portfolio_dict[portfolio][symbol]
    signal = security['signal']
    dfsig = pd.DataFrame(signal)
    
    
    print('PLOT: ',portfolio)
    print(indicator_list)
    
    '''
    for symbol in symbols:    
        candles = candles_dict[symbol]
        for index,candle in enumerate(candles):
            if index==0:
                candle['Long'] = False
                candle['CloseLong'] = False
                candle['Short'] = False
                candle['CloseShort'] = False
                continue
            p1 = candles[index-1]
            candle['Long'] = candle[portfolio+'trade_in']==1 and p1[portfolio+'trade_in']==0
            candle['LongPrice'] = candle[portfolio+'entryprice']
            
            candle['CloseLong'] = candle[portfolio+'trade_in']<p1[portfolio+'trade_in'] and p1[portfolio+'trade_in']>0
            candle['CloseLongPrice'] = candle[portfolio+'exitprice']
            
            candle['Short'] = candle[portfolio+'trade_in']==-1 and p1[portfolio+'trade_in']==0
            candle['ShortPrice'] = candle[portfolio+'entryprice']
            
            candle['CloseShort'] = candle[portfolio+'trade_in']>p1[portfolio+'trade_in'] and p1[portfolio+'trade_in']<0
            candle['CloseShortPrice'] = candle[portfolio+'exitprice']
    '''
    
    df = pd.DataFrame(candles_dict[symbol])

    #remove 0.0 close price
    df= df[df['close'] != 0.0]

    df.index = df['datetime']

    # --------Creating required data in new DataFrame OHLC----------------------------


    df['date'] = df.index

    #print(df.index)



    df["date"] = df["date"].apply(mdates.date2num)

    ohlc= df[['date', 'open', 'high', 'low','close']].copy()



    dates = ohlc['date'].copy()
    N = len(dates)
    ind = np.arange(N)  # the evenly spaced plot indices
    #fmt = "%d/%m/%y %H:%M"
    #def format_date(index, pos=None):
    #    thisind = np.clip(int(index + 0.5), 0, N - 1)
    #    return dates[thisind].strftime(fmt)        
    class MyFormatter(Formatter):
        def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
            self.dates = dates
            self.fmt = fmt

        def __call__(self, x, pos=0):
            'Return the label for time x at position pos'
            ind = int(np.round(x))
            if ind >= len(self.dates) or ind < 0:
                return ''

            return num2date(self.dates[ind]).strftime(self.fmt)

    formatter = MyFormatter(dates)        


    #--------------------plotly------------------------------------------------------

    data = []

    df['dates'] = df.index

    traceOHLC = go.Candlestick(x=df['dates'].astype(str), open=ohlc['open'], high=ohlc['high'], low=ohlc['low'], close=ohlc['close'], 
                              opacity=0.5, name='Prices')
    data.append(traceOHLC)


    chart_title = portfolio+"-"+symbol

    layout = go.Layout(
        title=chart_title,
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


    color_list = ['rgba(255, 0, 0, .6)','rgba(0, 255, 0, .6)','rgba(0, 0 , 255, .6)',\
                  'rgba(255, 69, 0, .6)','rgba(255, 0, 255, .6)','rgba(0, 255, 255, .6)']


    ''' line indicators '''
    k=0
    for indicator in indicator_list:
        k=k%6
        if indicator[1]!='line':continue
        indicatorvalues = df[indicator[0]].tolist()
        #dash = indicator_style_list[k]
        
        if 'avgHullMA' in indicator[0]:
            df['avgHullMA_up'] = df[df['HullTrend']==1]['avgHullMA'].replace(0,float('nan'))
            indicatorvalues = df['avgHullMA_up'].tolist()
            trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'lines', 
                               line=dict(color='rgba(0, 0, 255, .6)'), name = indicator[0])
            data.append(trace)
            
            df['avgHullMA_down'] = df[df['HullTrend']==-1]['avgHullMA'].replace(0,float('nan'))
            indicatorvalues = df['avgHullMA_down'].tolist()
            trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'lines', 
                               line=dict(color='rgba(255, 0, 0, .6)'), name = indicator[0])
            data.append(trace)
        
        
        elif 'halftrend' in indicator[0]:
            #df['halftrend_color'] = df['up']>0
            #colorsIdx = {True: 'rgb(215,48,39)', False: 'rgb(215,148,39)'}
            #colline      = df['halftrend_color'].map(colorsIdx)
            df['halftrend_up'] = df[df['up']>0]['halftrend'].replace(0,float('nan'))
            indicatorvalues = df['halftrend_up'].tolist()
            trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'lines', 
                               line=dict(color='rgba(0, 255, 0, .6)'), name = indicator[0])
            data.append(trace)
            
            df['halftrend_down'] = df[~(df['up']>0)]['halftrend'].replace(0,float('nan'))
            indicatorvalues = df['halftrend_down'].tolist()
            trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'lines', 
                               line=dict(color='rgba(255, 0, 0, .6)'), name = indicator[0])
            data.append(trace)
            
        else:
            trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'lines', 
                               line = dict(color = color_list[k],), name = indicator[0])
            data.append(trace)
        
        
        
        k+=1


    
    ''' dash indicators'''    
    k=0
    for indicator in indicator_list:
        k=k%6

        clr = color_list[k]
        if 'takeprofit' in indicator[0]: clr = 'rgba(0, 255, 0, .6)'
        elif 'stoploss' in indicator[0]: clr = 'rgba(255, 0, 0, .6)'
        

        if indicator[1]!='dash':continue
        
        try:
            indicatorvalues = df[indicator[0]].tolist()
            indicatorvalues = [float("nan") if v==0 else v for v in indicatorvalues]
        except:
            continue
        
        #dash = indicator_style_list[k]
        trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'lines', 
                               line = {'color':clr,'dash':'dash','width':1.0}, name = indicator[0])
        data.append(trace)
        k+=1

    
    
    ''' markers indicators'''    
    k=0
    for indicator in indicator_list:
        k=k%6

        clr = color_list[k]

        if indicator[1]!='markers':continue
        
        try:
            indicatorvalues = df[indicator[0]].tolist()
            indicatorvalues = [float("nan") if v==0 else v for v in indicatorvalues]
        except:
            continue
        
        
        if 'MC_P' in indicator[0]:
            df['MC_P_color'] = df['MC_P']>0
            colorsIdx = {True: 'rgb(0,255,0)', False: 'rgb(255,0,0)'}#{True: 'rgb(215,48,39)', False: 'rgb(215,148,39)'}
            colmarker      = df['MC_P_color'].map(colorsIdx)
            #df['MC_P_color'] = color_list[0] if df['MC_P_dir'] else color_list[1]
            #colmarker = df['MC_P_color'].tolist()
        
            trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'markers', 
                               marker=dict(size=5, color=colmarker), name = 'emacross')#indicator[0])
            data.append(trace)
        
        
        istr = 'MT1_TF'
        if istr in indicator[0]:
            df[istr+'_color'] = df[istr]>0
            colorsIdx = {True: 'rgb(0,255,0)', False: 'rgb(255,0,0)'}
            colmarker      = df[istr+'_color'].map(colorsIdx)
            #df['MC_P_color'] = color_list[0] if df['MC_P_dir'] else color_list[1]
            #colmarker = df['MC_P_color'].tolist()
        
            trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'markers',marker_symbol=1, 
                               marker=dict(size=5, color=colmarker), name = 'cciatr')#indicator[0])
            data.append(trace)
        
        
        
        istr = 'PSAR_TF'
        if istr in indicator[0]:
            df[istr+'_color'] = df[istr]
            colorsIdx = {1: 'rgb(0,255,0)', -1: 'rgb(255,0,0)', 0: 'rgb(255,255,0)'}
            colmarker      = df[istr+'_color'].map(colorsIdx)
            #df['MC_P_color'] = color_list[0] if df['MC_P_dir'] else color_list[1]
            #colmarker = df['MC_P_color'].tolist()
        
            trace = go.Scatter(x = df['dates'].astype(str), y = indicatorvalues, mode = 'markers', marker_symbol=2,
                               marker=dict(size=5, color=colmarker), name = 'trendema')#indicator[0])
            data.append(trace)
            
       
        
        
        k+=1


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


    try:
        if 'Short' in dfsig.columns:
            traceShort = go.Scatter(
                x = dfsig.loc[dfsig['Short'] == True , 'datetime'].astype(str),
                y = dfsig.loc[dfsig['Short'] ==True, 'ShortPrice'].values.tolist(),
                text=dfsig.loc[dfsig['Short'] == True , 'position'].astype(str),
                textposition='top center',
                mode = 'markers+text',
                marker={'color': 'rgba(255, 0, 0, .8)', 'symbol': 'triangle-down', 'size': arrowSize},
                name = 'Short'
                )
            data.append(traceShort)
    except:
        pass


    try:
        if 'CloseShort' in dfsig.columns:
            traceCloseShort = go.Scatter(
                x = dfsig.loc[dfsig['CloseShort'] == True , 'datetime'].astype(str),
                y = dfsig.loc[dfsig['CloseShort'] ==True, 'CloseShortPrice'].values.tolist(),
                text=dfsig.loc[dfsig['CloseShort'] == True , 'position'].astype(str),
                textposition='top center',
                mode = 'markers+text',
                marker={'color': 'rgba(0, 0, 0, .8)', 'symbol': 'triangle-up', 'size': arrowSize},
                name = 'CloseShort'
                ) 
            data.append(traceCloseShort)
    except:
        pass
    

    fig = go.Figure(data=data, layout=layout)        
    #fig.update_traces(textposition='top center')
    plot(fig, show_link = True, filename = './plots/'+portfolio+'-'+symbol+'.html')



    plt.show(block=False)
    return fig