"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


g_token_list = []
g_instrument_dict =  {}
g_underinstrument_dict =  {}
g_futures_dict = {}
g_futures_token_dict = {}
#global variables
g_universalparam = {}

g_param = {}
g_bankparam = {}
g_finparam = {}
g_midcapparam = {}
g_sensexparam = {}
g_bankexparam = {}

g_stockparam = {}

g_signal_dict = {}
g_trade_table_counter=0
g_trade_table_counter_start=False
g_market_dict={}
g_bar_dict = {}

g_out_live = None

g_kite = None
g_kiteticker = None
g_tick = None
g_lastdata = {}
g_copytick = False

g_shoonya = None


max_profit = 0.0
max_loss = 0.0
magic_tag = ''

week_code = {"MONDAY":0, "TUESDAY":1, "WEDNESDAY":2, "THURSDAY":3, "FRIDAY":4, "SATURDAY":5, "SUNDAY":6}
month_code = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7,"AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}
month_map = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL",8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}

