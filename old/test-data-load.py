from trades import trades
import pickle
from collections import deque
import csv
import time



def loadData(dataPath = '/media/Big Daddy/New_Documents/python_data/btc_usd_depth.pkl',num=None):
    i = 0
    historical = open(dataPath,'rb')
    
    full_data = []
    while True:
        try:
            if num != None and i > num: break
            current = pickle.load(historical)
            full_data.append(current)
            i = i+1
        except EOFError:
            print 'Done Loading.'
            break
        except:
            print 'Problem loading.'
            break
    
    return full_data
    
x = loadData()


import btceapi
from collections import deque
connection = btceapi.BTCEConnection()
ticker = btceapi.getTicker("btc_usd", connection)