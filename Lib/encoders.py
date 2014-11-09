########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : encoders.py
# Domain : Library
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import struct
import binascii
import firebolt.Utils.DiameterUtils as utils


def uint32Encoder(content):
    packedData = struct.pack('>I', int(content))
    return [packedData, 4, 0]


def int32Encoder(content):
    packedData = struct.pack('>i', int(content))
    return [packedData, 4, 0]


def uint64Encoder(content):
    packedData = struct.pack('>Q', int(content))
    return [packedData, 8, 0]


def int64Encoder(content):
    packedData = struct.pack('>q', int(content))
    return [packedData, 8, 0]


def stringEncoder(content):
    padding = utils.calculatePadding(len(content))
    packedData = struct.pack('{0}s{1}x'.format(len(content), padding), str(content))

    return [packedData, len(content), padding]


def ipv4AddressEncoder(content):
    import socket
    try:
        packedData = socket.inet_aton(content)
    except Exception, e:
        print 'WARN: incorrect IP address: {0}'.format(content)
        packedData = socket.inet_aton("10.10.10.10")

    return [packedData, 4, 0]


def ipv4AddressEncoderE164(content):
    import socket
    try:
        ip = socket.inet_aton(content)
        pack= struct.pack('!2B4s',0,1,ip).encode("hex")
    except Exception, e:
        print 'WARN: incorrect IP address: {0}'.format(content)
        pack = socket.inet_aton("10.10.10.10")
        pack= struct.pack('!2B4s',0,1,pack).encode("hex")

    return [pack, len(pack), utils.calculatePadding(len(pack))]
