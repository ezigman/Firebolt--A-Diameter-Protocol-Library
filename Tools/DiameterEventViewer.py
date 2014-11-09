########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : DiameterEventViewer.py
# Domain : Utils
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
import firebolt.Lib.DiameterGroup as Node
import firebolt.Lib.GenericDiameterMsgParser as Parser
import firebolt.Lib.GenericDiameterMsgFormatter as formatter
import firebolt.Utils.DiameterUtils as utils
import firebolt.Config.MasterAVPDict as avpConfig
import firebolt.Config.EventStructureConfig as evtStruct

class DiameterEventViewer:
    def __init__(self, File = None, eventType = None):
        self.fileName  = File
        self.eventType = eventType
        self.parser    = None
        self.event = evtStruct.eventStructure[eventType]

        self.avpObject = dict()
        self.code2Name = dict()
        self.decodeBF  = dict()  ## key = data_type ; value = Function
        self.decodeBF  = utils.bindDecodingFunc(self.decodeBF)

        self.mapCode2Name()
        self.initParser()


    def mapCode2Name(self):
        for name, value in avpConfig.avpPack.iteritems():
            self.code2Name[value['Code']] = name



    def initParser(self):
        if self.fileName:
            try:
                fd = open(self.fileName, "rb")
            except Exception, e:
                print "ERROR: file not loaded. Exception = {0}".format(str(e))
            
            # Read first 4 bytes of diameter event(which is part of 20 byte header)
            [msgLen, Version] = utils.getFlagAndLength(fd.read(4))
            # set file descriptor to start of file
            fd.seek(0)
            data = fd.read(msgLen)
            fd.close()
    
        self.parser = Parser.GenericDiameterMsgParser(data, msgLen)


    def serializeDictToDiameter(self):
        fmat   = formatter.GenericDiameterMsgFormatter()
        fmat.createHeader(commandCode = evtStruct.eventTypeConfig[self.eventType]['CommandCode']) 

        for key, value in self.avpObject.iteritems():
            value.setContent()
            serBuffer = value.serialize() 
            fmat.addAsIs(serBuffer)

        fmat.updateMessageLength()

        ## Write to a file
        [filename, ext] = os.path.basename(self.fileName).split('.')
        editFileName = filename + "_edit.dat"
        fd = open(editFileName, "wb") 
        fd.write(fmat.diamMessage.getvalue())
        fd.close()


    ## Should only be called after event is parsed
    ## and avpObject dict is populated
    def printEvent(self):
        print "#"*80
        print "# {0:30}  {1:6}    {2:16}   {3}".format("AVP_NAME", "AVP_CODE", "AVP_VALUE", "AVP_LENGTH")
        print "#"*80
        for key, value in self.avpObject.iteritems():
            if not value.isGrouped:
                print "# {0:30}  {1:6}      {2:16}   {3}".format(key, value.avp_code, str(value.avp_content), value.avp_size)
            else:
                print  "# " + "_"*80
                print "# {0:30}  {1:6}      {2:16}   {3}".format(key, value.avp_code, "{Grouped}", value.avp_size)
                print "# " + "_"*80
                for avp in value.diameterGroupList:
                    self.printGroup(avp)
                print "#"


    def printGroup(self, grpAvp, count = 1):
        if not grpAvp.isGrouped: 
            print "# " + "\t"*count + "{0:30}  {1:6}      {2:16}   {3}".format(grpAvp.avp_name, grpAvp.avp_code, str(grpAvp.avp_content), grpAvp.avp_size)
        else:
            print "# " + "\t"*count + "-"*80
            print "# " + "\t"*count + "{0:30}  {1:6}      {2:16}   {3}".format(grpAvp.avp_name, grpAvp.avp_code, "{Grouped}", grpAvp.avp_size)
            print "# " + "\t"*count + "-"*80
            for avp in grpAvp.diameterGroupList:
                self.printGroup(avp, count + 1)
            print "#"


    def groupHandler(self, avpName, avpValue):
        grpAvp = Node.DiameterGroup(avpName) 
        grpAvp.isGrouped = True

        o_ParsedData = self.parser.getElement(avpName)

        if o_ParsedData.isParsed:
            for name, value in avpValue.iteritems():
                if isinstance(value, dict):
                    initPos = self.parser.nwBuffer.tell()
                    grpAVP_N = self.groupHandler(name, value)

                    if grpAVP_N:
                        grpAvp.addItem(grpAVP_N)
                    self.parser.setNetworkBufferPosition(initPos)

                else:
                    ## Get the decoder
                    func = self.decodeBF[avpConfig.avpPack[name]['Type']]
                    ## save the position right after grouped
                    initPos = self.parser.nwBuffer.tell() 
                    o_ParsedDataAtm = self.parser.getElement(name)

                    if o_ParsedDataAtm.isParsed:
                        if o_ParsedDataAtm.vendorID:
                            [decodedData, avp_len] = func(self.parser.nwBuffer.read(o_ParsedDataAtm.avpSize - 12))
                        else:
                            [decodedData, avp_len] = func(self.parser.nwBuffer.read(o_ParsedDataAtm.avpSize - 8))

                        atom = Node.DiameterAtom(name) 
                        atom.avp_content = decodedData
                        atom.avp_size    = avp_len
                        atom.avp_padding = o_ParsedDataAtm.padding 
                        grpAvp.addItem(atom)

                    ## IMPORTANT
                    ## Reset the buffer back to grouped AVP
                    self.parser.setNetworkBufferPosition(initPos)
        else:
            print "WARN: ** AVP {0} NOT FOUND IN THE INPUT EVENT **".format(avpName)
            return None

        return grpAvp

    

    def atomHandler(self, avpName):
        func = self.decodeBF[avpConfig.avpPack[avpName]['Type']]
        o_ParsedData = self.parser.getElement(avpName) 

        if o_ParsedData.isParsed:
            if o_ParsedData.vendorID:
                [decodedData, avp_len] = func(self.parser.nwBuffer.read(o_ParsedData.avpSize - 12))
            else:
                [decodedData, avp_len] = func(self.parser.nwBuffer.read(o_ParsedData.avpSize - 8))
        else:
            print "WARN: ** AVP {0} NOT FOUND IN THE INPUT EVENT **".format(avpName)
            decodedData = ""
            avp_len = 0
            return None

        atom = Node.DiameterAtom(avpName)
        atom.avp_content = decodedData
        atom.avp_size    = avp_len
        atom.avp_padding = o_ParsedData.padding

        if o_ParsedData.vendorID:
            atom.setVendorID(o_ParsedData.vendorID)
        else:
            atom.clrVendorBit()

        return atom

        

    def startParsing(self):
        for avpName, avpValue in self.event.iteritems():
            if isinstance(avpValue, dict):
                grpAVP = self.groupHandler(avpName, avpValue) 
                ## Set the AVP in hash
                if grpAVP:
                    self.avpObject[avpName] = grpAVP
                self.parser.resetBuffer()
            else:
                atom = self.atomHandler(avpName)
                ## Set the AVP in hash
                if atom:
                    self.avpObject[avpName] = atom

                # IMPORTANT
                self.parser.resetBuffer()


if __name__ == "__main__":
    #obj = DiameterEventViewer("VOICE_2013_08_16_18_35_58.dat", "VOICE") 
    if len(sys.argv) < 3:
        print "Usage: python DiameterEventViewer.py <Diameter File> <Event Type>\n"
        print "Example:"
        print "python DiameterEventViewer.py VOICE_2013_08_16_18_35_58.dat VOICE"
        sys.exit(0)

    fileName = sys.argv[1]
    eventType= sys.argv[2]

    obj = DiameterEventViewer(fileName, eventType)
    obj.startParsing()
    obj.printEvent()
