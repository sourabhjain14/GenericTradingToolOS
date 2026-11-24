"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import globalvar
import importlib
import zerodha
#importlib.reload(zerodha)
import finvasia
#importlib.reload(finvasia)
#from zerodha import BUY_LIMIT
#kite = globalvar.g_kite
#symbol = "NIFTY2491925000CE"
#BUY_LIMIT(kite=kite, symbol=symbol, quantity=25, price=290.0)

def place_buy(exchange="",broker="",broker_object=None, symbol="", quantity=0, price=None):
    if broker=="zerodha":
        return zerodha.BUY_LIMIT(exchange=exchange,kite=broker_object, symbol=symbol, quantity=quantity, price=price, tag=globalvar.magic_tag)
    elif broker=="finvasia":
        return finvasia.BUY_LIMIT(exchange=exchange, brokerapi=broker_object, symbol=symbol, quantity=quantity, price=price, tag=globalvar.magic_tag)



def place_sell(exchange="",broker="",broker_object=None, symbol="", quantity=0, price=None, short_flag=0):
    if broker=="zerodha":
        return zerodha.SELL_LIMIT(exchange=exchange,kite=broker_object, symbol=symbol, quantity=quantity, price=price, 
                           tag=globalvar.magic_tag, short_flag=short_flag)
    elif broker=="finvasia":
        return finvasia.SELL_LIMIT(exchange=exchange,brokerapi=broker_object, symbol=symbol, quantity=quantity, price=price, 
                            tag=globalvar.magic_tag, short_flag=short_flag)


