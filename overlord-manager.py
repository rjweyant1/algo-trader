from overlord import *
from observer import *
from common import *

import os.path
import sys, getopt

def main(argv):        
    inputfile = ''
    # Accept command line argument -i
    try:
        opts, args = getopt.getopt(argv,'hi:o',['ifile='])
    except getopt.GetoptError:
        print 'Usage: overlord.py -i <inputfile>'
        sys.exit(2)
    for opt,arg in opts:
        if opt == '-h':
            print 'Usage: overlord.py -i <inputfile>'
            sys.exit()
        elif opt in ('-i','--ifile'):
            inputfile=arg
        
    print 'Input file is ', inputfile
    if inputfile != '' and os.path.isfile(inputfile):
        
        x = loadOverlord(parmFile=inputfile)        
        profits = [x.workers[i].current_worth[-1] for i in x.workers.keys()]
        x.continuous_run(60,6)
    else: 
        print 'File does not exist.'        
        sys.exit()


if __name__=='__main__':
    # send command line args to main
    main(sys.argv[1:])        