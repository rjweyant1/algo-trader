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
    def __init__(self,smooth,md,ma,percent,lossTolerance=0.1, riseTolerance=0.1):
        self.n = 0
        self.btc = [0]
        self.usd = [1]
        self.current_worth = [1]
        self.zero = []
        self.smooth=smooth
        self.md = md
        self.ma = ma
        self.percent=percent
        self.lossTolerance = lossTolerance
        self.riseTolerance = riseTolerance
        self.orders=np.array([])
        self.lastBuy = -9999
        self.lastSell = 9999
        self.BUYFEE = 0.002
        self.SELLFEE = 0.002
        self.ALERT = False
        self.EXECUTE = False

        
    def loadData(self,price,time):
        ''' 
        loads price/time from lists 
        '''
        # initial load
        self.price = price
        self.time = time
        
        # smoothing
        self.price_smooth = moving_average(self.price,self.smooth)
        self.d1 = moving_derivative(self.price_smooth,self.time,self.md)
        self.d1_smooth = moving_average(self.d1,self.ma)
        self.d2 = moving_derivative(self.d1,self.time,self.md)
        self.d2_smooth = moving_average(self.d2,self.ma)
        self.n = len(self.price)-1
        
        # move starting btc and usd forward
        self.btc = self.btc*(self.n+1)
        self.usd = self.usd*(self.n+1)
        self.current_worth = (np.array(self.btc)*np.array(self.price) + np.array(self.usd)).tolist()

    def update(self,price,time):
        '''
        Given a single price/time pair, this updates the data set 
        '''
        self.price.append(price)
        self.time.append(time)
        self.btc.append(self.btc[self.n])
        self.usd.append(self.usd[self.n])
        self.n=self.n+1
        
        # do something about real time !!!
        
        # update price, derivatives and smooth functions
        # only look at last window.
        self.price_smooth.append(mean(self.price[self.n-self.smooth:]))
        self.d1.append(get_slope(self.price_smooth[self.n-self.md:],self.time[self.n-self.md:]))
        self.d1_smooth.append(mean(self.d1[self.n-self.ma:]))
        self.d2.append(get_slope(self.d1_smooth[self.n-self.md:],self.time[self.n-self.md:]))
        self.d2_smooth.append(mean(self.d2[self.n-self.ma:]))
        
    def check_current_extreme(self):
        ''' 
        Identify if the CURRENT price shows evidence of a minimum or maximum.
        Also checks if an apparent previous execution was premature (SAFEGUARD)        
        '''

        # CHECK IF LAST D1 WAS NEGATIVE AND CURRENT D1 IS POSITIVE 
        # AND THE PRICE HAS DECREASED BY A CERTAIN PERCENT SINCE LAST SELL
        # also requires that number of dollars is positive -- as in the last action was a SELL
        if self.d1_smooth[self.n-1] <0 and self.d1_smooth[self.n] >0 and self.price[self.n] < (1-self.percent)*self.lastSell and self.usd[self.n-1] > 0:
            print 'Buy\t', round(self.lastSell,1),round(self.price[self.n],1)
            self.buy()
            
        # CHECK IF LAST D1 IS POSITIVE AND CURRENT D1 IS NEGATIVE
        # AND THE PRICE HAS INCREASED BY A CERTAIN PERCENT SINCE LAST BUY
        # also requires that number of BTC is positive -- as in last action was a BUY
        elif self.d1_smooth[self.n-1]>0 and self.d1_smooth[self.n]<0 and self.price[self.n] > (1+self.percent)*self.lastBuy and self.btc[self.n-1]>0:
            print 'Sell\t', round(self.lastBuy,1), round(self.price[self.n],1)
            self.sell()

        #### SAFE GUARDS -- RISK TOLERANCE ####
        # if we dip below our risk tolerance, sell.
        elif self.price_smooth[self.n] < (1-self.lossTolerance)*self.lastBuy and self.btc[self.n-1]>0:
            print 'BOUGHT at %s and price is now %s Still going down, SELLING' % (round(self.lastBuy,1),round(self.price[self.n],1))
            self.sell()

        # if the price keeps going up after peak, then buy?
        # I have not seen evidence of this happening, and actually acting on it seems slightly harder to implement.
        elif self.price_smooth[self.n]>(1+self.riseTolerance)*self.lastSell and self.usd[self.n-1]>0:
            print 'SOLD at %s and price is now %s Still going up, BUYING' % (round(self.lastSell,1),round(self.price[self.n],1))
            self.buy()

    # somehow use macd to make calls
    # need to figure this out            
    def macd_eval(self):
        pass
    
    # placeholder for a high-frequency strategy
    # idea is to buy and then sell for a small amount above price+fee
    # then buy again at a small amount-fee
    def high_freq_eval(self):
        pass
        
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
        
        # stores price, time and -1 for buys.
        # use -1 to summarize final status (raise to -1 power)
        if self.orders.size == 0:
            self.orders = np.array([[self.price[self.n],self.time[self.n],-1]])
        elif self.orders.size > 0:
            self.orders = np.concatenate([self.orders,np.array([[self.price[self.n],self.time[self.n],-1]])])
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
        
        # stores price, time and -1 for buys.
        # use -1 to summarize final status (raise to 1 power)
        if self.orders.size == 0:
            self.orders = np.array([[self.price[self.n],self.time[self.n],1]])
        elif self.orders.size > 0:
            self.orders = np.concatenate([self.orders,np.array([[self.price[self.n],self.time[self.n],1]])])
        
        # Placeholders
        if self.ALERT:   pass
        if self.EXECUTE: pass

    def step(self,price,time,backup=0):
        # update current price/time
        self.update(price,time)
        
        # Check if evidence that price is currently at a minimum or maxmium
        # Execute theoretical trade at this point.
        self.check_current_extreme()
        
        # update current worth based on current BTC and USD amounts
        self.current_worth.append(self.btc[self.n]*self.price[self.n] + self.usd[self.n])
        
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
        ax1.plot(self.time[burn_in:],self.price[burn_in:], 'b',linewidth=2)
        ax1.plot(self.time[burn_in:],self.price_smooth[burn_in:], 'b',linewidth=4)
        ax1.vlines(buy_times,0,2*max(self.price[burn_in:]),'g',linewidth=1)
        ax1.vlines(sell_times,0,2*max(self.price[burn_in:]),'r',linewidth=1)
        ax1.set_ylabel('USD/BTC',fontsize=yaxisFontSize )
        ax1.yaxis.tick_right()
        ax1.axis([min(self.time)-20000,max(self.time)+20000,min(self.price)-10,max(self.price)+10])
        
        # First derivative
        ax2 =fig.add_subplot(212) 
        ax2.plot(self.time[burn_in:],self.current_worth[burn_in:], 'b',linewidth=4)
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
