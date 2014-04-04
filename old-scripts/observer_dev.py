#!/usr/bin/python

'''
This class follows one strategy...
need something more helpful here
'''

from common import *
import numpy as np
from numpy import mean
import matplotlib.pyplot as plt


class observer:
    # constructor
    def __init__(self,smooth=1,md=5,ma=5,percent=0.05,lossTolerance=0.05, riseTolerance=0.05,percentExtremum=0.01,percentTrade=0.05,percentRisk=0.02,method=1):
        self.n = 0
        self.btc = [0]
        self.usd = [1]
        self.current_worth = [1]
        self.smooth=smooth
        if method == 1:
            self.md = md
            self.ma = ma
            self.percent=percent
            self.lossTolerance = lossTolerance
            self.riseTolerance = riseTolerance
            self.depth = 2*max(self.smooth,self.ma,self.md)            
            
        if method == 2: 
            self.percent_for_extremum = percentExtremum
            self.percent_for_trade = percentTrade
            self.percent_for_risk = percentRisk
            self.depth = 2*self.smooth
            self.current_window=[]
        if method != 1 and method != 2: pass
        
        
        self.orders=np.array([])
        self.lastBuy = -9999
        self.lastSell = 9999
        self.BUYFEE = 0.002
        self.SELLFEE = 0.002
        
        self.ALERT = False
        self.EXECUTE = False
     
    def loadData_dev(self,price,time):
        ''' 
        loads price/time from lists 
        '''
        # initial load
        self.price = price
        self.time = time
        
        # smoothing
        self.price_smooth = moving_average(self.price,self.smooth)
        self.curMax = max(self.price_smooth)
        self.curMin = min(self.price_smooth)
        self.curState = None
        self.n = len(self.price)-1
        
        # move starting btc and usd forward
        self.btc = self.btc*(self.n+1)
        self.usd = self.usd*(self.n+1)
        self.current_worth = (np.array(self.btc)*np.array(self.price) + np.array(self.usd)).tolist()


    def update_dev(self,price,time):
        '''
        Given a single price/time pair, this updates the data set 
        '''
        
        # drop old data -- resize list 
        if self.n > self.depth:
            self.price = self.price[-self.depth:]
            #self.time = self.time[-self.depth:]
        
        self.price.append(price)
        self.time.append(time)
        self.btc.append(self.btc[self.n])
        self.usd.append(self.usd[self.n])
        self.n=self.n+1
        
        # update price, derivatives and smooth functions
        # only look at last window.
        self.price_smooth.append(mean(self.price[-self.smooth:]))
        self.current_window.append(self.price_smooth[-1])
        self.curMax = max(self.current_window)
        self.curMin = min(self.current_window)
        
    def check_current_extreme_dev(self):
        ''' 
        '''
        '''
        # if current price is Z percent lower than current Max and 
        # we are X% higher than last buy, then are dropping --> SELL
        if self.price_smooth[-1] > self.curMin*(1+self.percent_for_extremum) and self.price_smooth[-1] < (1-self.percent_for_trade)*self.lastSell and self.usd[-1] > 0:
            print 'BUY: current price %s, current min %s, last Sell %s' % (self.price_smooth[-1],self.curMin,self.lastSell)
            self.buy()
        
        # if we are Z% higher than current minimum and we are X% lower
        # than last sell, then we are rising --> BUY
        if self.price_smooth[-1] < self.curMax*(1-self.percent_for_extremum) and self.price_smooth[-1] > (1+self.percent_for_trade)*self.lastBuy and self.btc[-1] > 0:
            print 'SELL: current price %s, current max %s, last Buy %s' % (self.price_smooth[-1],self.curMax,self.lastBuy)
            self.sell()
        
        #   if we are Y% lower than last buy, the loss is too great --> SELL
        if self.price_smooth[-1] < (1-self.percent_for_risk)*self.lastBuy:
            print 'RISK SELL: current price %s, current max %s, last Buy %s' % (self.price_smooth[-1],self.curMax,self.lastBuy)
            self.sell()
        
        #   if we are Y% lower than last sell, the gain is too great --> BUY?
        if self.price_smooth[-1] > (1+self.percent_for_risk)*self.lastSell:
            print 'RISK BUY: current price %s, current min %s, last Sell %s' % (self.price_smooth[-1],self.curMin,self.lastSell)
            self.buy()
        '''
            
        if self.price[-1] > (1+self.percent_for_trade)*self.lastBuy and self.btc[-1] > 0:
            print 'SELL: current price %s, current max %s, last Buy %s' % (self.price_smooth[-1],self.curMax,self.lastBuy)
            self.sell()

        if self.price[-1] < (1-self.percent_for_trade)*self.lastSell and self.usd[-1] > 0:
            print 'BUY: current price %s, current min %s, last Sell %s' % (self.price_smooth[-1],self.curMin,self.lastSell)
            self.buy()
        if (self.time[-1] - self.orders[-1][1]) > 86400 and self.orders[-1][2] == 1:
            print 'Wait BUY: current price %s, current min %s, last Sell %s' % (self.price_smooth[-1],self.curMin,self.lastSell)
            self.buy()
        if self.price_smooth[-1] < (1-self.percent_for_risk)*self.lastBuy:
            print 'RISK SELL: current price %s, current max %s, last Buy %s' % (self.price_smooth[-1],self.curMax,self.lastBuy)
            self.sell()
            
                        
            
        
    def buy(self):
        ''' 
        This function simulates buying BTC with USD
        Right now, it exchanges all USD for BTC.
        '''
        
        # These are temporary amounts calculated before updating 
        newUSD = 0
        newBTC = exchange_usd_to_btc(self.usd[-1]*(1-self.BUYFEE),self.price[-1])
        
        #    reset new last-buy price.
        self.lastBuy=self.price[-1]
        self.lastSell=9999        
        self.current_window = []

        # set all future values to current value
        self.btc[-1] = newBTC
        self.usd[-1] = newUSD
        
        # stores price, time and -1 for buys.
        # use -1 to summarize final status (raise to -1 power)
        if self.orders.size == 0:
            self.orders = np.array([[self.price[-1],self.time[-1],-1]])
        elif self.orders.size > 0:
            self.orders = np.concatenate([self.orders,np.array([[self.price[-1],self.time[-1],-1]])])
        # Placeholders
        if self.ALERT:   pass
        if self.EXECUTE: pass
    
    def sell(self,ALERT=False, EXECUTE=False):
        ''' 
        This function simulates selling BTC for USD
        Exchange ALL BTC for USD
        '''
        # These are temprorary amounts calculated before updating.
        newUSD = exchange_btc_to_usd(self.btc[-1]*(1-self.SELLFEE),self.price[-1])
        newBTC = 0
        
        # Set last sell in case price keeps increasing.
        self.lastSell=self.price[-1]
        self.lastBuy=-9999
        
        # change all future values
        self.btc[self.n] = newBTC
        self.usd[self.n] = newUSD
        self.current_window = []
        
        # stores price, time and -1 for buys.
        # use -1 to summarize final status (raise to 1 power)
        if self.orders.size == 0:
            self.orders = np.array([[self.price[-1],self.time[-1],1]])
        elif self.orders.size > 0:
            self.orders = np.concatenate([self.orders,np.array([[self.price[-1],self.time[-1],1]])])
        
        # Placeholders
        if self.ALERT:   pass
        if self.EXECUTE: pass

    def step_dev(self,price,time,backup=0):
        # update current price/time
        self.update_dev(price,time)
        
        # Check if evidence that price is currently at a minimum or maxmium
        # Execute theoretical trade at this point.
        self.check_current_extreme_dev()
        
        # update current worth based on current BTC and USD amounts
        self.current_worth.append(self.btc[-1]*self.price[-1] + self.usd[-1])
        
        # Placeholders
        # if backup = 1 --> update current profit summary
        # if backup = 2 --> update larger summary object [think what this is]
        if backup > 0:  pass
        if backup > 1:  pass

    def current_profit(self,start=0):
        ''' 
        quick calculation of current profit status 
        based off of self.orders list
        includes fees
        trade_type  = -1 for buys ($/price)
                    =  1 for sells ($*price)
        *** would be nice to find a way to window this to past X days or something
        '''
        profit_percent = 1
        for (price,date,trade_type) in self.orders:
            if date >= start:
                profit_percent = ((trade_type == -1) * (1-self.BUYFEE) + (trade_type == 1) * (1-self.SELLFEE)) * tmp * price**trade_type
        return profit_percent

    def add_usd(self,amt):
        ''' add money to simulation.'''
        self.usd[0]=amt

    def plot_trades(self,burn_in=30):
        ''' Display plots of price and approximate worth in dollars. '''
        yaxisFontSize = 15
        
        fig = plt.figure()
        ax1 =fig.add_subplot(211) 
        
        #print self.price
        
        buy_times=[i[1] for i in self.orders if i[2] == -1]
        sell_times=[i[1] for i in self.orders if i[2] == 1]
        
        # price curve
        #ax1.plot(self.time[burn_in:],self.price[burn_in:], 'b',linewidth=2)
        ax1.plot(self.time[burn_in:],self.price_smooth[burn_in:], 'b',linewidth=1)
        ax1.vlines(buy_times,0,2*max(self.price_smooth[burn_in:]),'g',linewidth=1)
        ax1.vlines(sell_times,0,2*max(self.price_smooth[burn_in:]),'r',linewidth=1)
        ax1.set_ylabel('USD/BTC',fontsize=yaxisFontSize )
        ax1.yaxis.tick_right()
        ax1.axis([min(self.time)-20000,max(self.time)+20000,min(self.price_smooth)-10,max(self.price_smooth)+10])
        
        # First derivative
        ax2 =fig.add_subplot(212) 
        ax2.plot(self.time[burn_in:],self.current_worth[burn_in:], 'b',linewidth=1)
        ax2.vlines(buy_times,0,2*max(self.current_worth[burn_in:]),'g',linewidth=1)
        ax2.vlines(sell_times,0,2*max(self.current_worth[burn_in:]),'r',linewidth=1)
        ax2.set_xlabel('TIME')
        ax2.set_ylabel('Current worth in USD',fontsize=yaxisFontSize )
        ax2.yaxis.tick_right()        
        ax2.axis([min(self.time)-20000,max(self.time)+20000,min(self.current_worth)-.05,max(self.current_worth)+.05])
        plt.show()
        
    def quickPlot(self,values,i,j):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(values[i:j])
        plt.show()





'''
datas= loadData(data='data/btce_basic_btc_usd_depth.pkl')
x = observer(5,20,60,0.005,0.05,0.05)
x.loadData(datas[0,0:100].tolist(),datas[1,0:100].tolist())
for i in range(100,len(datas[0,:])):
    x.step(datas[0,i],datas[1,i])

tmp = 1    
for (price,date,trade_type) in x.orders:
    tmp = 0.998*tmp*price**trade_type
x.plot_trades()
'''
