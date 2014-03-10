#!/usr/bin/python

'''
This is just a functional test of observer class
'''

# These are the modules created for this project
from observer import *
from common import *

# Load data
datas= loadData(data='data/btce_basic_btc_usd_depth.pkl')

# Not a best performing parameter set -- highlights potential problems
# Might show that something is not working as intended .
x = observer(10,20,60,0.01,0.05,0.05)

# Start with the first 100 points in the set
x.loadData(datas[0,0:100].tolist(),datas[1,0:100].tolist())

# "step" through the rest.
for i in range(100,len(datas[0,:])):
    x.step(datas[0,i],datas[1,i])

# Make a plot
x.plot_trades()
