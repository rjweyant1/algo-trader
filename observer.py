#!/usr/bin/python
from scipy import stats
import numpy as np
import math
import random
import matplotlib.pyplot as plt
from trades import trades
import time
import pickle
import matplotlib.cm as cm


def loadData(data = '/media/Big Daddy/New_Documents/python_data/btc_usd_depth.pkl',num=None):
    print data
    i = 0
    historical = open(data,'r')
    
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

def loadQuickData(data = '/media/Big Daddy/New_Documents/python_data/btc_usd_depth.pkl',num=None):
    print data
    i = 0
    historical = open(data,'rb')
    
    price_data = []
    time_data = []
    for line in historical:
       (pair,mktime,price)= line.split(',')
       price_data.append(price)
       time_data.append(mktime)
    
    price_data=[float(i.strip()) for i in price_data]
    time_data = [float(i.strip()) for i in time_data]
    return price_data,time_data
    
def moving_average(x,k=30):
    ''' 
    calculate simple moving average with window size of k
    '''
    ma = []
    for i in range(len(x)):
        if i < k:
            ma.append(np.mean(x[0:(i+1)]))
        else:
            ma.append(ma[i-1] + (x[i]-x[i-k])/k)
    return ma
    
def moving_derivative(y,x,k=30):
    ''' 
    approximate derivative using past i markers.    
    '''
    md = [0,0]
    for i in range(len(x)):
        if i <= k and i > 1:    md.append(get_slope(x[0:i],y[0:i]))
        elif i > k and i > 1:   md.append(get_slope(x[(i-k):i],y[(i-k):i]))
        
    return md
    
def get_slope(x,y):
    '''
    get slope of regression line of window [i,j]
    '''
    #time = x.time[i:j]
    #rate = x.rate[i:j]
    slope,intercept,correlation,p,se = stats.linregress(x,y)
    return slope
    
def exchange_btc_to_usd(amt,price): return(amt*price)
def exchange_usd_to_btc(amt,price): return(amt/price)


class order:
    ''' Nothing yet. '''
    def __init__(self):
        pass
    
class test_set:
    def __init__(self,smooth,md,ma,percent,lossTolerance=0.1, riseTolerance=0.1):
        self.n = 0
        self.btc = []
        self.usd = []
        self.zero = []
        self.smooth=smooth
        self.md = md
        self.ma = ma
        self.percent=percent
        self.lossTolerance = lossTolerance
        self.riseTolerance = riseTolerance
        self.orders=[]
        self.lastBuy = -9999
        self.lastSell = 9999
        self.BUYFEE = 0.002
        self.SELLFEE = 0.002
        self.ALERT = False
        self.EXECUTE = False

        
    def loadData(self,price,time):
        ''' loads price/time from lists '''
        # initial load
        self.price = price
        self.time = time
        
        # smoothing
        self.price_smooth = moving_average(self.price,self.smooth)
        self.d1=moving_derivative(self.price_smooth,self.time,self.md)
        self.d1_smooth=moving_average(self.d1,self.ma)
        self.d2 = moving_derivative(self.d1,self.time,self.md)
        self.d2_smooth = moving_average(self.d2,self.ma)
        self.n = len(self.price)

    def update(price,time):
        '''
        Given a single price/time pair, this updates the data set 
        '''
        self.price.append(price)
        self.time.append(time)
        self.n=self.n+1
        
        # do something about real time !!!
        
        # update price, derivatives and smooth functions
        self.price_smooth.append(mean(self.price[self.n-self.smooth:]))
        self.d1.append(get_slope(self.price_smooth[self.n-self.md:]))
        self.d1_smooth.append(mean(self.d1[self.n-self.ma:]))
        self.d2.append(get_slope(self.d1_smooth[self.n-self.md:]))
        self.d2_smooth.append(mean(self.d2[self.n-self.ma:]))
        
    def check_current_extreme(self):
        ''' 
        Identify if the CURRENT price shows evidence of a minimum or maximum.
        Also checks if an apparent previous execution was premature (SAFEGUARD)        
        '''

        # CHECK IF LAST D1 WAS NEGATIVE AND CURRENT D1 IS POSITIVE 
        # AND THE PRICE HAS DECREASED BY A CERTAIN PERCENT SINCE LAST SELL
        # also requires that number of dollars is positive -- as in the last action was a SELL
        if self.d1_smooth[self.n-1] <0 and self.d1_smooth[self.n] >0 and self.price[self.n] < (1-self.percent)*self.lastSell and self.usd[self.n] > 0:
            print 'Buy\t', round(self.lastSell,1),round((1-self.percent)*self.price[self.n],1)
            self.buy()
            
        # CHECK IF LAST D1 IS POSITIVE AND CURRENT D1 IS NEGATIVE
        # AND THE PRICE HAS INCREASED BY A CERTAIN PERCENT SINCE LAST BUY
        # also requires that number of BTC is positive -- as in last action was a BUY
        elif self.d1_smooth[self.n-1]>0 and self.d1_smooth[self.n]<0 and self.price[self.n] > (1+self.percent)*self.lastBuy and self.btc[self.n]>0:
            print 'Sell\t', round(self.lastBuy,1), round((1+self.percent)*self.price[self.n],1)
            self.sell()

        #### SAFE GUARDS -- RISK TOLERANCE ####
        # if we dip below our risk tolerance, sell.
        elif self.price_smooth[self.n] < (1-self.lossTolerance)*self.lastBuy and self.btc[self.n]>0:
            print 'BOUGHT at %s and price is now %s Still going down, SELLING' % (round(self.lastBuy,1),round(self.price[self.n],1))
            self.sell()

        # if the price keeps going up after peak, then buy?
        # I have not seen evidence of this happening, and actually acting on it seems slightly harder to implement.
        elif self.price_smooth[self.n]>(1+self.riseTolerance)*self.lastSell and self.usd[self.n]>0 and False:
            print 'SOLD at %s and price is now %s Still going up, BUYING' % (round(self.lastSell,1),round(self.price[self.n],1))
            self.buy()
            
    def buy(self):
        ''' 
        This function simulates buying BTC with USD
        Right now, it exchanges all USD for BTC.
        '''
        
        # These are temporary amounts calculated before updating 
        newUSD = 0
        newBTC = exchange_usd_to_btc(self.usd[self.n]*(1-self.BUYFEE),self.price[self.n])
        
        #    reset new last-buy price.
        self.lastBuy=self.price[self.n]
        self.lastSell=9999        

        # set all future values to current value
        self.btc[self.n] = newBTC
        self.usd[self.n] = newUSD
        
        # Not sure what to do about this.
        self.orders[self.n] = 1
        
        # Placeholders
        if self.ALERT:   pass
        if self.EXECUTE: pass
            
    def sell(self,ALERT=False, EXECUTE=False):
        ''' 
        This function simulates selling BTC for USD
        Exchange ALL BTC for USD
        '''
        # These are temprorary amounts calculated before updating.
        newUSD = exchange_btc_to_usd(self.btc[self.n]*(1-self.SELLFEE),self.price[self.n])
        newBTC = 0
        
        # Set last sell in case price keeps increasing.
        self.lastSell=self.price[self.n]
        self.lastBuy=-9999
        
        # change all future values
        self.btc[self.n] = newBTC
        self.usd[self.n] = newUSD
        
        # Not sure what to do about this.
        self.orders[self.n] = 1
        
        # Placeholders
        if self.ALERT:   pass
        if self.EXECUTE: pass

    def step(self,price,time,backup=0):
        # update current price/time
        self.update(price,time)
        
        # Check if evidence that price is currently at a minimum or maxmium
        # Execute theoretical trade at this point.
        self.check_current_extreme()
        
        # Placeholders
        # if backup = 1 --> update current profit summary
        # if backup = 2 --> update larger summary object [think what this is]
        if backup > 0:  pass
        if backup > 1:  pass
        

    def add_usd(self,amt):
        ''' add money to simulation.'''
        self.usd[0]=amt


    def plot(self,burn_in=30):
        ''' Display plots of price and derivatives. '''
        fig = plt.figure()
        orders = [i for i in self.orders if i > burn_in]
        ax1 =fig.add_subplot(511) 
        #print self.price
        
        # price curve
        ax1.plot(self.time[burn_in:],self.price[burn_in:], 'b',linewidth=2)
        ax1.plot(self.time[burn_in:],self.price_smooth[burn_in:], 'b',linewidth=4)
        #ax1.vlines(orders,min(self.price[burn_in:]),max(self.price[burn_in:]))
        #ax1.ylabel('USD/BTC')
        
        # First derivative
        ax2 =fig.add_subplot(512) 
        ax2.plot(self.time[burn_in:],self.d1_smooth[burn_in:], 'b',linewidth=4)
        ax2.plot(self.time[burn_in:],self.zero[burn_in:], 'b',linewidth=1)
        #ax2.vlines(orders,min(self.d1_smooth[burn_in:]),max(self.d1_smooth[burn_in:]))
        #ax2.ylabel('First Derivative')
        
        # Second Derivative
        ax3 =fig.add_subplot(513) 
        ax3.plot(self.time[burn_in:],self.d2_smooth[burn_in:], 'b',linewidth=4)
        ax3.plot(self.time[burn_in:],self.zero[burn_in:], 'b',linewidth=1)
        #ax3.vlines(orders,min(self.d2_smooth[burn_in:]),max(self.d2_smooth[burn_in:]))
        #ax3.ylabel('Second Derivative')        
        
        # Amt BTC
        ax4 =fig.add_subplot(514) 
        ax4.plot(self.time[burn_in:],self.btc[burn_in:], 'b',linewidth=4)
        #ax4.ylabel('BTC')
        
        # Amt USD
        ax5 =fig.add_subplot(515) 
        ax5.plot(self.time[burn_in:],self.usd[burn_in:], 'b',linewidth=4)
        #ax5.ylabel('USD')        
        plt.show()
        
    def quickPlot(self,values,i,j):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(values[i:j])
        plt.show()
