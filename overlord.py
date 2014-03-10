#!/usr/bin/python

'''
This class follows manages several observer classes...
need something more helpful here
'''
from observer import *
from common import *
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



class overlord:
    # constructor
    def __init__(self,smooths=[],mas=[],mds=[],percents=[],riseTols=[],lossTols=[]):
        self.mas = mas
        self.mds = mds
        self.smooths = smooths
        self.percents = percents
        self.riseTols = riseTols
        self.lossTols = lossTols
        
        n_mas = len(mas)
        n_mds = len(mds)
        n_smooths = len(smooths)
        n_percents = len(percents)
        n_riseTols = len(riseTols)
        n_lossTols = len(lossTols)
        
        numWorkers= n_mas*n_mds*n_smooths*n_percents*n_riseTols*n_lossTols
    
        # print 
        self.price_data= loadData(data='data/btce_basic_btc_usd_depth.pkl') 

    def initializeWorkers(self):
        '''
        initializes workers from scratch
        '''
        # creates 7 dimensional array
        ## Xworkers X=X np.empty((n_mas,n_mds,n_smooths,n_percents,n_riseTols,n_lossTols,7))
        # initializes dictionary for monitoring.
        workers = dict()
        for ma in mas:
            for md in mds:
                for smooth in smooths:
                    for percent in percents:
                        for riseTol in riseTol:
                            for lossTol in lossTol:
                                workers[(ma,md,smooth,percent,riseTol,lossTol)] = observer(smooth,md,ma,percent,lossTol,riseTol)
                                workers[(ma,md,smooth,percent,riseTol,lossTol)].loadData(price_data[0,0:100].tolist(),price_data[1,0:100].tolist())
                                
                                for i in range(100,len(datas[0,:])):
                                    x.step(datas[0,i],datas[1,i])

    def loadWorkers(self):  
        '''
        Loads Workers from backups
        '''
        pass
        