"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import math
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
from scipy.stats import norm

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__



    
def lindev(candles=None, index=0, key=None, period=20):
    if index<period-1:
        return 0.0
    
    sum_=0.0
    for i in range(period):
        sum_ = sum_ + candles[index+i+1-period][key]
    
    mean = sum_/period
    
    var = 0.0
    for i in range(period):
        var = var +  abs(candles[index+i+1-period][key] - mean)
    
    ldv = var/period
    return ldv    
    
    
    
def stddev(candles=None, index=0, key=None, period=20):
    if index<period-1:
        return 0.0
    
    sum_=0.0
    for i in range(period):
        sum_ = sum_ + candles[index+i+1-period][key]
    
    mean = sum_/period
    
    var = 0.0
    for i in range(period):
        var = var +  ((candles[index+i+1-period][key] - mean)**2)
    
    std = math.sqrt(var/period)
    return std
    
    

def LogReturns(M=None):
    return np.log(M / M.shift(1))


def SMA(M=None, period=20):
    sma = M.rolling(period,min_periods=1).mean().rename("Simple Moving Average("+str(period)+")")
    return sma


def SMACandle(S, index, period):
    if index<period-1:
        return S.values[-1]
        
    arr = np.array(S)
    sum_=0.0
    for i in range(period):
        sum_ = sum_ + arr[index+i+1-period]
    return sum_/period


def SMACandleKey(candles, index, period, key):
    if index<period-1:
        return candles[index][key]
        
    #arr = np.array(S)
    sum_=0.0
    for i in range(period):
        sum_ = sum_ + candles[index+i+1-period][key]
    return sum_/period


def EMA(M=None, period=20):
    return M.ewm(span=period).mean().rename("Exponential Moving Average("+str(period)+")")    


def EMACandle(S, index, period):
    if index<period-1:
        return S.values[-1]
    
    fac = 2.0/(period+1)
    
    arr = np.array(S)
    
    ema = fac*arr[index] + (1-fac)*arr[index-1]
    
    return ema


    
def EMACandleKey(candles, index, period, key):
    if index<period-1:
        return candles[index][key]
    
    fac = 2.0/(period+1)
    
    #arr = np.array(S)
    
    candles[index]['EMA'] = fac*candles[index][key] + (1-fac)*candles[index-1]['EMA']
    
    return candles[index]['EMA']


def EMAKeyCandleKey(candles, index, period, key, emakey):
    if index<1:#period-1:
        candles[index][emakey] = candles[index][key] 
        return candles[index][emakey]
    
    fac = 2.0/(period+1)
    
    #arr = np.array(S)
    
    candles[index][emakey] = fac*candles[index][key] + (1-fac)*candles[index-1][emakey]
    
    return candles[index][emakey]


def RMAKeyCandleKey(candles, index, period, key, emakey):
    if index<1:#period-1:
        return candles[index][key]
    
    fac = 1.0/(period)
    
    #arr = np.array(S)
    
    candles[index][emakey] = fac*candles[index][key] + (1-fac)*candles[index-1][emakey]
    
    return candles[index][emakey]



def EMAIndexKeyCandleKey(candles, previndex, index, period, key, emakey):
    if index<period-1 or previndex < 1:
        return candles[index][key]
    
    fac = 2.0/(period+1)
    
    #arr = np.array(S)
    
    candles[index][emakey] = fac*candles[index][key] + (1-fac)*candles[previndex][emakey]
    
    return candles[index][emakey]



def RSI(M=None, period=14):
    delta = M.diff()
    delta.iloc[0] = 0
    #print("delta shape=",delta.shape)
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.ewm(span=period).mean()
    roll_down = down.abs().ewm(span=period).mean()
    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))
    return RSI.rename("Relative Strength Index("+str(period)+")")


def Volatility(M=None):
    log_ret = np.log(M / M.shift(1))
    #log_ret = self.C.pct_change()
    vol = log_ret.rolling(252).std() * np.sqrt(252)
    return vol.rename("Annualized Volatility")


def ADX(H=None, L=None, C=None, period = 14):
    UpMove = H - H.shift(1)
    DoMove = L.shift(1) - L
    UpD = pd.Series(UpMove)
    DoD = pd.Series(DoMove)
    UpD[(UpMove<=DoMove)|(UpMove <= 0)] = 0
    DoD[(DoMove<=UpMove)|(DoMove <= 0)] = 0
    hll = H-L
    hlpc = abs(H-C.shift(1))
    llpc = abs(L-C.shift(1))
    tr = np.maximum(hll , hlpc)
    tr = np.maximum(tr , llpc)            
    ATR = tr.rolling(period).mean()       
    PosDI = (UpD.ewm(span = period).mean()).divide(ATR)
    NegDI = (DoD.ewm(span = period).mean()).divide(ATR)
    DX = 100 * (PosDI - NegDI) / (PosDI + NegDI) 
    DX = abs(DX)
    ADX = DX.ewm(span = period).mean().rename("ATR("+str(period)+")")
    return ADX


def BollingerBand(M=None, period=20):
    middle_band = M.rolling(period,min_periods=1).mean().rename("Bolliner Middle Band("+str(period)+")")
    std =  M.rolling(min_periods=period, window=period, center=False).std()
    upper_band = (middle_band + (std * 2)).rename("Bolliner Upper Band("+str(period)+")")
    lower_band = (middle_band - (std * 2)).rename("Bolliner Lower Band("+str(period)+")")
    return middle_band, upper_band, lower_band


def MACD(M=None, periodEMA1=26, periodEMA2=12, periodSignal=9):
    ema1 = M.ewm(span=periodEMA1).mean()
    ema2 = M.ewm(span=periodEMA2).mean()
    MACD = ema1 - ema2
    Signal = MACD.ewm(span=periodSignal).mean()
    return MACD.rename("MACD"),Signal.rename("Signal")


def Ichimoku(data=None, tenkan=9, kijun=26, senkou=52, senkou_lead=26, chikou=26):
    if data is None: return None
    hi_tenkan = data.high.rolling(tenkan,min_periods=1).max()
    lo_tenkan = data.low.rolling(tenkan,min_periods=1).min()
    tenkan_sen = (hi_tenkan + lo_tenkan) / 2.0
    
    hi_kijun = data.high.rolling(kijun,min_periods=1).max()
    lo_kijun = data.low.rolling(kijun,min_periods=1).min()
    kijun_sen = (hi_kijun + lo_kijun) / 2.0
    
    senkou_span_a_pre = (tenkan_sen + kijun_sen) / 2.0
    senkou_span_a = senkou_span_a_pre.shift(senkou_lead)

    hi_senkou = data.high.rolling(senkou,min_periods=1).max()
    lo_senkou = data.low.rolling(senkou,min_periods=1).min()
    senkou_span_b_pre = (hi_senkou + lo_senkou) / 2.0
        
    senkou_span_b = senkou_span_b_pre.shift(senkou_lead)

    chikou_span = data.close.shift(-chikou)
    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

def PSAR(barsdata, iaf = 0.02, maxaf = 0.2):
    length = len(barsdata)
    price = barsdata['close']
    
    high = list(barsdata['high'])
    low = list(barsdata['low'])
    close = list(barsdata['close'])
    
    
    psar = close[0:len(close)]
    psarbull = [None] * length
    psarbear = [None] * length
    bull = True
    af = iaf
    ep = low[0]
    hp = high[0]
    lp = low[0]
    for i in range(2,length):
        if bull:
            psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
        else:
            psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
        reverse = False
        if bull:
            if low[i] < psar[i]:
                bull = False
                reverse = True
                psar[i] = hp
                lp = low[i]
                af = iaf
        else:
            if high[i] > psar[i]:
                bull = True
                reverse = True
                psar[i] = lp
                hp = high[i]
                af = iaf
        if not reverse:
            if bull:
                if high[i] > hp:
                    hp = high[i]
                    af = min(af + iaf, maxaf)
                if low[i - 1] < psar[i]:
                    psar[i] = low[i - 1]
                if low[i - 2] < psar[i]:
                    psar[i] = low[i - 2]
            else:
                if low[i] < lp:
                    lp = low[i]
                    af = min(af + iaf, maxaf)
                if high[i - 1] > psar[i]:
                    psar[i] = high[i - 1]
                if high[i - 2] > psar[i]:
                    psar[i] = high[i - 2]
        if bull:
            psarbull[i] = psar[i]
        else:
            psarbear[i] = psar[i]
    a = pd.Series(psar, index=price.index)
    b = pd.Series(psarbear, index=price.index)
    c = pd.Series(psarbull, index=price.index)
    return a, b, c




def calc_atr(candles, index, period):
    candle = candles[index]
    
    if index<period-1:
        candle['tr'] = candle['high'] - candle['low']
        candle['atr'] = candle['high'] - candle['low']
        return candle['atr']
        
    prev = candles[index-1]
    
    a = candle['high'] - candle['low']
    b = abs(candle['high'] - prev['close'])
    c = abs(candle['low'] - prev['close'])

    tr = max(a,max(b,c))
    candle['tr'] = tr

    '''
    sum_=0.0
    for i in range(period):
        sum_ = sum_ + candles[index+i+1-period]['tr']
    
    candle['atr'] = sum_/period    
    '''
    candle['atr'] = RMAKeyCandleKey(candles, index, period, 'tr', 'atr')
    return candle['atr']


def ATR(high, low, close, n=14, fillna=False, averageType='simple'):
    """Average True Range (ATR)
    The indicator provide an indication of the degree of price volatility.
    Strong moves, in either direction, are often accompanied by large ranges,
    or large True Ranges.
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_true_range_atr
    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        n(int): n period.
    Returns:
        pandas.Series: New feature generated.
    """
    cs = close.shift(1)
    TR = high.combine(cs, max) - low.combine(cs, min)
    
    
    
    '''
    ATR = np.zeros(len(close))
    atr[0] = tr[1::].mean()
    for i in range(1, len(atr)):
        atr[i] = (atr[i-1] * (n-1) + tr.iloc[i]) / float(n)

    atr = pd.Series(data=atr, index=tr.index)
    '''
    
    ATRPeriod = n
    if averageType=='wilders':
        ATR = TR.ewm(alpha=1/ATRPeriod).mean()
    elif averageType=='simple':
        ATR = TR.rolling(ATRPeriod).mean()
    else:
        ATR = TR.ewm(span=ATRPeriod).mean()
    
    
    if fillna:
        ATR = ATR.replace([np.inf, -np.inf], np.nan).fillna(0)

    return pd.Series(ATR, name='atr')







def KeltnerChannel(barsdata=None, period=20, factor=1.5):
    high = barsdata['high']
    low = barsdata['low']
    close = barsdata['close']
    
    atr =  ATR(high, low, close, n=period, fillna=False)
        
    middle_band = close.rolling(period,min_periods=1).mean().rename("Keltner Middle Band("+str(period)+")")
    upper_band = (middle_band + (atr * factor)).rename("Keltner Upper Band("+str(period)+")")
    lower_band = (middle_band - (atr * factor)).rename("Keltner Lower Band("+str(period)+")")
    
    return middle_band, upper_band, lower_band








def KAMA(price, effRatioLength=10, fastLength=2, slowLength=30):
    #input price = close;
    #input fastLength = 2;
    #input slowLength = 30;
    #input effRatioLength = 10;
    ''' kama indicator '''    
    ''' accepts pandas dataframe of prices '''
    n = effRatioLength
    pow1 = fastLength
    pow2 = slowLength
    
    

    ER_num = abs( price - price.shift(n) )
    
    absDiffx = abs(price - price.shift(1) )  
    ER_den = absDiffx.rolling(n).sum()
    
    ER = ER_num / ER_den

    sc = ( ER*(2.0/(pow1+1)-2.0/(pow2+1.0))+2/(pow2+1.0) ) ** 2.0


    answer = np.zeros(sc.size)
    N = len(answer)
    first_value = True

    for i in range(N):
        if sc[i] != sc[i]:
            answer[i] = np.nan
        else:
            if first_value:
                answer[i] = price[i]
                first_value = False
            else:
                answer[i] = answer[i-1] + sc[i] * (price[i] - answer[i-1])
    return pd.Series(answer, index=price.index)



def ATRTrailingStop(df, ATRPeriod=5, ATRFactor=3.5, trailType="modified", firstTrade='long', averageType='wilders'):
    C = df['close']
    H = df['high']
    L = df['low']
    
    
    if trailType=="modified":
        HiLoref = 1.5*(H-L).rolling(ATRPeriod).sum()
        HiminusLo = H-L 
        HiLo = HiminusLo.combine(HiLoref, min)
    
        HRefpre = np.where( L<=H.shift(1), H-C.shift(1), (H - C.shift(1)) - 0.5 * (L - H.shift(1)) )
        HRef = pd.Series(HRefpre, index=C.index)
    
        LRefpre =np.where( H>=L.shift(1), C.shift(1)-L, (C.shift(1) - L) - 0.5 * (L.shift(1) - H) )
        LRef = pd.Series(LRefpre, index=C.index)
    
        TRpre = HRef.combine(LRef,max)
        TR = TRpre.combine(HiLo, max)
    else:
        CS = C.shift(1)
        TR = H.combine(CS, max) - L.combine(CS, min)
    
    
    if averageType=='wilders':
        ATR = TR.ewm(alpha=1/ATRPeriod).mean()
    elif averageType=='simple':
        ATR = TR.rolling(ATRPeriod).mean()
    else:
        ATR = TR.ewm(span=ATRPeriod).mean()
    
    loss = ATRFactor * ATR
    
    Clist = list(C)
    losslist = list(loss)
    statelist = [1]*len(df)
    traillist = [0]*len(df)
    
    for i in range(len(df)):
        if i==0:
            statelist[i] = 0
            traillist[i] = float('nan')
            continue        
        
        if statelist[i-1] == 0 and math.isnan(losslist[i]):
            statelist[i] = 0
            traillist[i] = float('nan')            
            
        if statelist[i-1] == 0 and not math.isnan(losslist[i]):
            statelist[i] = 1
            traillist[i] = Clist[i] - losslist[i]
            
        
        if statelist[i-1] == 1 and Clist[i] > traillist[i-1]:
            statelist[i] = 1
            traillist[i] = max(traillist[i-1], Clist[i] - losslist[i])
        
        elif statelist[i-1] == 1 and Clist[i] <= traillist[i-1]:
            statelist[i] = -1
            traillist[i] = Clist[i] + losslist[i]
        
        elif statelist[i-1] == -1 and Clist[i] < traillist[i-1]:
            statelist[i] = -1
            traillist[i] = min(traillist[i-1], Clist[i] + losslist[i])
        
        elif statelist[i-1] == -1 and Clist[i] >= traillist[i-1]:
            statelist[i] = 1
            traillist[i] = Clist[i] - losslist[i]
    
    return pd.Series(traillist, index=C.index)
                



def WMA(C=None, Period=200):
    def f(N):
        w =  np.arange(1,N+1)
        def g(x):
            return (w*x).sum() / w.sum()
        return g
    return C.rolling(window=Period).apply(f(Period))



def WMACandleKey(candles, index, Period, key):
    if index<Period-1:
        return candles[index][key]
    
    w =  np.arange(1,Period+1)
    wsum = w.sum()
    sum_=0.0
    for i in range(Period):
        sum_ +=  w[i]*candles[index+i+1-Period][key] 
    wma = sum_/wsum
    return wma

def HullMACandleKey(candles, index, Period, key):
    #if index<Period-1:    
    #    return candles[index][key]
    
    candle = candles[index]
    candle['wma'+str(Period)] = WMACandleKey(candles, index, Period, key)
    candle['wma'+str(Period)+'bytwo'] = WMACandleKey(candles, index, int(Period/2), key)
    candle['hullpre'+str(Period)] = 2*candle['wma'+str(Period)+'bytwo'] - candle['wma'+str(Period)]
    candle['hullMA'+str(Period)] = WMACandleKey(candles, index, int(math.sqrt(Period)), 'hullpre'+str(Period))
    return candle['hullMA'+str(Period)]
    #return WMA(2*WMA(C, int(Period/2)) - WMA(C, Period), int(math.sqrt(Period)))


def HullMA(C = None, Period=200):
    return WMA(2*WMA(C, int(Period/2)) - WMA(C, Period), int(math.sqrt(Period)))


'''
def HullMACandle(C, index, period):
    def ma(C, N):
        w =  np.arange(1,N+1)
        return (w*C).sum() / w.sum()
    return ma(2*ma(S, int(period/2)) - ma(S, period), int(math.sqrt(period)))
'''




'''dictionary based calculations of volatility'''
def calc_volatility(candles=None, i=0):
    if i<252: return 0.0
    summ = 0.0
    for k in range(i-251,i+1):
        c0 = candles[k]['close']
        c1 = candles[k-1]['close']
        try:
            log_ret = np.log(c0) - np.log(c1)
        except:
            log_ret=0.0
        summ = summ+log_ret
    avg = summ/252    
    
    summ2=0.0
    for k in range(i-251,i+1):
        c0 = candles[k]['close']
        c1 = candles[k-1]['close']
        try:
            log_ret = np.log(c0) - np.log(c1)
        except:
            log_ret=0.0
        summ2 = (log_ret-avg)*(log_ret-avg)
    std_ = summ2/252 
    std = np.sqrt(std_) * np.sqrt(252)
    return std


'''dictionary based calculations of psar'''
def calc_psar(candles=None, i=0, iaf = 0.02, maxaf = 0.2):
    target = candles[i]
    
    if i<2:
        target['psar'] = target['close']
        target['psarbull'] = 1
        target['hp'] = target['high']
        target['low'] = target['low']
        target['af'] = iaf
        return
    
    previous = candles[i-1]
    p2 = candles[i-2] 
    
    af = previous['af']
    bull = previous['psarbull']
    hp = previous['hp']
    lp = previous['lp']
    
    if bull==1:
        target['psar'] = previous['psar'] + af * (hp - previous['psar'])
    else:
        target['psar'] = previous['psar'] + af * (lp - previous['psar'])
    
    reverse = False
    
    if bull==1:
        if target['low'] < target['psar']:
            target['psarbull'] = 0
            reverse = True
            target['psar'] = hp
            target['lp'] = target['low']
            target['hp'] = previous['hp']
            target['af'] = iaf
    else:
        if target['high'] > target['psar']:
            target['psarbull'] = 1
            reverse = True
            target['psar'] = lp
            target['hp'] = target['high']
            target['lp'] = previous['lp']
            target['af'] = iaf
    
    if not reverse:
        if bull==1:
            if target['high'] > hp:
                target['hp'] = target['high']
                target['af'] = min(af + iaf, maxaf)
            if previous['low'] < target['psar']:
                target['psar'] = previous['low']
            if p2['low'] < target['psar']:
                target['psar'] = p2['low']
        else:
            if target['low'] < lp:
                target['lp'] = target['low']
                target['af'] = min(af + iaf, maxaf)
            if previous['high'] > target['psar']:
                target['psar'] = previous['high']
            if p2['high'] > target['psar']:
                target['psar'] = p2['high']
    
    if target['hp']==0: target['hp'] = previous['hp']
    if target['lp']==0: target['lp'] = previous['lp']
    if target['af']==0: target['af'] = previous['af']    
    if target['psar']==0: target['psar'] = previous['psar']
    if target['psarbull']==-1: target['psarbull'] = previous['psarbull']   
    
    return





def stochfull(df=None, kperiod=14, index=0):
    if index+1<kperiod: return 0
    size = index+1
    
    array_close = np.array(df['close'])
    array_high = np.array(df['high'])
    array_low = np.array(df['low'])
    
    kmax=array_high[size-kperiod]
    for x in range(size-kperiod,size):
        kmax=max(kmax,array_high[x])
    
    kmin=array_low[size-kperiod]
    for x in range(size-kperiod,size):
        kmin=min(kmin,array_low[x])    
    
    c1 = array_close[size-1] - kmin
    c2 = kmax - kmin
    K = c1 / c2 * 100 if c2 != 0 else 0
    return K



def vwapweek(candles, index):
    candle = candles[index]
    
    if index < 1:
        candle['cumvolume'] = candle['volume']
        candle['vwap'] = candle['close']
        return candle['vwap']
    
    previous = candles[index-1]
    
    #print(candle['datetime'], type(candle['datetime']))
    #print(candle['datetime'].date())
    #print(candle['datetime'].date().weekday())
          
          
    w0=candle['datetime'].date().weekday()
    w1=previous['datetime'].date().weekday()
    
    if  w0 == 0 and w1==6:
        candle['cumvolume'] = candle['volume']
        candle['vwap'] = candle['close']
    else:
        candle['cumvolume'] = previous['cumvolume'] + candle['volume']
        if candle['cumvolume']==0:
            candle['vwap'] = candle['close']
        else:
            candle['vwap'] = (previous['vwap']*previous['cumvolume'] + candle['close']*candle['volume'])/candle['cumvolume']
            
    return candle['vwap']        
    
    

    
    
def vwapday(candles, index):
    #print('index:',index)
    candle = candles[index]
    
    candle['typical_price'] = (candle['high']+candle['low']+candle['close'])/3
    
    if index < 1:
        candle['cumvolume'] = candle['volume']
        candle['vwapday'] = candle['typical_price']
        return candle['vwapday']
    
    previous = candles[index-1]
          
          
    w0=candle['datetime'].date().weekday()
    w1=previous['datetime'].date().weekday()
    
    if  w0 != w1:
        candle['cumvolume'] = candle['volume']
        candle['vwapday'] = candle['typical_price']
    else:
        try:
            candle['cumvolume'] = previous['cumvolume'] + candle['volume']
        except:
            print(previous)
        
        if candle['cumvolume']==0:
            candle['vwapday'] = previous['vwapday']
        else:
            candle['vwapday'] = (previous['vwapday']*previous['cumvolume'] + candle['typical_price']*candle['volume'])/candle['cumvolume']
            
    return candle['vwapday']      
    
    
def vwapdaykey(candles, index, key):
    #print('index:',index)
    candle = candles[index]
    
    if index < 1:
        candle[key+'_cumvolume'] = candle[key+'_volume']
        candle[key+'_vwapday'] = candle[key+'_average']
        return candle[key+'_vwapday']
    
    previous = candles[index-1]
    
    
    #print(previous)
    
    #print(candle['datetime'], type(candle['datetime']))
    #print(candle['datetime'].date())
    #print(candle['datetime'].date().weekday())
          
          
    w0=candle['datetime'].date().weekday()
    w1=previous['datetime'].date().weekday()
    
    if  w0 != w1:
        candle[key+'_cumvolume'] = candle[key+'_volume']
        candle[key+'_vwapday'] = candle[key+'_average']
    else:
        
        try:
            candle[key+'_cumvolume'] = previous[key+'_cumvolume'] + candle[key+'_volume']
        except:
            print(previous)
        
        if candle[key+'_cumvolume']==0:
            candle[key+'_vwapday'] = previous[key+'_vwapday']
        else:
            candle[key+'_vwapday'] = (previous[key+'_vwapday']*previous[key+'_cumvolume'] + candle[key+'_average']*candle[key+'_volume'])/candle[key+'_cumvolume']
            
    return candle[key+'_vwapday']      




    
    

def getDailyData(df):
    df['openDay']=df['open']
    df['highDay']=df['high']
    df['lowDay']=df['low']
    #df['closeDay']=df['close']
    fcn = lambda x: x.date().day
    df['Date']=df['datetime'].map(fcn)
    for index, row in df.iterrows():
        if index==0:
            #df.at[index,'openDay']=row['open']
            prev=row
            continue
        if row['Date']!=prev['Date']:
            df.at[index,'openDay'] = row['open']
            df.at[index,'highDay'] = row['high']
            df.at[index,'lowDay'] = row['low']

        else:
            df.at[index,'openDay'] = prev['openDay']
            df.at[index,'highDay'] = max(prev['highDay'],row['high'])
            df.at[index,'lowDay'] = min(prev['lowDay'],row['low'])                     
        prev=df.iloc[index]                  
    return df



def getDailyDataOnCandle(candles, index):
    candle = candles[index]
    
    if index<1:
        candle['openDay'] = candle['open']
        candle['highDay'] = candle['high']
        candle['lowDay'] = candle['low']
        return
    
    #candle = candles[index]
    previous = candles[index-1]
    
    #print(candle['datetime'].date().day)
    #print(previous['datetime'].date().day)
    #print(previous['openDay'])
    
    if candle['datetime'].date().day != previous['datetime'].date().day:
        candle['openDay'] = candle['open']
        candle['highDay'] = candle['high']
        candle['lowDay'] = candle['low']
    else:
        candle['openDay'] =  previous['openDay']
        candle['highDay'] =  max(previous['highDay'], candle['high'])
        candle['lowDay'] =  min(previous['lowDay'], candle['low'])
    
    return





def stochfullCandle(candles, index, kperiod):
    if index+1<kperiod: return 0
    size = index+1
    
    #array_close = np.array(df['close'])
    #array_high = np.array(df['high'])
    #array_low = np.array(df['low'])
    
    kmax=candles[size-kperiod]['high']
    for x in range(size-kperiod,size):
        kmax=max(kmax,candles[x]['high'])
    
    kmin=candles[size-kperiod]['low']
    for x in range(size-kperiod,size):
        kmin=min(kmin,candles[x]['low'])    
    
    c1 = candles[index]['close'] - kmin
    c2 = kmax - kmin
    K = c1 / c2 * 100 if c2 != 0 else 0
    return K



def vwapweek(candles, index):
    candle = candles[index]
    
    if index < 1:
        candle['cumvolume'] = candle['volume']
        candle['vwap'] = candle['close']
        return candle['vwap']
    
    previous = candles[index-1]
    
    #print(candle['datetime'], type(candle['datetime']))
    #print(candle['datetime'].date())
    #print(candle['datetime'].date().weekday())
          
          
    w0=candle['datetime'].date().weekday()
    w1=previous['datetime'].date().weekday()
    
    #candle['w0'] = w0
    #candle['w1'] = w1
    
    if  w0 == 0 and w1!=0:
        candle['cumvolume'] = candle['volume']
        candle['vwap'] = candle['close']
    else:
        candle['cumvolume'] = previous['cumvolume'] + candle['volume']
        if candle['cumvolume']==0:
            candle['vwap'] = candle['close']
        else:
            candle['vwap'] = (previous['vwap']*previous['cumvolume'] + candle['close']*candle['volume'])/candle['cumvolume']
            
    return candle['vwap']        
    
    
    
def totalvolumeday(candles, index):
    candle = candles[index]
    
    if index < 1:
        candle['totalvolumeday'] = candle['volume']
        return candle['totalvolumeday']
    
    previous = candles[index-1]
    
    #print(candle['datetime'], type(candle['datetime']))
    #print(candle['datetime'].date())
    #print(candle['datetime'].date().weekday())
          
          
    w0=candle['datetime'].date().weekday()
    w1=previous['datetime'].date().weekday()
    
    if  w0 != w1:
        candle['totalvolumeday'] = candle['volume']
    else:
        candle['totalvolumeday'] = previous['totalvolumeday'] + candle['volume']
        
            
    return candle['totalvolumeday']        
    

def firstdayhigh(candles, index):
    candle = candles[index]
    w0=candle['datetime'].date()
    w1=candles[0]['datetime'].date()
    
    if index<1:
        candle['firstdayhigh'] = candle['high']
    elif w0==w1:
        candle['firstdayhigh'] = max(candles[index-1]['firstdayhigh'], candle['high'])
    else:
        candle['firstdayhigh'] = candles[index-1]['firstdayhigh']
    return candle['firstdayhigh']


def firstdaylow(candles, index):
    candle = candles[index]
    w0=candle['datetime'].date()
    w1=candles[0]['datetime'].date()
    
    if index<1:
        candle['firstdaylow'] = candle['low']
    elif w0==w1:
        candle['firstdaylow'] = min(candles[index-1]['firstdaylow'], candle['low'])
    else:
        candle['firstdaylow'] = candles[index-1]['firstdaylow']
    return candle['firstdaylow']


def totalvolumelastday(candles, index):
    candle = candles[index]
    
    if index < 1:
        candle['totalvolumelastday'] = 0
        candle['averagevolumelastday'] = 0
        candle['totalvolumeday'] = candle['volume']
        candle['averagevolumeday'] = candle['volume']
        return candle['totalvolumeday']
    
    previous = candles[index-1]
    
          
    w0=candle['datetime'].date().weekday()
    w1=previous['datetime'].date().weekday()
    
    if  w0 != w1:
        candle['totalvolumelastday'] = previous['totalvolumeday']
        candle['averagevolumelastday'] = candle['totalvolumelastday']/375
        candle['totalvolumeday'] = candle['volume']
        candle['averagevolumeday'] = candle['volume']
    else:
        n = candle['datetime']
        dt = candle['datetime'] - datetime(year=n.year, month=n.month, day=n.day, hour=9,minute=15, tzinfo = n.tzinfo)
        x = dt.total_seconds() / 60
        candle['totalvolumelastday'] = previous['totalvolumelastday']
        candle['averagevolumelastday'] = previous['averagevolumelastday']
        candle['totalvolumeday'] = previous['totalvolumeday'] + candle['volume']
        candle['averagevolumeday'] = candle['totalvolumeday'] / x

    #vN=0
    #for i in range(N):
    #    w0=candles[]['datetime'].date().weekday()
    #    w1=previous['datetime'].date().weekday()
    #candle['totalvolumedaylast'+str(N)]    
    
    return candle['totalvolumelastday']


def totalvolumelasthour(candles, index):
    candle = candles[index]
    
    if index < 1:
        candle['totalvolumelasthour'] = 0
        candle['averagevolumelasthour'] = 0
        candle['totalvolumehour'] = candle['volume']
        candle['averagevolumehour'] = candle['volume']
        return candle['totalvolumehour']
    
    previous = candles[index-1]
    
          
    #w0=candle['datetime'].hour
    #w1=previous['datetime'].hour
    n = candle['datetime']
    hr_ = n.hour
    mn_ = n.minute
    new_hour = mn_==15
    
    if  new_hour:
        candle['totalvolumelasthour'] = previous['totalvolumehour']
        candle['averagevolumelasthour'] = candle['totalvolumelasthour']/60
        candle['totalvolumehour'] = candle['volume']
        candle['averagevolumehour'] = candle['volume']
    else:
        n = candle['datetime']
        hr_ = n.hour
        mn_ = n.minute
        hr = hr_ if mn_>15 else hr_-1
        dt = candle['datetime'] - datetime(year=n.year, month=n.month, day=n.day, hour=hr, minute=15, tzinfo = n.tzinfo)
        x = dt.total_seconds() / 60

        candle['totalvolumelasthour'] = previous['totalvolumelasthour']
        candle['averagevolumelasthour'] = previous['averagevolumelasthour']
        candle['totalvolumehour'] = previous['totalvolumehour'] + candle['volume']
        candle['averagevolumehour'] = candle['totalvolumehour'] / x

    #vN=0
    #for i in range(N):
    #    w0=candles[]['datetime'].date().weekday()
    #    w1=previous['datetime'].date().weekday()
    #candle['totalvolumedaylast'+str(N)]    
    
    return candle['totalvolumelasthour']
    

def CCI(candles, index, period):
    candle = candles[index]
    candle['typical_price'] = (candle['high'] + candle['low'] + candle['close'])
    
    tp = candle['typical_price']
    ma = SMACandleKey(candles, index, period, 'typical_price')
    std = lindev(candles, index , 'typical_price', period)
    
    eps = 0.00000000001
    if std < eps:
        candle['CCI'] = 0.0
    else:    
        candle['CCI'] = (tp - ma) / (0.015 * std)
    
    return candle['CCI']    
    


def supertrend(candles, index, period, factor):
    candle = candles[index]
    close = candle['close']

    try:
        candle['hl2'] = (candle['high']+candle['low'])/2.0
    except:
        candle['hl2'] = (candle['open']+candle['close'])/2.0

    atr = calc_atr(candles, index, period)
    
    if index == 0:
        candle['supertrend'] = candle['hl2']
        candle['trend_up'] = candle['hl2']
        candle['trend_down'] = candle['hl2']
        candle['trend'] = 0
        return candle['supertrend']
    
    previous = candles[index-1]
    previous_close = previous['close']
    previous_trend_up = previous['trend_up']
    previous_trend_down = previous['trend_down']
    
        
    fatr = factor*atr
    
    up =  candle['hl2'] - fatr
    down = candle['hl2'] + fatr

    
    if previous_close > previous_trend_up:
        trend_up = max(up, previous_trend_up)
    else:
        trend_up = up
    
    if previous_close < previous_trend_down:
        trend_down = min(down,previous_trend_down)
    else:
        trend_down = down

    candle['trend_up'] = trend_up
    candle['trend_down'] = trend_down

    
    if close > previous_trend_down:
        trend = 1
    elif close < previous_trend_up:
        trend = -1
    else:
        trend = previous['trend']

    candle['trend'] = trend

    
    if trend == 1:
        supertrend = trend_up
    else:
        supertrend = trend_down

    candle['supertrend'] = supertrend
    return supertrend



def rma_up(candles, source, n, length):
    target = candles[n]
    
    if n != 0:
        previous = candles[n-1]
    #length = 14
    if n < length:
        rma = float('nan')
    elif n==length:
        rma=0.0
        for i in range(1,length+1):
            rma = rma+max(candles[i][source]-candles[i-1][source],0)
            #print(rma)
        rma = rma/length
    elif n>length:
        rma = max(target[source]-previous[source],0)*(1/length) + (1-1/length)*previous['rsi_up']
    else:
        return target['rsi_up']
    return rma



def rma_down(candles, source, n, length):
    target = candles[n]
    if n != 0:
        previous = candles[n-1]
    #length = 14
    if n < length:
        rma = float('nan')
    elif n==length:
        #rma = -min(target[source]-previous[source],0)
        rma=0.0
        for i in range(1,length+1):
            rma = rma-min(candles[i][source]-candles[i-1][source],0)
        rma = rma/length
    elif n>length:
        rma = -min(target[source]-previous[source],0)*(1/length) + (1-1/length)*previous['rsi_down']
    else:
        return target['rsi_down']
    return rma


def calc_rsi(candles, index, length, source):
    candle = candles[index]

    candle['rsi_up'] = rma_up(candles, source, index, length)
    candle['rsi_down'] = rma_down(candles, source, index, length)
    
    if candle['rsi_down'] == 0:
        rsi=100
    elif candle['rsi_up'] == 0:
        rsi=0
    else:
        rsi=100-(100/(1+candle['rsi_up']/candle['rsi_down'])) 
    candle['rsi'] = rsi
    return rsi
        



def calc_renko(candles, index, renko, brick_size, timenow):
    candle = candles[index]
    close = candle['close']
    #dt = candle['datetime']
    dt = timenow
    #now_ = datetime.now().replace(microsecond=0)
    #now = now_ if param['live_trading']==True else candle['datetime']
    
    brick_size = round(brick_size,2)
    
    brick = {}
    if index==0:
        brick['datetime'] = dt
        brick['open'] = (close//brick_size)*brick_size
        brick['close'] = (close//brick_size)*brick_size
        brick['high'] = (close//brick_size)*brick_size
        brick['low'] = (close//brick_size)*brick_size
        renko.append(brick)
        #print(renko)
        return renko

    prev_open = renko[-1]['open']
    prev_close = renko[-1]['close']
    diff = round(close - prev_close,2)

    #print(close, prev_close)
    # Calculate number of bricks to plot
    try:
        num_bricks = int(np.floor(abs(diff) / brick_size))
    except Exception as e:
        print(e)
        print("brick_size: ", brick_size)
        print("candle: ", candle)
        num_bricks = int(np.floor(abs(diff) / brick_size))
        
    #print(num_bricks)
    if num_bricks != 0:
        # Determine the direction of the bricks
        direction = 1 if diff > 0 else -1
        prev_direction = 1 if (prev_close - prev_open)>0 else -1
        flip = direction != prev_direction #and abs(num_bricks)>1
        #print(direction, prev_direction, flip)
        for z in range(abs(num_bricks)):
            if not flip:
                brick['datetime'] = dt
                brick['open'] = renko[-1]['close']
                brick['close'] = brick['open'] + direction * brick_size
                brick['high'] = max(brick['open'], brick['close'])
                brick['low'] = min(brick['open'], brick['close'])
                renko.append(brick)
            if flip and z>0:
                brick['datetime'] = dt
                brick['open'] = renko[-1]['open']
                brick['close'] = brick['open'] + direction * brick_size
                brick['high'] = max(brick['open'], brick['close'])
                brick['low'] = min(brick['open'], brick['close'])
                renko.append(brick)
    return renko
                


def JurikMovingAverage(candles, index, sourcekey, ikey, length, phase, power):
    '''
    length = input(title="Length", type=integer, defval=7)
    phase = input(title="Phase", type=integer, defval=50)
    power = input(title="Power", type=integer, defval=2)
    src = input(title="Source", type=source, defval=close)
    highlightMovements = input(title="Highlight Movements ?", type=bool, defval=true)
    
    phaseRatio = phase < -100 ? 0.5 : phase > 100 ? 2.5 : phase / 100 + 1.5
    
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = pow(beta, power)
    
    jma = 0.0
    
    e0 = 0.0
    e0 := (1 - alpha) * src + alpha * nz(e0[1])
    
    e1 = 0.0
    e1 := (src - e0) * (1 - beta) + beta * nz(e1[1])
    
    e2 = 0.0
    e2 := (e0 + phaseRatio * e1 - nz(jma[1])) * pow(1 - alpha, 2) + pow(alpha, 2) * nz(e2[1])
    
    jma := e2 + nz(jma[1])
    
    jmaColor = highlightMovements ? (jma > jma[1] ? green : red) : #6d1e7f
    plot(jma, title="JMA", linewidth=2, color=jmaColor, transp=0)

    '''
    candle = candles[index]
    price = candle[sourcekey]
    if index<1:
        candle['jurik_e0'] = price
        candle['jurik_e1'] = price
        candle['jurik_e2'] = price
        candle['jurikma'] = price
        return price

    prev = candles[index-1]
    
    phase_ratio = 0.5 if phase < -100 else 2.5 if phase > 100 else phase / 100 + 1.5
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = beta**power
    
    candle['jurik_e0'] =  (1 - alpha) * price + alpha * prev['jurik_e0']
    candle['jurik_e1'] = (price - candle['jurik_e0']) * (1 - beta) + beta * prev['jurik_e1']
    candle['jurik_e2'] = (candle['jurik_e0'] + phase_ratio * candle['jurik_e1'] - prev['jurikma']) * ((1 - alpha)**2) + (alpha**2) * prev['jurik_e2']
    
    jma = candle['jurik_e2'] + prev['jurikma']
    candle['jurikma'] = jma
    return jma




def calculate_option_delta(S, K, T, r, sigma, option_type='call'):
    """
    Calculate the Delta of an option using the Black-Scholes model.

    Parameters:
    S : float : Current price of the underlying asset
    K : float : Strike price of the option
    T : float : Time to expiration (in years)
    r : float : Risk-free interest rate (annual)
    sigma : float : Volatility of the underlying asset (annualized)
    option_type : str : 'call' for call option, 'put' for put option

    Returns:
    float : Delta of the option
    
    # Example usage
    S = 25000  # Current price of the underlying asset
    K = 24650  # Strike price
    T = 0.05  # Time to expiration (in years)
    r = 0.065  # Risk-free interest rate (annual)
    sigma = 0.18  # Volatility (annualized)
    
    call_delta = calculate_option_delta(S, K, T, r, sigma, option_type='call')
    put_delta = calculate_option_delta(S, K, T, r, sigma, option_type='put')
    
    print(f"Call Option Delta: {call_delta}")
    print(f"Put Option Delta: {put_delta}")
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))

    if option_type == 'call':
        delta = norm.cdf(d1)
    elif option_type == 'put':
        delta = norm.cdf(d1) - 1
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")
    
    return delta


def days_until_last_weekday(timenow, wi):
    today = timenow#.date()
    #print(today.year,today.month )
    if today.month==12:
        nxm = 1
        yr = today.year+1
    else:
        nxm=today.month+1
        yr = today.year
    
    last_day_of_month = date(yr, nxm, 1) - timedelta(days=1)
    last_wednesday = last_day_of_month
    while last_wednesday.weekday() != wi:  # 2 corresponds to Wednesday
        last_wednesday -= timedelta(days=1)
    #days_remaining = (last_wednesday - today).days
    lw = last_wednesday
    date1 = datetime(lw.year, lw.month, lw.day, 15, 30)
    difference = (date1 - today)
    days_remaining = difference.total_seconds() / (24 * 60 * 60)
    return date1, days_remaining


def calc_adx(prices, index, period=14):
    candles = prices
    candle = prices[index]

    atr = calc_atr(candles, index, period)
    
    if index < 1:
        candle['adx'] = 0.0
        candle['plus_dm_val'] = 0.0
        candle['minus_dm_val'] = 0.0
        candle['+dm'] = 0.0
        candle['-dm'] = 0.0
        return candle['adx']

    #atr = calc_atr(candles, index, period)
        
    # Initialize lists for calculations
    tr_list = []
    plus_dm = []
    minus_dm = []

    i=index
    # Calculate True Range (TR), +DM, and -DM up to index
    high = prices[i]['high']
    low = prices[i]['low']
    close_prev = prices[i-1]['close']
    
    
    # Directional Movement
    up_move = high - prices[i-1]['high']
    down_move = prices[i-1]['low'] - low
    candle['plus_dm_val'] = up_move if up_move > down_move and up_move > 0 else 0
    candle['minus_dm_val'] = down_move if down_move > up_move and down_move > 0 else 0

    candle['+dm'] = RMAKeyCandleKey(candles, index, period, 'plus_dm_val', '+dm')
    candle['-dm'] = RMAKeyCandleKey(candles, index, period, 'minus_dm_val', '-dm')
    
    #if smoothed_tr is None or smoothed_tr == 0:
    #    return {'adx': None, '+di': None, '-di': None}
    try:
        plus_di = (candle['+dm'] / atr) * 100
    except:
        plus_di = 0.0

    try:
        minus_di = (candle['-dm'] / atr) * 100
    except:
        minus_di = 0.0
        
    # Calculate DX
    candle['dx'] = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) != 0 else 0
    candle['adx'] = RMAKeyCandleKey(candles, index, period, 'dx', 'adx')
    return candle['adx']



    

        
######################------------------------END------------------------------------------------------