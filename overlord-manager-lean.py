from overlord import *
from observer import *
from common import *

import os.path
import sys, getopt

def main(argv):        
    param_dir = ''
    # Accept command line argument -i
    try:
        opts, args = getopt.getopt(argv,'hi:o',['ifile='])
    except getopt.GetoptError:
        print 'Usage: overlord.py -i <parameter-directory>'
        sys.exit(2)
    for opt,arg in opts:
        if opt == '-h':
            print 'Usage: overlord.py -i <parameter-directory>'
            sys.exit()
        elif opt in ('-i','--ifile'):
            param_dir=arg.strip().replace(' ','')
        
    #print 'Input file is ', param_dir
    if param_dir != '' and os.path.exists(param_dir):
        param_files = [i for i in os.listdir(param_dir) if 'pkl' in i and 'param' in i]
        overlords = []
        
        print '\n\n\n\n\n\n\n\n\n\n\n==============================================='
        print '   Starting data load. Managing %s overlords.' % len(param_files)
        print '===============================================\n\n\n'
        i = 0
        # Load all overlords
        for param_f in param_files:
            i=i+1
            print 'Running overlord %s of %s' % (i,len(param_files))
            loadOverlord(parmFile=param_dir+'/'+param_f,fullBackup=True)
            print '======================================\n'

            
    else: 
        print 'File does not exist!'   
        print len(param_dir)
        sys.exit()


if __name__=='__main__':
    # send command line args to main
    main(sys.argv[1:])        