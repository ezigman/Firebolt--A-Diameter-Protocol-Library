########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : DiameterEditor.py
# Domain : Tools
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
import copy
import firebolt.Tools.DiameterEventViewer as objViewer


class DiameterEditor:
    def __init__(self, File = None, eventType = None):
        self.diamObject = objViewer.DiameterEventViewer(File, eventType)
        print "START: parsing od diameter file: {0}".format(File)
        self.diamObject.startParsing()
        print "END  : parsing finished\n"

        self.startStateMachine()

    def startStateMachine(self):
        print "______________________________________________"
        print "List of AVP's present in the diameter event:"
        print "--------------------------------------------"
        print "[Note] At this stage, AVP's inside AVP will"
        print "not be shown. For that select the grouped AVP."
        print "______________________________________________\n"

        print "AVP_CODE        AVP_NAME                             AVP_TYPE"
        print "-------------------------------------------------------------"

        for avpName, avpObj in self.diamObject.avpObject.iteritems():
            if avpObj.isGrouped:
                print "{0:8}         {1:32}      Grouped".format(avpObj.avp_code, avpName)
            else:
                print "{0:8}         {1:32}      Single".format(avpObj.avp_code, avpName)
        
        print "\n"

        self.startEditor()

        return True


    def printAVP(self, avpObj):
        print "Current AVP Details:"
        print "----------------------"
        print "AVP Name   :  {0}".format(avpObj.avp_name)
        print "AVP Code   :  {0}".format(avpObj.avp_code)
        print "AVP Flag   :  {0}".format(avpObj.avp_flag)
        print "AVP Len    :  {0}".format(avpObj.avp_size)
        print "AVP Vendor :  {0}".format(avpObj.avp_vendorID)
        print "AVP Padding:  {0}".format(avpObj.avp_padding)
        print "AVP Data   :  {0}".format(avpObj.avp_content)


    def handleAtom(self, avpObj):
        self.printAVP(avpObj)

        print ""
        print "Attribute ID       Attribute Name"
        print "---------------------------------"
        print "{0:12}        {1}".format(1, 'AVP Name')
        print "{0:12}        {1}".format(2, 'AVP Code')
        print "{0:12}        {1}".format(3, 'AVP Flag')
        print "{0:12}        {1}".format(4, 'AVP Len')
        print "{0:12}        {1}".format(5, 'AVP Vendor ID')
        print "{0:12}        {1}".format(6, 'AVP Data')
        print "{0:12}        {1}".format(7, 'Remove AVP')
        print "\n Enter 'q' to quit"

        while True:
            print ""
            attribID = raw_input("Enter the Attribute ID: ")
            if attribID == 'q':
                break
            attribID = int(attribID)

            if attribID not in [2,3,4,5,6,7]:
                print "ERROR: invalid attribute ID."
                return False

            if attribID == 2:
                avp_code = raw_input("Enter New AVP Code: ")
                avp_code = int(avp_code)
                avpObj.avp_code = avp_code
                pass
            elif attribID == 3:
                avp_flag = raw_input("Enter New AVP Flag: ")
                avp_flag = int(avp_flag)
                avpObj.setFlags(avp_flag)
                pass
            elif attribID == 4:
                avp_len = raw_input("Enter New Length (w/o padding): ")
                avp_len = int(avp_len)
                avpObj.avp_size = avp_len
                pass
            elif attribID == 5:
                avp_vendor = raw_input("Enter New Vendor ID: ")
                avp_vendor = int(avp_vendor)
                avpObj.setVendorID(avp_vendor)
            elif attribID == 6:
                avp_data = raw_input("Enter New data: ")
                avpObj.avp_content = avp_data
                pass
            elif attribID == 7:
                ## AVP cannot be removed here directly, as we dont know
                ## whether its single AVP or AVP inside grouped
                ## at this point of time.
                avpObj = "REMOVE"
                
        if not isinstance(avpObj, str):
            print "AVP New Details:"
            self.printAVP(avpObj)

        return avpObj


    def handleGroup(self, avpObj, count = 0):
        print "AVP's available under this group.\n"
        print "AVP_CODE        AVP_NAME                             AVP_TYPE"
        print "-------------------------------------------------------------"

        for avp in avpObj.diameterGroupList:
            if avp.isGrouped:
                print "{0:8}         {1:32}      Grouped".format(avp.avp_code, avp.avp_name)
            else:
                print "{0:8}         {1:32}      Single".format(avp.avp_code, avp.avp_name)

        print "\n"

        print "Provide the details of the AVP which is to be modified"
        print "------------------------------------------------------\n"

        while True:
            print "Enter 'q' to quit menu\n"
            avp_code = raw_input("AVP Code: ")
            if avp_code == 'q':
                break

            avp_code = int(avp_code)

            for avp in avpObj.diameterGroupList:
                if avp.avp_code == avp_code:
                    if avp.isGrouped:
                        count += 1
                        avp_n = copy.copy(avp)
                        avpObj.avp_size -= avp.getTotalSize()
                        avpObj.diameterGroupList.remove(avp)
                        avpGrp_N = self.handleGroup(avp_n, count)
                        avpObj.addItem(avpGrp_N) 
                        pass
                    else:
                        avp_n = copy.copy(avp)
                        avpObj.avp_size -= avp.getTotalSize()
                        avpObj.diameterGroupList.remove(avp)
                        avp_n = self.handleAtom(copy.deepcopy(avp_n)) 
                        ## Check tio handle if its a string.
                        if isinstance(avp_n, str):
                            if avp_n == "REMOVE":
                                ## DO nothing, we already removed!  
                                pass
                        else:
                            avpObj.addItem(avp_n)
                    break
         
        return avpObj


    def startEditor(self):
        print "Provide the details of the AVP which is to be modified"
        print "------------------------------------------------------\n"

        print "Length :: {0}".format(len(self.diamObject.avpObject.items()))

        while True:
            print "Enter 'q' to quit menu\n"
            avp_code = raw_input("AVP Code: ")
            if avp_code == 'q':
                break
            """
            if not self.diamObject.avpObject.has_key(self.diamObject.code2Name[int(avp_code)]):
                print "ERROR: Incorrect AVP entered."
                return False
            """

            avpObj = self.diamObject.avpObject[self.diamObject.code2Name[int(avp_code)]]
            if not avpObj.isGrouped:
                # This is simple AVP
                avpObj = self.handleAtom(avpObj)

                ## Check to handle if its a string.
                if isinstance(avpObj, str):
                    if avpObj == "REMOVE":
                        ## remove from the dict
                        del self.diamObject.avpObject[self.diamObject.code2Name[int(avp_code)]]
                else:
                    self.diamObject.avpObject[avpObj.avp_name] = avpObj
            else:
                # This is a grouped AVP
                avpGrp_n = self.handleGroup(avpObj)
                self.diamObject.avpObject[avpObj.avp_name] = avpGrp_n
                pass

        return True



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "Usage: python DiameterEditor.py <Diameter File> <Event Type>\n"
        print "Example:"
        print "python DiameterEditor.py VOICE_2013_08_16_18_35_58.dat VOICE"
        sys.exit(0) 

    fileName = sys.argv[1]
    eventType= sys.argv[2]

    editor = DiameterEditor(fileName, eventType)
    editor.diamObject.serializeDictToDiameter()
