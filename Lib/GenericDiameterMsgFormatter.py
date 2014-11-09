########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : GenericDiameterMsgFormatter.py
# Domain : Library
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import sys
import struct
from cStringIO import StringIO

import firebolt.Utils.DiameterUtils as utils
import firebolt.Config.MasterAVPDict as avpConfig
import firebolt.Lib.DiameterGroup as Node

"""
@class: GenericDiameterMsgFormatter
@desc : This class provides functions for building the AVP's to 
        form a diameter structure.
"""
class GenericDiameterMsgFormatter:
    def __init__(self):
        self.diamMessage = StringIO()
        self.messageSize = utils.DIAMETER_HEADER_SIZE   ## Size of diameter event excluding header i.e 20 bytes
        self.encodeBF = dict()
        self.bindEncodingFunc()
        self.commandcode = 272

    """ Binds the encoding function as per data type """
    def bindEncodingFunc(self):
        self.encodeBF = utils.bindEncodingFunc(self.encodeBF)


    """
        Creates diameter header with the default values of
        version, command code and Application ID unless
        explicitly provided to the function.
    """
    def createHeader(self, version = 1, commandCode = 272, appID = 4):
        packedData =  struct.pack('>BBHBBHIII', version, self.messageSize >> 16, self.messageSize & 0xFFFF, 128, \
                                    commandCode >> 16 , commandCode & 0xFFFF, appID, 1, 1)
        self.diamMessage.write(packedData)
        self.commandCode = commandCode
        return True


    """
        This function must be called after adding all the AVP's 
        of the event to the formatter. It updates the message
        length in the diameter header.
    """
    def updateMessageLength(self, msgLength = None):
        ## seek to the starting position of the cStringIO buffer
        self.diamMessage.seek(0)
        if msgLength:
            self.messageSize = msgLength

        self.createHeader(commandCode = self.commandCode)
        return True

    
    """ Resets the buffer and message size to zero. """
    def reset(self):
        self.diamMessage = StringIO() ## creating new one will be faster
        self.messageSize = 0
        return True


    """
        Creates a diameter atom for the Avp name
        with the provided value.
        The diameter atom is then serialized to the
        formatter buffer (diamMessage)
    """
    def addElement(self, avpName, value):
        diamAtom = Node.DiameterAtom(avpName) 
        diamAtom.setContent(value) 
        serAVP = diamAtom.serialize()
        self.diamMessage.write(serAVP.getvalue())

        self.messageSize += diamAtom.getTotalSize()
        return True



    def getMessageSize(self):
        return True

    def getBodyMessageSize(self):
        return True



    def getHeaderSize(self):
        """
            Diameter Header size is always 20 bytes
        """
        return 20


    """
    This function is used for adding grouped AVP's to the diamMessage buffer
    of the formatter.
    The function expects serialized buffer of the grouped AVP instead of just 
    AVP name and value.
    Adds a diameter part, i_pDiameterPart, to the buffer this might be useful
    in cases where there is a diameter part that is already prepared and the 
    caller must be sure about that
    """
    def addAsIs(self, serDiameterPart):
        self.diamMessage.write(serDiameterPart.getvalue())
        self.messageSize += len(serDiameterPart.getvalue())

        return


    def replaceElementValue(self, avpName, newValue):
        return



## testing purpose
if __name__ == "__main__":
    fmt = GenericDiameterMsgFormatter() 
    fmt.createHeader()
    fmt.addElement('Session-ID', 'wreg9rwkej')
    fmt.updateMessageLength(44)

    fd = open('test.dat', "wb")
    fd.write(fmt.diamMessage.getvalue())
    fd.close()
