#!/usr/bin/python

'''
This class follows manages several observer classes...
need something more helpful here
'''
from observer import *
from common import *

import pickle
import time
import os.path

class overlord:
    # constructor
    def __init__(self,smooths=[],mas=[],mds=[],percents=[],riseTols=[],lossTols=[],historical_data='data/test_data.txt'):
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

        self.getID()


    def getID(self):
        min_mas,max_mas,len_mas = (str(min(self.mas)),str(max(self.mas)),str(len(self.mas)))
        min_mds,max_mds,len_mds = (str(min(self.mds)),str(max(self.mds)),str(len(self.mds)))
        min_smooths,max_smooths,len_smooths = (str(min(self.smooths)),str(max(self.smooths)),str(len(self.smooths)))
        min_precents,max_percents,len_percents = (str(min(self.percents)),str(max(self.percents)),str(len(self.percents)))
        min_rise, max_rise,len_rise = (str(min(self.riseTols)),str(max(self.riseTols)),str(len(self.riseTols)))
        min_loss,max_loss,len_loss = (str(min(self.lossTols)),str(max(self.lossTols)),str(len(self.lossTols)))
        
        tmp_id = len_mas+min_mas+max_mas+min_mds+max_mds+len_mds+min_smooths+max_smooths+len_smooths +min_precents+max_percents+len_percents +min_rise+ max_rise+len_rise +min_loss+max_loss+len_loss 
        self.id = str(self.numWorkers) + tmp_id.replace('.','')
        
        
    def initializeWorkers(self):
        '''
        initializes workers from scratch
        '''
        # creates 7 dimensional array
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
        pass

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
        # append?
        with open('results/short_status_'+self.id+'.txt','w') as quick_file:
            for key in self.workers.keys():
                line = str(self.workers[key].time[-1])+','+','.join([str(i) for i in key])+','+str(self.workers[key].current_worth[-1])+'\n'
                quick_file.write(line)
    def fullBackup(self):
        '''
        writes the full overlord object, with all the historical data
        '''
        with open('results/full_backup_'+self.id+'.pkl','wb') as full_backup:
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
        if float(time) != self.curTime:
            self.curTime = float(time)             # new time = current time
            self.updateWorkers(float(price),float(time))  # update everyone
        
    def continuous_run(self,wait_time = 60, cycle_length = 60, load=False):
        '''
        continuously update this overlord's workers
        '''
        i = cycle_length
        while True:
            self.updatePrice()
            
            # Every 10 minutes make a 'quick' update
            if i % 10 == 0:
                print 'Quick Update'
                self.quickBackup()
            # every hour make a full backup
            if i == 0:
                print 'Full Update'
                self.fullBackup()
                i = cycle_length
            i = i-1
            # sleep 1 minute
            time.sleep(wait_time)

def getID(smooths,mas,mds,percents,riseTols,lossTols):
    min_mas,max_mas,len_mas = (str(min(mas)),str(max(mas)),str(len(mas)))
    min_mds,max_mds,len_mds = (str(min(mds)),str(max(mds)),str(len(mds)))
    min_smooths,max_smooths,len_smooths = (str(min(smooths)),str(max(smooths)),str(len(smooths)))
    min_precents,max_percents,len_percents = (str(min(percents)),str(max(percents)),str(len(percents)))
    min_rise, max_rise,len_rise = (str(min(riseTols)),str(max(riseTols)),str(len(riseTols)))
    min_loss,max_loss,len_loss = (str(min(lossTols)),str(max(lossTols)),str(len(lossTols)))
    
    numWorkers = len(mas)*len(mds)*len(smooths)*len(percents)*len(riseTols)*len(lossTols)
    tmp_id = len_mas+min_mas+max_mas+min_mds+max_mds+len_mds+min_smooths+max_smooths+len_smooths +min_precents+max_percents+len_percents +min_rise+ max_rise+len_rise +min_loss+max_loss+len_loss 
    id = str(numWorkers) + tmp_id.replace('.','')
    return id

def loadOverlord(smooths,mas,mds,percents,riseTols,lossTols):
    '''
    check for backup, if it doesn't exist, load from scratch
    '''
    # what ID will be with this parameter set
    curID = getID(smooths,mas,mds,percents,riseTols,lossTols)
    print curID
    backupName = 'results/full_backup_'+curID+'.pkl'

    # Check for backup
    if os.path.isfile(backupName):
        print 'Loading from backup'
        with open(backupName,'rb') as backup:
            curObj = pickle.load(backup)
            print curObj.id
    # else create new object
    else:   
        print 'Creating new overlord object'
        curObj = overlord(smooths=smooths,mas=mas,mds=mds,percents=percents,riseTols=riseTols,lossTols=lossTols)    
        print curObj.id
        curObj.initializeWorkers()
    
    return curObj
    
    

        
x = loadOverlord(   smooths = [5],
                    mas=[20],
                    mds=[20],
                    percents=[0.005],
                    riseTols=[0.01],
                    lossTols=[0.005]
                )        

x.continuous_run(10,2)


#x.workers[x.workers.keys()[-1]].plot_trades()

#for key in x.workers.keys():
#    x.workers[key].plot_trades()

