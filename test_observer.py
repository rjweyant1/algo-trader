#!/usr/bin/python

'''
This is just a functional test of observer class
'''

# These are the modules created for this project
from observer import *
from common import *

# Load data
datas= loadData(data='data/test_data.txt')
#datas= loadData(data='data/btc_usd_btce.txt')
    
# Not a best performing parameter set -- highlights potential problems
# Might show that something is not working as intended .
#               ma md  smooth    percent   riseTol lossTol
# current best: 100 40  10          0.1     0.7     0.1
x = observer(smooth=10,md=40,ma=100,percent=0.1,riseTolerance=0.7,lossTolerance=0.1)

# Start with the first 100 points in the set
x.loadData(datas[0,0:100].tolist(),datas[1,0:100].tolist())

# "step" through the rest.
for i in range(100,len(datas[0,:])):
    x.step(datas[0,i],datas[1,i])

# Make a plot
#x.plot_trades()as
