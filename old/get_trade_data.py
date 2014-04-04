#!/usr/bin/python
import btceapi
from collections import deque
import csv
import time
import pickle
from trades import trades

def mean(x):
    return sum(x)/len(x)

def getPrice(connection,f,pair="btc_usd"):
    
    #get ticker
    ticker = btceapi.getTicker(pair, connection)
    #print ticker.high
    #get asks/bids
    asks, bids = btceapi.getDepth(pair)
    ask_prices, ask_volumes = zip(*asks)
    bid_prices, bid_volumes = zip(*bids)

    #start list with all of the ticker info
    curTrades = trades(coin='ltc',updated=ticker.updated,server_time=ticker.server_time,buy=ticker.buy,sell=ticker.sell)
    #print out_list
    #now we have a huge list with all the info, write to a single line in the csv file
    
    
    print pair
    print curTrades.buy
    # Pickle class using protocol 0.
    pickle.dump(curTrades,f) 
    
def collect_data(wait=60):
    
    #initialize connection
    connection = btceapi.BTCEConnection()
   
    while 1:
        btc_usd_f = open('/media/Big Daddy/New_Documents/python/python_projects/trading/data/btc_usd_depth.pkl', 'ab')
        ltc_btc_f = open('/media/Big Daddy/New_Documents/python/python_projects/trading/data/ltc_btc_depth.pkl', 'ab')
        ltc_usd_f = open('/media/Big Daddy/New_Documents/python/python_projects/trading/data/ltc_usd_depth.pkl', 'ab')
        
        try:    getPrice(connection,btc_usd_f,'btc_usd')
        #if connection is lost, just try to reconnect (this does seem to happen, so this line is actually pretty important for long data collects)
        except: connection = btceapi.BTCEConnection()

        try:    getPrice(connection,ltc_btc_f,'ltc_btc')
        #if connection is lost, just try to reconnect (this does seem to happen, so this line is actually pretty important for long data collects)
        except: connection = btceapi.BTCEConnection()
        
        try:    getPrice(connection,ltc_usd_f,'ltc_usd')
        #if connection is lost, just try to reconnect (this does seem to happen, so this line is actually pretty important for long data collects)
        except: connection = btceapi.BTCEConnection()        
     
        print 'done loop'

        btc_usd_f.close()
        ltc_btc_f.close()
        ltc_usd_f.close()

        
        #sleep for .5 seconds, i.e. collect at 2Hz
        time.sleep(wait)

def main():
    collect_data(wait=600)
    
if __name__ == '__main__':
    main()