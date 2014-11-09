########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : DiameterEventCount.py
# Domain : Tools
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
from cStringIO import StringIO

import firebolt.Utils.DiameterUtils as utils


def getCount(FileName = None):
    if FileName == None:
        return True

    try:
        fd = open(FileName, "rb")
    except Exception, e:
        print "ERROR: {0}".format(str(e))
        return False

    fileSize = os.path.getsize(FileName) 
    try:
        [part_1, ext] = os.path.basename(FileName).split('.')
    except Exception, e:
        print "Provide some extension to the file"
        sys.exit(1)

    eventCount= 0  
    fileCount = 1

    while True: 
        # Read first 4 bytes of diameter event(which is part of 20 byte header)
        [msgLen, _version] = utils.getFlagAndLength(fd.read(4)) 
        # move back by 4 bytes
        fd.seek(-4, 1) 
        data = fd.read(msgLen)
        eventCount += 1

        curSize = fd.tell()
        if fileSize == curSize:
            break
        
    fd.close()

    return eventCount

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python DiameterEventCount.py <Diameter File>"
        print "Example: "
        print "python DiameterEventCount.py TCUSAGE_VOC_23_08_2013.dat"
        sys.exit(0)
        
    fileName = sys.argv[1]

    count = getCount(fileName)

    print "Number Of Events in the File : {0}".format(count)
