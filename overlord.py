#!/usr/bin/python

'''
This class follows manages several observer classes...
need something more helpful here
'''
from observer import *
from common import *

import pickle
import time


class overlord:
    # constructor
    def __init__(self,smooths=[],mas=[],mds=[],percents=[],riseTols=[],lossTols=[],historical_data='data/btce_basic_btc_usd_depth.pkl'):
        self.mas = mas
        self.mds = mds
        self.smooths = smooths
        self.percents = percents
        self.riseTols = riseTols
        self.lossTols = lossTols
        
        self.workers = dict()       # blank
        self.curTime = 0
        
        n_mas = len(mas)
        n_mds = len(mds)
        n_smooths = len(smooths)
        n_percents = len(percents)
        n_riseTols = len(riseTols)
        n_lossTols = len(lossTols)
        
        self.numWorkers= n_mas*n_mds*n_smooths*n_percents*n_riseTols*n_lossTols
    
        self.price_data= loadData(data=historical_data) 

        self.id = 'id'

    def initializeWorkers(self):
        '''
        initializes workers from scratch
        '''
        # creates 7 dimensional array
        ## Xworkers X=X np.empty((n_mas,n_mds,n_smooths,n_percents,n_riseTols,n_lossTols,7))
        # initializes dictionary for monitoring.
        
        for ma in self.mas:
            for md in self.mds:
                for smooth in self.smooths:
                    for percent in self.percents:
                        for riseTol in self.riseTols:
                            for lossTol in self.lossTols:
                                curKey = (ma,md,smooth,percent,riseTol,lossTol)
                                # initialize
                                self.workers[curKey ] = observer(smooth,md,ma,percent,lossTol,riseTol)
                                
                                # take the first 100 points in data file
                                self.workers[curKey].loadData(self.price_data[0,0:100].tolist(),self.price_data[1,0:100].tolist())
                                
                                # cycle over the rest of the historical data
                                for i in range(100,len(self.price_data[0,:])):
                                    self.workers[curKey].step(self.price_data[0,i],self.price_data[1,i])

    def loadWorkers(self):  
        '''
        Loads Workers from backups
        '''
        

    def updateWorkers(self,price,time):
        '''
        updates each worker under this overlord's control
        '''
       
        # cycle through each worker, do 1-step for current (price,time)
        for key in self.workers.keys():
            self.workers[key].step(price,time)

    def quickBackup(self):            
        ''' 
        write out a file that has parameter list + windowd profits and total profit 
        '''
        quick_file = open('short_status_'+self.id+'.txt','w')
        for key in self.workers.keys():
            line = str(self.workers[key].time[-1])+','+','.join([str(i) for i in key])+','+str(self.workers[key].current_worth[-1])+'\n'
            quick_file.write(line)
    def fullBackup(self):
        '''
        writes the full overlord object, with all the historical data
        '''
        full_backup = open('full_backup_'+self.id+'.pkl','wb')
        pickle.dump(self,full_backup)

    def updatePrice(self):
        '''
        checks for a new price, and if it's new, update all workers
        '''
        # load new data file
        tmp_data = open('data/btc_usd_btce.tmp','r')
        for line in tmp_data:
            (pair,time,price) = line.split(',')
        
        # If the current time is new, then update
        if time != self.curTime:
            self.curTime = time             # new time = current time
            self.updateWorkers(price,time)  # update everyone
        
    def continuous_run(self,load=False):
        '''
        continuously update this overlord's workers
        '''
        i = 60
        while True:
            self.updatePrice()
            
            # Every 10 minutes make a 'quick' update
            if i % 10 == 0:
                self.quickBackup()
            # every hour make a full backup
            if i == 0:
                self.fullBackup()
                i = 60
            i = i-1
            # sleep 1 minute
            time.sleep(60)

        
x = overlord(   smooths = [10],
                mas=[20],
                mds=[20],
                percents=[0.015],
                riseTols=[0.01],
                lossTols=[0.005]
             )        
x.initializeWorkers()

#x.workers[x.workers.keys()[-1]].plot_trades()

#for key in x.workers.keys():
#    x.workers[key].plot_trades()

