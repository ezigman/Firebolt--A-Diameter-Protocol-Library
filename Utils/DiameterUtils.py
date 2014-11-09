########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : DiameterUtils.py
# Domain : Utils
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import sys
import re
import inspect
import struct
import firebolt.Config.MasterAVPDict as avpConfig

DIAMETER_HEADER_SIZE = 20 #bytes
## Flags
AVP_LEN_FLAG = 0x00FFFFFF
AVP_CF_FLAG  = 0xFF000000


""" Gets the AVP Code from AVP name """
def getAVPCode(avpName):
    return avpConfig.avpPack[avpName]['Code']


""" Checks if vendor ID is set in the AVP Flag """
def existVendorID(avpFlags):
    return int(avpFlags) & 0x80

""" Checks if Mandatory bit is set in the AVP Flag """
def existMandatory(avpFlags):
    return int(avpFlags) & 0x40

""" Checks if Persistent bit is set in the AVP Flag """
def existPersistent(avpFlags):
    return int(avpFlags) & 0x20



"""
    Argument expected is a 4 byte composite
    having 1 byte flag and 3 bytes length
    Length returned includes (Avp Header + Avp Data without padding)
"""
def getFlagAndLength(composite):
    fmt = struct.Struct('>I')
    (flagsAndLength,) = fmt.unpack(composite) 
    avpLen = flagsAndLength & AVP_LEN_FLAG

    avpFlags = (flagsAndLength & AVP_CF_FLAG) >> 24

    return [avpLen, avpFlags]


""" Calculates padding length required for the AVP """
def calculatePadding(Length):
    if (Length % 4) == 0:
        return 0
    else:
        padLen = 4 - (Length % 4)
        return padLen


""" Converts integer in string representation to integer type """
def format(avpName, avpValue):
    re_c = re.search('int', avpConfig.avpPack[avpName]['Type']) 
    if re_c:
        return int(avpValue)
    return avpValue


# Taken from auror.utils
# imports a module specified as string
def importClass(name):
    cur_version = sys.version_info
    req_version = (2,7)

    # Split the module name by the dot(.)
    parts = name.split('.')

    # if there are no dots then 'parts' will be a an array of 1 element
    # If this is the case then the class should be in the current module
    if len(parts) > 1:
        """
            importlib module comes shipped only for version >= 2.7
        """
        if cur_version >= req_version:
            import importlib
            module = importlib.import_module(".".join(parts[:-1]))
        else:
            module = __import__(".".join(parts[:-1]), fromlist = [''])
    else:
        module = None

    if module is not None:
        loadedClass = getattr(module, parts[-1])
    else:
        #loadedClass = globals()[parts[-1]]
        loadedClass = None
        localmodule = inspect.getmodule(inspect.currentframe().f_back)
        loadedClass = getattr(localmodule, parts[-1])
            
    return loadedClass



""" Binds the encoding functions to the respective data type """
def bindEncodingFunc(functionMap):
    for key in avpConfig.encodingFuncConfig.keys():
        funcName = avpConfig.encodingFuncConfig[key]
        functionMap[key] = importClass(funcName)

    return functionMap



""" Binds the decoding functions to the respective data type """
def bindDecodingFunc(functionMap):
    for key in avpConfig.decodingFuncConfig.keys():
        funcName = avpConfig.decodingFuncConfig[key]
        functionMap[key] = importClass(funcName)

    return functionMap
