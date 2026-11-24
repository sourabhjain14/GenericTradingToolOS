"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


def modify_order(order_id):
    print("IN MODIFY ORDER")
    try:
        kite = globalvar.g_kite
    except Exception as e:
        print(e)
        return None
    
    #variety=kite.VARIETY_REGULAR
    try:
        i=0
        while(i<10):
            time.sleep(3)
            i+=1
            order = kite.order_history(order_id)[0]
            print('modify order: ', order)
            order_status = order['status']
            order_open = (order_status != 'COMPLETE') and (order_status != 'CANCELLED') and (order_status != 'REJECTED')
            print('modify order open: ', order_open)
            if order_open:
                symbol = order['tradingsymbol']
                variety = order['variety']
                dir = order['transaction_type']
                price = order['price']
                exchange = order['exchange']
                
                qsymbol = exchange+":"+symbol
                quote = kite.quote(qsymbol)
                v = quote[qsymbol]
                ltp = v['last_price']
                #bid = v["depth"]["buy"][0]["price"]
                #ask = v["depth"]["sell"][0]["price"]
                try:
                    bid = v["depth"]["buy"][0]["price"]
                except:
                    bid = ltp
                try:
                    ask = v["depth"]["sell"][0]["price"]
                except:
                    ask = ltp
                
                if dir=='BUY': best_price =  ask
                elif dir=='SELL': best_price = bid
                print("modifying order for ", symbol, ' having price ', price, ' with new price ', best_price)
                order_id = kite.modify_order(variety=variety, order_id=order_id, price=best_price)
            else:
                return order_id
        return order_id
    except Exception as e:
        print("zerodha modfiy order error:",e)
        return order_id