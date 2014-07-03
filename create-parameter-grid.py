'''
Need to define the full grid somehow
'''    
import pickle
from common import *

#def create_grid():

fsmooths = [1,5]
fmas = [40,80,]
fmds = [40,80]
fpercents = [0.01,0.02,0.03]
friseTols = [0.05,0.1,0.15]
flossTols = [0.05,0.1]
'''
fsmooths = [10]
fmas = [60]
fmds = [20,60]
fpercents = [0.02]
friseTols = [0.1]
flossTols = [0.1]
'''

smooths=[]
mas=[]
mds=[]
percents=[]
riseTols=[]
lossTols=[]
full_list=[]
for r in friseTols:
   for l in flossTols:
        for s in fsmooths:
            for a in fmas:
                for p in fpercents:
                    for d in fmds:
                        curID = getID(smooths=[s],mas=[a],mds=[d],percents=[p],riseTols=[r],lossTols=[l])
                        print curID
                        with open('parameters-lists/params_'+curID+'.pkl','wb') as curFile:
                            pickle.dump([[s],[a],[d],[p],[r],[l]],curFile)



# make a spazzy one
'''
curID = getID(smooths=[10],mas=[10],mds=[10],percents=[0.001],riseTols=[0.001],lossTols=[0.001])
print curID
with open('parameters-lists/params_'+curID+'.pkl','wb') as curFile:
    pickle.dump([[10],[10],[10],[0.001],[0.001],[0.001]],curFile)
'''    