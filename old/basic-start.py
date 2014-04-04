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
    def __init__(self,price=None,n=500,numExtrema=3,shift=3,noise=0.09,lossTolerance=0.1, riseTolerance=0.1):
        if price == None:
            self.price= [ math.sin(numExtrema*i*math.pi/n) + random.normalvariate(0,noise) + shift for i in range(n) ]
        elif price != None:
            self.price = price
            n = len(price)
        self.n = n
        self.time = range(n)
        self.btc = [0 for i in range(n)]
        self.usd = [0 for i in range(n)]
        self.zero = [0 for i in range(n)]
        self.lastBuy = -9999
        self.lossTolerance = lossTolerance
        self.lastSell = 9999
        self.riseTolerance = riseTolerance
        self.orders=[0 for i in range(n)]
        
    def add_usd(self,amt,time=0):
        ''' add money to simulation.'''
        self.usd=[self.usd[i] for i in range(0,time)] + [self.usd[i] + amt for i in range(time,self.n)]
    def add_btc(self,amt,time=0):
        ''' add money to simulation.'''
        self.btc=[self.btc[i] for i in range(0,time)] + [self.btc[i] + amt for i in range(time,self.n)]
    def calc_derivatives(self,price_smoother=30,md_window=30,ma_window=30):
        ''' Find local derivatives and smooth using a MA. '''
        self.price_smooth = moving_average(self.price,price_smoother)
        print 'approx d1'
        self.d1=moving_derivative(self.price_smooth,self.time,md_window)
        print 'smooth d1'
        self.d1_smooth=moving_average(self.d1,ma_window)
        
        print 'approx d2'
        self.d2 = moving_derivative(self.d1,self.time,md_window)
        print 'smooth d2'
        self.d2_smooth = moving_average(self.d2,ma_window)

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


def iterate(mas=[20,40,80],
            mds=[10,20,40,80],
            percents=[0.005,0.01,0.02,0.03,0.04], 
            smoothers=[5,10,30], 
            riseTolerances=[0.01,0.05,0.1],
            lossTolerances=[0.01,0.05,0.1],
            data='/media/Big Daddy/New_Documents/python/python_projects/trading/data/btce_basic_btc_usd_depth.pkl'):
    ''' iterates through all possible combinations of a set of vectors and captures the end state '''
    (newPrice,newTime) = loadQuickData(data=data)
    parameters = []
    for ma_window in mas:
        for md_window in mds:
            for percent in percents:
                for smooth in smoothers:
                    for riseTol in riseTolerances:
                        for lossTol in lossTolerances:
                            x = test_set(price = newPrice)
                            x.calc_derivatives(price_smoother=smooth,md_window=md_window,ma_window=ma_window)
                            x.add_usd(amt=1,time=0)
                            x.find_extrema(percent=percent, burn_in=md_window+50)
                            btcs = [k for k in x.btc if k != 0][-1]
                            min_btc = min([k for k in x.btc if k != 0])
                            max_btc = max([k for k in x.btc if k != 0])
                            
                            usds = [k for k in x.usd if k != 0][-1]
                            min_usd = min([k for k in x.usd if k != 0])
                            max_usd = max([k for k in x.usd if k != 0])
                            
                            num_orders = len([i for i in x.orders if i != 0 ])
                            
                            parameters.append((num_orders,btcs,min_btc,max_btc,usds,min_usd,max_usd,ma_window,md_window,percent,smooth,riseTol,lossTol))
                            print parameters[-1]
                            del x
                            
    return np.array(parameters)




btc_data = iterate(mas=[20,40,60,100],
            mds=[10,20,40,100],
            percents=[0.005,0.01,0.02,0.03,0.06,0.08], 
            smoothers=[5,10,30,60], 
            riseTolerances=[0.01,0.05,0.1],
            lossTolerances=[0.01,0.05,0.1],
            data='/media/Big Daddy/New_Documents/python/python_projects/trading/data/btce_basic_btc_usd_depth.pkl')
ltc_data = iterate(mas=[20,40,60,100],
            mds=[10,20,40,100],
            percents=[0.005,0.01,0.02,0.03,0.06,0.08], 
            smoothers=[5,10,30,60], 
            riseTolerances=[0.01,0.05,0.1],
            lossTolerances=[0.01,0.05,0.1],
            data='/media/Big Daddy/New_Documents/python/python_projects/trading/data/btce_basic_ltc_usd_depth.pkl')         
ltc_btc_data = iterate(mas=[20,40,60,100],
            mds=[10,20,40,100],
            percents=[0.005,0.01,0.02,0.03,0.06,0.08], 
            smoothers=[5,10,30,60], 
            riseTolerances=[0.01,0.05,0.1],
            lossTolerances=[0.01,0.05,0.1],
            data='/media/Big Daddy/New_Documents/python/python_projects/trading/data/btce_basic_ltc_btc_depth.pkl')            
# 0=n, 1=btcs, 2=min btcs 3=max_btc 4=usds 5=min usd 6=max usd 7=ma window 8=md window 9=percent 10=smooth 11=riseTol 12=lossTol
for i in range(5,12):
    print i
    plt.plot(btc_data[:,4],btc_data[:,i],'ro')
    plt.axis([min(btc_data[:,4])*0.9,max(btc_data[:,4])*1.1,min(btc_data[:,i])*0.9,max(btc_data[:,i])*1.1])
    plt.show()


def basicStart():
    # load data
    (newPrice,newTime) = loadQuickData(data='/media/Big Daddy/New_Documents/python/python_projects/trading/data/btce_basic_btc_usd_depth.pkl')

    # how smooth things are
    md_window = 40
    ma_window = 40
    price_smoother = 30
    percent = 0.01
    x = test_set(price=newPrice)
    # start 
    x.calc_derivatives(price_smoother=price_smoother,md_window=md_window,ma_window=ma_window)
    x.add_usd(amt=1,time=0)
    x.find_extrema(percent=percent, burn_in=md_window+50)
    x.plot()


def olditerate():
    start = 5
    num_evals = 5
    scale = 4
    
    usds = np.zeros(shape=(num_evals,num_evals))
    btcs = np.zeros(shape=(num_evals,num_evals))
    mds = np.zeros(shape=(num_evals,num_evals))
    mas = np.zeros(shape=(num_evals,num_evals))
    
    #for ma_window in [20*i for i in range(1,30)]:
    for i in range(0 ,num_evals ):
        for j in range(0 ,num_evals ):
            print i,j
            ma_window = (i+start)*scale
            md_window = (j+start)*scale
            mds[i][j]=md_window
            mas[i][j]=ma_window
            
            x = test_set(price=newPrice)
            # start 
            x.calc_derivatives(md_window=md_window,ma_window=ma_window)
            x.add_usd(amt=1,time=0)
            x.find_extrema(50)
            btcs[i][j] = [k for k in x.btc if k != 0][-1]
            usds[i][j] = [k for k in x.usd if k != 0][-1]
            del x
        #x.plot(burn_in=50)
    
    x = range(start+scale,start+num_evals*scale+1,scale)
    y = range(start+scale,start+num_evals*scale+1,scale)
    X,Y = np.meshgrid(x,y)
    Z = usds
    
    # Or you can use a colormap to specify the colors; the default
    # colormap will be used for the contour lines
    
    CS = plt.contour(X,Y,Z)
    plt.clabel(CS, inline=1, fontsize=10)
    plt.show()
        

def oldTestData():
    #testPrice = [ math.sin(numExtrema*i*math.pi/n) + random.normalvariate(0,noise) + shift for i in range(n) ]
    numExtrema=5
    noise = 10
    n = 500
    shift = 800
    n2 = 600
    multiplier = 200
    
    basicCurve = [ multiplier *math.sin(numExtrema*i*math.pi/n) + random.normalvariate(0,noise) + shift  for i in range(n)]
    basicAndDown = basicCurve[0:385]+ [shift-0.5*multiplier  - multiplier*float(i)/n2 - multiplier*math.sin(i*math.pi/200)+ random.normalvariate(0,noise) for i in range(n2)]
    
    #realData = loadData(data='/media/Big Daddy/New_Documents/python/python_projects/trading/data/ltc_btc_depth.pkl')
    #realPrice = [float(i.buy) for i in realData 
    #print realPrice
