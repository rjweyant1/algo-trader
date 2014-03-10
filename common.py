#!/usr/bin/python

'''
The point of this code is to maintain common functions that are required for 
the algorithm, but don't belong in any of the classes.


'''

from scipy import stats
import numpy as np
from numpy import mean
import math
import random
import matplotlib.pyplot as plt
from trades import trades
import time
import pickle
import matplotlib.cm as cm

def loadData(data = 'data/btce_basic_btc_usd_depth.pkl'):
    '''
    loads a csv of the format pair,time,price
      where pair is of the form currency_currency
      e.g. btc_usd, ltc_usd, ltc_btc
      which isn't really important for anything
    '''
    historical = open(data,'rb')

    # initialize lists    
    price_data = []
    time_data = []
    
    for line in historical:
        # get values
       (pair,mktime,price)= line.split(',')
       price_data.append(price)
       time_data.append(mktime)
    
    # cast as floats rather than strings
    price_data=[float(i.strip()) for i in price_data]
    time_data = [float(i.strip()) for i in time_data]
    
    # Maybe the dimensions should be fixed on this?
    return np.array([price_data,time_data])
    
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
