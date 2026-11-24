"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import numpy as np
import pandas as pd
#import datetime
from datetime import datetime
import time
#from decimal import Decimal
import pandas as pd
import requests
from datetime import date,timedelta
#import simplejson as json
import os
import pytz
import ast
#import inspect

#from ACCOUNT_DETAIL import ACCOUNT_ID_STRING,  CLIENT_ID_STRING


CLIENT_ID = ""
REFRESH_TOKEN=""
#CLIENT_ID = CLIENT_ID_STRING
#API_KEY = CLIENT_ID+"@AMER.OAUTHAP"

#ACCOUNT_ID = "123456789"
#ACCOUNT_ID = ACCOUNT_ID_STRING

#https://auth.tdameritrade.com/oauth?client_id=DEARSOURABH99%40AMER.OAUTHAP&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1

#data_folder = inspect.getfile(src.techlib).replace("techlib.py","")

#data_folder = os.path.dirname(os.path.realpath('__file__'))
#filename = "REFRESH_TOKEN"
#filepath = os.path.join(data_folder, filename)
#REFRESH_TOKEN = open(filepath,"r").read()

#print(REFRESH_TOKEN, CLIENT_ID)

def get_access_token(refresh_token=REFRESH_TOKEN, client_id=CLIENT_ID):
    #print(REFRESH_TOKEN, CLIENT_ID)
    tz = pytz.timezone('US/Eastern')
    now = datetime.now()
    nowtz = now.astimezone(tz).replace(tzinfo=None)
    
    try:
        with open('ACCESS_TOKEN','r') as alog:
            token  = alog.read()
        #print(token)
        token_dict = ast.literal_eval(token)
        #print(token_dict)
        token_ts = next(iter(token_dict))
        access_token = token_dict[token_ts]
        #print(token_ts)
        access_ts  = datetime.strptime(token_ts, "%Y %m %d %H:%M:%S")
        #print(type(access_ts))
        if nowtz-access_ts<timedelta(minutes=20):
            return access_token
        #print('hello')
    except:
        pass
    
    
    
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = [
      ('grant_type', 'refresh_token'),
      ('refresh_token', refresh_token),
      ('access_type', ''),
      ('code', ''),
      ('client_id', client_id),
      ('redirect_uri', ''),
    ]
    #print(REFRESH_TOKEN)

    resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
    #print(resp)
    #print('checking access token')
    if resp.status_code != 200:
        raise Exception('Could not authenticate!')
    
    access_token = resp.json()['access_token']
    
    tz = pytz.timezone('US/Eastern')
    now = datetime.now()
    nowtz = now.astimezone(tz)
    nowtzstr = nowtz.strftime("%Y %m %d %H:%M:%S")
    
    token_dict = {}
    token_dict[nowtzstr] = access_token
    
    try:
        with open('./ACCESS_TOKEN','w') as alog:
            alog.write(str(token_dict)) 
    except:
        pass
    
    print('fresh access token')
    return access_token
