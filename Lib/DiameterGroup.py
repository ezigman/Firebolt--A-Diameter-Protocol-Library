########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : DiameterGroup.py
# Domain : Library
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
import importlib
import inspect
import struct

import firebolt.Utils.DiameterUtils as utils
import firebolt.Config.MasterAVPDict as avpConfig
from cStringIO import StringIO

FUN = 0xDEADBEEFCAFEBABE

## AVP Header Flags
V_BIT_MASK = 0x80
M_BIT_MASK = 0x40
P_BIT_MASK = 0x20

CLR_V_BIT  = 0x7F
CLR_M_BIT  = 0xBF
CLR_P_BIT  = 0xDF

## Size of AVP header(in Bytes) with and 
## without Vendor-ID
AVP_HEADER_NO_VENDOR   = 8
AVP_HEADER_WITH_VENDOR = 12


"""
@class: DiameterGroup
@desc : Represents a diameter AVP (single/grouped) as 
        a class.
        It initializes the AVP by reading the AVP configuration dict.
        It also provides a number of members to modify the 
        state of an AVP. Eg. Setting/Clearing Flags, adding nested AVP's
        getting size of AVP etc..
"""
class DiameterGroup:
    def __init__(self, avpName = ""):
        self.avp_name = avpName 
        self.avp_code = 0
        self.avp_size = 0
        self.avp_flag = 0
        self.avp_vendorID = 0
        self.isGrouped = False       ## Indicates if its an grouped AVP or not
        self.diameterGroupList = []

        self.avp = avpConfig.avpPack[self.avp_name]
        self.initializeAVP()

    """
        This Function must be called to create the AVP.
        It sets the value of all the fields based upon the
        values configured in the dictionary.
        For now, this is called within the constructor.
    """
    def initializeAVP(self):
        self.setCode(self.avp['Code'])

        if self.avp['Mandatory'] == 1:
            self.setMandatoryBit()

        if self.avp['Protected'] == 1:
            self.setEncryptionBit()

        if self.avp['Vendor-ID'] == 1:
            self.setVendorID(self.avp['Vendor-Code'])

        return True

    """ Set AVP Code """
    def setCode(self, avpCode):
        self.avp_code = avpCode


    """ Add a Diameter AVP under a grouped AVP """
    def addItem(self, diameterGroup):
        # set isGrouped boolean here
        # never reset the Value
        self.isGrouped = True
        itemSize = diameterGroup.getTotalSize()
        self.avp_size += itemSize

        self.diameterGroupList.append(diameterGroup)


    """ Gets the total size of the grouped AVP """
    def getRealSize(self):
        return self.getTotalSize()


    def getTotalSize(self):
        if self.avp['Vendor-ID'] == 1:
            return  AVP_HEADER_WITH_VENDOR + self.avp_size
        else:
            return AVP_HEADER_NO_VENDOR + self.avp_size


    """ Gets number of child AVP's under this Grouped AVP """
    def childrenNumber(self):
        return len(self.diameterGroupList)


    """ packs the AVP header in binary format """
    def packAVPHeader(self):
        Len = self.getRealSize()
        if self.avp['Vendor-ID'] == 1:
            packedData = struct.pack('>IBBHI', self.avp_code, self.avp_flag, Len >> 16, Len & 0xFFFF, self.avp_vendorID) 
        else:
            packedData = struct.pack('>IBBH', self.avp_code, self.avp_flag, Len >> 16, Len & 0xFFFF)

        return packedData

    """
    @note: setContent is usually called on DiamterAtom,
           but, this functiona is only called while recreating 
           the diameter event by DiameterEditor.
    """ 
    def setContent(self):
        ## Reset the AVP size
        self.avp_size = 0

        ## To be called by Diameter Editor
        for avp in self.diameterGroupList:
            avp.setContent()
            self.avp_size += avp.getTotalSize()
    

    """
        Serializes the AVP content in diameter format
        Function returns cStringIO.StringIO object
    """
    def serialize(self):  
        serializedBuffer = StringIO()
        packedHeader = self.packAVPHeader() 
        serializedBuffer.write(packedHeader)

        for atom in self.diameterGroupList:
            serBuffer = atom.serialize()
            serializedBuffer.write(serBuffer.getvalue())

        return serializedBuffer


    """ Functions for handling(set/get) AVP Flags """


    def setVendorID(self, vendorID):
        self.avp_flag     = self.avp_flag | V_BIT_MASK

        self.avp_vendorID = vendorID
        self.setFlags(self.avp_flag)


    def setFlags(self, avpFlags):
        if utils.existVendorID(avpFlags):
            self.avp['Vendor-ID'] = 1
        else:
            self.avp['Vendor-ID'] = 0
            self.clrVendorBit()

        if utils.existMandatory(avpFlags):
            self.avp['Mandatory'] = 1
            self.setMandatoryBit()
        else:
            self.avp['Mandatory'] = 0
            self.clrMandatoryBit()

        if utils.existPersistent(avpFlags):
            self.avp['Protected'] = 1
            self.setEncryptionBit()
        else:
            self.avp['Protected'] = 0
            self.clrEncryptionBit()

    
    def clrVendorBit(self):
        self.avp_flag = self.avp_flag & CLR_V_BIT

    def setMandatoryBit(self):
        self.avp_flag = self.avp_flag | M_BIT_MASK

    def clrMandatoryBit(self):
        self.avp_flag = self.avp_flag & CLR_M_BIT

    def setEncryptionBit(self):
        self.avp_flag = self.avp_flag | P_BIT_MASK

    def clrEncryptionBit(self):
        self.avp_flag = self.avp_flag & CLR_P_BIT


#____________________________________________________________________________________________________________________

"""
@class : DiameterAtom
@desc  : Describes a single AVP Node.
         Derived from DiameterGroup class
"""

class DiameterAtom(DiameterGroup):
    def __init__(self, avpName = 0):
        DiameterGroup.__init__(self, avpName)
        
        self.avp_content = None
        self.avp_padding = 0

        self.encodeBF = dict()  ## key = data_type ; value = Encoding Function
        self.bindEncodingFunc()


    """ Gets the size of AVP WITHOUT Padding """
    def getRealSize(self):
        if self.avp['Vendor-ID'] == 1:
            return AVP_HEADER_WITH_VENDOR + self.avp_size
        else:
            return AVP_HEADER_NO_VENDOR + self.avp_size

    """ Gets the size of AVP WITH Padding """
    def getTotalSize(self):
        return self.getRealSize() + self.avp_padding


    """ Binds an encoding function for each data type """ 
    def bindEncodingFunc(self):
        self.encodeBF = utils.bindEncodingFunc(self.encodeBF)


    """
        Set the content as per the encoding
        The encoding handler must be called as per the
        AVP data type configuration
    """
    def setContent(self, avpContent = None):
        if avpContent == None:
            avpContent = self.avp_content
        func = self.encodeBF[avpConfig.avpPack[self.avp_name]['Type']]
        [self.avp_content, self.avp_size, self.avp_padding] = func(avpContent)
        return True


    """
        Serializes the AVP content in diameter format
        Function return cStringIO.StringIO() object
    """
    def serialize(self):
        serializedBuffer = DiameterGroup.serialize(self) 
        serializedBuffer.write(self.avp_content)

        return serializedBuffer

