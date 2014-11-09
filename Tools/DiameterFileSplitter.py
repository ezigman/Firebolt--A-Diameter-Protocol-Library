########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : DiameterFileSplitter.py
# Domain : Tools
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
from cStringIO import StringIO

import firebolt.Utils.DiameterUtils as utils


def splitter(FileName = None, CountPerFile = None):
    if FileName == None or CountPerFile == None:
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

    print part_1
   
    eventCount= 0  
    fileCount = 1
    nFd = open(part_1 + "_{0}.{1}".format(fileCount, ext), "wb")

    while True: 
        # Read first 4 bytes of diameter event(which is part of 20 byte header)
        [msgLen, _version] = utils.getFlagAndLength(fd.read(4)) 
        # move back by 4 bytes
        fd.seek(-4, 1) 
        data = fd.read(msgLen)
        eventCount += 1

        if eventCount <= CountPerFile:
            nFd.write(data)     
        else:
            nFd.close()
            eventCount = 1
            fileCount += 1
            nFd = open(part_1 + "_{0}.{1}".format(fileCount, ext), "wb")
            nFd.write(data)


        curSize = fd.tell()
        if fileSize == curSize:
            break
        
    fd.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: python DiameterFileSplitter.py <Diameter File> <Count per File>"
        print "Example: "
        print "python DiameterFileSplitter.py TCUSAGE_VOC_23_08_2013.dat 5"
        sys.exit(0)
        
    fileName = sys.argv[1]
    count    = int(sys.argv[2])

    splitter(fileName, count)
