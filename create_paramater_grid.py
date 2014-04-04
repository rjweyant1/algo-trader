'''
Need to define the full grid somehow
'''    
import pickle
from common import *

#def create_grid():
fsmooths = [10]
fmas = [80]
fmds = [20,60,80]
fpercents = [0.01,0.02,0.05]
friseTols = [0.1]
flossTols = [0.05]

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
                    curID = getID(smooths=[s],mas=[a],mds=fmds,percents=[p],riseTols=[r],lossTols=[l])
                    print curID
                    with open('parameters-lists/params_'+curID+'.pkl','wb') as curFile:
                        pickle.dump([[s],[a],fmds,[p],[r],[l]],curFile)
