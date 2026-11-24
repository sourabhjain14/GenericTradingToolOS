"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


import nest_asyncio
import asyncio
from datetime import datetime
background_tasks = set()

nest_asyncio.apply()

LEN = 10000000

async def some_coro(param):
    i = param+2
    c=0
    for zi in range(LEN):
        #print(param, zi//i)
        c+=1
    return 0
        
async def check():
    # Create a task for each stock
    stocks = [0,1,2,3,4,5,6,7,8,9]
    tasks = [some_coro(stock) for stock in stocks]
    # Run the tasks within Jupyter's event loop
    #results = asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))
    results = await asyncio.gather(*tasks)
    return results
    

def fetch():
    print("f1",datetime.now())
    re = asyncio.run(check())
    print("f2",datetime.now())
    print("f:",re)


def n_some_coro(param):
    i = param+2
    c=0
    for zi in range(LEN):
        #print(param, zi//i)
        c+=1
    return c

def sf():
    print("sf1",datetime.now())
    stocks = [0,1,2,3,4,5,6,7,8,9]
    for stock in stocks:
        n_some_coro(stock)
    print("sf2",datetime.now())
    fetch()
    
        
    