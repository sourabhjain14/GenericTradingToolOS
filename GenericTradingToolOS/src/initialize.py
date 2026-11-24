"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import os

global g_streamer_connection
g_streamer_connection = False



global g_tick_dict
g_tick_dict = {}


global g_param
g_param = {}


global param
param = {}


global g_security_dict
g_security_dict = {}

#global g_kite
#g_kite = None
DATAPATH = "../data/"
PLOTPATH = "../plot/"
SUMMARYPATH = "../summary/"
ANALYSISPATH = "../analysis/"

path = "./strategy"
dir_list = os.listdir(path)
#print(dir_list)

STRATEGY_LIST=[]
for e in dir_list:
    if '_strategy' in e:
        es = e[:-12]
        STRATEGY_LIST.append(es)
#print(STRATEGY_LIST)        

param['portfolio_dict'] = {}
param['indicator_dict'] = {}

'''
for e in STRATEGY_LIST:
    param['portfolio_dict'][e] = {}
    param['indicator_dict'][e] = {}
print(param)
'''