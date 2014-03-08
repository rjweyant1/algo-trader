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
        self.lastBuy = -9999
        self.lastSell = 9999
        self.smooth=smooth
        self.md = md
        self.ma = ma
        self.percent=percent
        self.lossTolerance = lossTolerance
        self.riseTolerance = riseTolerance
        self.orders=[]
        
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
        ''' Given a single price/time pair, this updates the data '''
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
        
    def find_extrema(self,percent=0.1,burn_in=150):
        ''' Identify min and maxes of the price curve.'''
        self.timer = 0
        for i in range(burn_in+1,self.n):
            # at minimum --> buy
            if self.d1_smooth[i-1] <0 and self.d1_smooth[i] >0 and self.timer == 0 and self.usd[i] > 0 and self.price[i] < (1-percent)*self.lastSell:
                print 'Buy', self.lastSell,(1-percent)*self.price[i]
                #print 'border crossing'
                self.buy(i)
                
            # at maximum --> sell
            elif self.d1_smooth[i-1]>0 and self.d1_smooth[i]<0 and self.timer == 0 and self.btc[i]>0 and self.price[i] > (1+percent)*self.lastBuy:
                print 'Sell', self.lastBuy, (1+percent)*self.price[i]
                #print 'border crossing'
                self.sell(i)

            # if we dip below our risk tolerance, sell.
            elif self.price_smooth[i] < (1-self.lossTolerance)*self.lastBuy and self.timer == 0 and self.btc[i]>0:
                print 'Bought at %s and price is now %s Still going down, selling' % (self.lastBuy,self.price[i])
                self.sell(i)
                #self.timer = self.timer+15
                
            # if the price keeps going up after bump
            elif self.price_smooth[i]>(1+self.riseTolerance)*self.lastSell and self.timer == 0 and self.usd[i]>0 and False:
                print 'Still going up, buying'
                self.buy(i)
                #self.timer = self.timer+15

            if self.timer > 0:
                self.timer = self.timer-1
    def add_usd(self,amt,time=0):
        ''' add money to simulation.'''
        self.usd=[self.usd[i] for i in range(0,time)] + [self.usd[i] + amt for i in range(time,self.n)]
    def add_btc(self,amt,time=0):
        ''' add money to simulation.'''
        self.btc=[self.btc[i] for i in range(0,time)] + [self.btc[i] + amt for i in range(time,self.n)]

    def buy(self,i):
        ''' 
        This is the function that will perform everything necessary to purchase bitcoins.
        Right now, it just changes the values of the dollar/BTC amount from now till the end.
        '''
        newUSD = 0
        newBTC = exchange_usd_to_btc(self.usd[i]*.998,self.price[i])
        #    set new last buy price to keep track if things drop afterwards.
        self.lastBuy=self.price[i]
        self.lastSell=9999
        #print 'New BTC: %s' % newBTC
        # set all future values to current value
        self.btc = [self.btc[t] for t in range(0,i)]+[newBTC for t in range(i,self.n)]
        self.usd = [self.usd[t] for t in range(0,i)]+[newUSD for t in range(i,self.n)]
        self.orders[i] = 1
        self.timer = 1   
    def sell(self,i):
        ''' 
        function will do everything necessary for selling bitcoin.
        '''
        newUSD = exchange_btc_to_usd(self.btc[i]*.998,self.price[i])
        newBTC = 0
        
        # Set last sell in case price keeps increasing.
        self.lastSell=self.price[i]
        self.lastBuy=-9999
        #print 'New USD: %s ' % newUSD
        
        # change all future values
        self.btc = [self.btc[t] for t in range(0,i)]+[newBTC for t in range(i,self.n)]
        self.usd = [self.usd[t] for t in range(0,i)]+[newUSD for t in range(i,self.n)]
        self.orders[i] = i
        self.timer = 1        

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
