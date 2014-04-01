import os

param_sets = os.listdir(os.curdir+'/parameters-lists/')

out = open('submitter.sh','w')
for curSet in param_sets:
    if 'pkl' in curSet :
        newLog = 'logs/'+curSet[7:-3]+'log'
        newErr = 'logs/'+curSet[7:-3]+'err'

        #line='nohup /usr/bin/python overlord-manager.py -i parameters-lists/%s > %s 2> %s  \n' % (curSet,newLog, newErr)
        curLine='/usr/bin/python overlord-manager.py -i parameters-lists/%s\n' % (curSet)
        out.write(curLine)
        