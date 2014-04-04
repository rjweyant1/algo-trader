#!/usr/bin/python
import btceapi
from BeautifulSoup import BeautifulSoup
import urllib2
import csv
import time
import pickle
from trades import trades

def mean(x):
    return sum(x)/len(x)

    
def get_CT_Sell(f,coin='wdc'):
    link = 'https://crypto-trade.com/api/1/ticker/'+coin+'_usd'
    page = urllib2.urlopen(link)
    soup = BeautifulSoup(page)
    pretty = soup.prettify().strip().split('{')[2].replace('}','').replace("\"",'').split(',')
    for line in pretty:
        pair = line.split(':')
        if pair[0] == 'max_bid':
            price = float(pair[1])
            
    line = ','.join((coin,str(time.mktime(time.localtime())),str(curTrades.buy)))
    f.write(line)
    
    return float(price)
    
def collect_data(wait=60):
    
    while 1:
        btc_usd_f = open('/media/Big Daddy/New_Documents/python/python_projects/trading/data/ct_basic_btc_usd_depth.pkl', 'a')
        ltc_usd_f = open('/media/Big Daddy/New_Documents/python/python_projects/trading/data/ct_basic_ltc_usd_depth.pkl', 'a')
        wdc_usd_f = open('/media/Big Daddy/New_Documents/python/python_projects/trading/data/ct_basic_wdc_usd_depth.pkl', 'a')
        get_CT_Sell(btc_usd_f,'btc')
        #getPrice(connection,btc_usd_f,'btc_usd')
        try:    get_CT_Sell(btc_usd_f,'btc')
        #if connection is lost, just try to reconnect (this does seem to happen, so this line is actually pretty important for long data collects)
        except: print 'problemo'

        try:    get_CT_Sell(ltc_usd_f,'ltc')
        #if connection is lost, just try to reconnect (this does seem to happen, so this line is actually pretty important for long data collects)
        except: print 'problemo'

        try:    get_CT_Sell(wdc_usd_f,'wdc')
        #if connection is lost, just try to reconnect (this does seem to happen, so this line is actually pretty important for long data collects)
        except: print 'problemo'

        print 'done loop'

        btc_usd_f.close()
        ltc_usd_f.close()
        wdc_usd_f.close()
        
        #sleep for .5 seconds, i.e. collect at 2Hz
        time.sleep(wait)

def main():
    collect_data(wait=300)
    
if __name__ == '__main__':
    main()