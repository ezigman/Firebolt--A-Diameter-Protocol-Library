########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : decoders.py
# Domain : Library
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import struct
import binascii
import firebolt.Utils.DiameterUtils as utils

def uint32Decoder(content):
    fmt = struct.Struct('>I')
    (val,) = fmt.unpack(content)
    return [val, 4]


def int32Decoder(content):
    fmt = struct.Struct('>i')
    (val,) = fmt.unpack(content)
    return [val, 4]


def uint64Decoder(content):
    fmt = struct.Struct('>Q')
    (val,) = fmt.unpack(content)
    return [val, 8]


def int64Decoder(content):
    fmt = struct.Struct('>q')
    (val,) = fmt.unpack(content)
    return [val, 8]


def stringDecoder(content):
    fmt = struct.Struct('>{0}s'.format(len(content)))
    (val,) = fmt.unpack(content)
    return [val, len(val)]


def ipv4AddressDecoder(content):
    import socket
    addr = socket.inet_ntoa(content)
    return [addr, 4]


def ipv4AddressDecoderE164(content):
    import socket
    #import binascii
    #binary_string = binascii.unhexlify(content[4:])
    return [str(content), len(str(content))] 
