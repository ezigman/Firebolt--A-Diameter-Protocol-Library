########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : GenericDiameterMsgParser.py
# Domain : Library
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
import struct

import firebolt.Lib.DiameterGroup as Node
import firebolt.Utils.DiameterUtils as utils
import firebolt.Config.MasterAVPDict as avpConfig

from cStringIO import StringIO


"""
@class: ParsedData
@desc : States the result of parsing an AVP
"""
class ParsedData:
    def __init__(self):
        self.isParsed = False
        self.vendorID = None
        self.avpSize  = None
        self.padding  = None



"""
@class: GenericDiameterMsgParser
@desc : Provides functions which helps in 
        parsing diameter binary events by AVP code.
"""
class GenericDiameterMsgParser:
    """
        Constructor receives diameter binary data and its
        corresponding size as input parameters.
    """
    def __init__(self, inputEvent, inputEventSize):
        self.nwBuffer = StringIO()
        self.nwBuffer.write(inputEvent)
        self.nwEventSize = inputEventSize
        ## Seek off 20 bytes diameter Header
        self.nwBuffer.seek(utils.DIAMETER_HEADER_SIZE)


    """
        Sets the network buffer to a specific location 
        within the buffer boundary.
    """
    def setNetworkBufferPosition(self, bytes = 0):
        self.nwBuffer.seek(bytes) 


    """
        Resets the nwBuffer right after the diameter
        header. Usually called after parsing every 
        Diameter atom (simple AVP).
    """
    def resetBuffer(self):
        self.setNetworkBufferPosition(0)
        ## Move past diameter header
        self.setNetworkBufferPosition(utils.DIAMETER_HEADER_SIZE)



    """
        Function called within getElement interface function.
        It iterates over the nwBuffer/diameter event till it
        finds the AVP code .
        If AVP is found, places the nwBuffer, right after the 
        AVP header.
        Returns 'ParsedData' as output.

        IMP NOTE: for clients of this class member
        ---------
        ParsedData.isParsed must be checked, before trying
        to read from the buffer.
    """
    def findSimpleElementLocation(self, avpCode, msgSize):
        codeFound = False
        size = self.nwBuffer.tell() #bytes

        o_ParsedData = ParsedData()

        while (size < msgSize) and not codeFound:
            #print "DEBUG: {0} : {1} : {2}".format(size, msgSize, self.nwBuffer.tell())
            # read the AVP Code
            fmt = struct.Struct('>I')
            try:
                (avp,) = fmt.unpack(self.nwBuffer.read(4))
            except Exception, e:
                print "ERROR: Major formatting Issue {0}. Exception : {1}".format(avpCode, str(e))
                return o_ParsedData

            if avp == avpCode:
                codeFound = True

            ## Flags And Length
            [avpLen, avpFlags] = utils.getFlagAndLength(self.nwBuffer.read(4))
            avpLenPadded = avpLen + utils.calculatePadding(avpLen)

            size += 8
            if codeFound:
                o_ParsedData.isParsed = True
                o_ParsedData.avpSize  = avpLen
                o_ParsedData.padding  = utils.calculatePadding(avpLen)

                if (utils.existVendorID(avpFlags)):
                    # read vendor-id
                    (vendorID,) = fmt.unpack(self.nwBuffer.read(4))
                    o_ParsedData.vendorID = vendorID
                    size += 4
                    ## Set the network buffer to the data.
                    ## It's already set to data due to above read.
                    ## So, we can return safely from here

                codeFound = False
                return o_ParsedData
            else:
                unwanted = self.nwBuffer.read(avpLenPadded - 8)  ## (8 bytes is already read)
                size += (avpLenPadded - 8)
                
        return o_ParsedData


    """
    getElement function returns the size of the complete AVP i.e.
    (AVP header + Avp Data) and sets the self.nwBuffer
    right after the AVP header.
    1. For simple AVP's, the next logical step is to parse the data.
    2. For Grouped AVP's, we can again call this function to parse the AVP's
       present inside the grouped AVP, and buffer needs to be reset to right under
       grouped AVP header instead of Diameter header.
    3. After parsing grouped AVP's, nwBuffer needs to reset using resetBuffer()
    """
    def getElement(self, avpName = None, msgSize = None):
        if not msgSize:
            msgSize = self.nwEventSize

        if avpName:
            avpCode = utils.getAVPCode(avpName) 

            if avpCode:
                return  self.findSimpleElementLocation(avpCode, msgSize)
            else:
                print "ERROR: AVP code not found for {0}".format(avpName)
                return False
        else:
            print "ERROR: AVP Name not provided {0}".format(avpName)
            return False
        
        return True


    ## For future use
    def getElement_multi(self):
        return True



if __name__ == "__main__":
    fd = open("VOICE_2013_08_20_10_19_37_edit.dat", "rb") 
    data = fd.read(512)
    fd.close()

    parser = GenericDiameterMsgParser(data, 408)
    p = parser.getElement('Service-Context-Id') 
    parser.resetBuffer() 
    """
    o_ParsedData = parser.getElement('Subscription-ID')

    if o_ParsedData.isParsed:
        o_ParsedData = parser.getElement('Subscription-ID-Type', o_ParsedData.avpSize + o_ParsedData.padding)
        data = parser.nwBuffer.read(4)
        s = struct.Struct('>I')
        (val,) = s.unpack(data)
        print  val
    parser.resetBuffer()
    """
    
