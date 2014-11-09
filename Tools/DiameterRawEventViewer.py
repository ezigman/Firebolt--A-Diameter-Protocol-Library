########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : DiameterRawEventViewer.py
# Domain : Tools
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
import struct
import binascii

import firebolt.Utils.DiameterUtils as utils
import firebolt.Lib.decoders as decoder

def parser(fd):
    #fd = open(fileName, "rb")
    # Read first 4 bytes of diameter event(which is part of 20 byte header)
    fd.seek(0)
    [msgLen, _version] = utils.getFlagAndLength(fd.read(4)) 
    print "Total Message Length in header: {0}".format(msgLen)

    [commandCode, flags] = utils.getFlagAndLength(fd.read(4))
    print "Command Code : {0}".format(commandCode)
    
    print ""
    ## Move past remaining header
    _rest = fd.read(12)

    bytes_read = 20

    print "====================================================================================================="
    print "   AVP_CODE       AVP_FLAGS      AVP_LENGTH         AVP_VALUE                           AVP_VALUE(hex)"
    print "====================================================================================================="

    while bytes_read < msgLen:
        fmt = struct.Struct('>I')
        try:
            (avp,) = fmt.unpack(fd.read(4))
        except Exception, e:
            print "Error while parsing AVP Code."
            print "Parsed till {0} bytes".format(bytes_read)

        [avpLen, avpFlags] = utils.getFlagAndLength(fd.read(4))

        avpLenPadded = avpLen + utils.calculatePadding(avpLen)

        diff = 8
        vendorID = 0
        if utils.existVendorID(avpFlags):
            _rest = fd.read(4)
            vendorID = decoder.uint32Decoder(_rest)
            diff = 12

        raw_data = fd.read(avpLenPadded - diff)
        len_diff = avpLen - diff

        if len_diff == 4:
            [avp_value, len] = decoder.uint32Decoder(raw_data) 
        elif len_diff == 8:
            [avp_value, len] = decoder.uint64Decoder(raw_data)
        else:
            fmt = struct.Struct('{0}s'.format(avpLenPadded - diff))
            (avp_value,) = fmt.unpack(raw_data)

        avp_val_hex = binascii.hexlify(raw_data)

        #print ">> {0:7}       {1:9}[{2:5}]      {3:10}         {4:9}                           {5}".format(avp, avpFlags, vendorID, avpLen, avp_value, avp_val_hex)
        print ">> {0:7}       {1:9}     {2:10}         {3:9}                           {4}".format(avp, avpFlags, avpLen, avp_value, avp_val_hex)
        #print "-"*80
        bytes_read += avpLenPadded

    
    fd.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "For those who cannot wait till event structure is configured.\n"
        print "Usage: python DiameterRawEventViewer.py <Diameter File>"
        sys.exit(1)
    fd = open(sys.argv[1], "rb")	
    parser(fd)
