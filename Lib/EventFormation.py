########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : EventFormation.py
# Domain : Library
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
import firebolt.Lib.DiameterGroup  as Node
import firebolt.Lib.GenericDiameterMsgFormatter as formatter
import firebolt.Utils.DiameterUtils  as utils
import firebolt.Config.EventStructureConfig as evStruct
import firebolt.Config.MasterAVPDict  as avpConfig

from cStringIO import StringIO

"""
@class: EventFormatter
@desc : Class is responsible for creating a diameter event 
        as per the event structure.
        It uses the formatter class ang DiameterGroup to create serialized
        AVP structure.
        The generated data is put in a queue (only if its subscribed to)
        Which can be consumed by any other python client.
"""
class EventFormatter:
    def __init__(self, File = None, eventType = None):
        self.fileName    = File            ## File name from which events needs to be created
        self.eventType   = eventType       ## Type of the event
        self.variableAVP = dict()          ## Stores the AVP Name as key and the Value (from file) as value

        self.event       = evStruct.eventStructure[eventType] ## Event structure
        self.formatter   = None
        self.queue       = None
        self.eventTypeConfig = evStruct.eventTypeConfig[self.eventType]

        # for sending multiple events from file
        # this list stores the header(avp's with variable data)
        self.header = []
        self.isSubscribedToQ = False


    """
        Initializes the formatter and starts event creation by 
        creating the header.
        This function is called when event formation process
        is started.
    """
    def initEvent(self):
        self.formatter   = formatter.GenericDiameterMsgFormatter()
        ##create the diameter header
        self.formatter.createHeader(commandCode = self.eventTypeConfig['CommandCode'])


    """
        Attaches the working instance to
        a multiprocessor Queue
    """
    def subscribe(self, queue):
        self.queue = queue
        print self.queue
        self.isSubscribedToQ = True
        return True


    """ Put the event into Queue """
    def put(self, data = "Def"):
        if self.isSubscribedToQ:
            if data:
                self.queue.put(self.formatter.diamMessage.getvalue())
            else:
                self.queue.put(None)


    """ Use for testing purpose only """
    def put_test(self):
        fd = open("test_voice.dat", "ab")
        fd.write(self.formatter.diamMessage.getvalue())
        fd.close()
        return True


    def validate_header(self):
        for avpName in self.header:
            for key in self.event.keys():
                if key == avpName:
                    found = True
                    break
            if found:
                found = False
            else:
                return False


    """
        The index value of the AVP name present in the
        file provided.
        Used to retrieve the corresponding AVP's value by
        indexing.
    """ 
    def getIndexFromHeader(self, avpName):
        for index, value in enumerate(self.header):
            if value == avpName:
                return index

        return None



    """ Adding Diameter Atom to formatter """
    def atomHandler(self, avpName, avpValue, fileRec = None):
        if fileRec:
            index = self.getIndexFromHeader(avpName)
            if index is not None:
                #avpValue = utils.format(avpName, fileRec[index].strip()) #what if we want spaces ? 
                avpValue = utils.format(avpName, fileRec[index])
        try:
            self.formatter.addElement(avpName, avpValue)
        except Exception, e:
            print "ERROR for AVP {0}".format(avpName)
            print "Exception:\n{0}".format(str(e))

        return True



    """
        Recursive function for serializing grouped AVP.
        This function, instead of creating the serialized
        AVP structure, returns the final DiameterGroup
        object. The calling function, needs to use the 
        object and call its serialize function explicitly. 
    """  
    def groupHandler(self, avpName, child, fileRec = None):
        grpAvp = Node.DiameterGroup(avpName) 

        for name, value in child.iteritems():
            if isinstance(value, dict):
                grpAVP_N = self.groupHandler(name, value, fileRec)
                try:
                    grpAvp.addItem(grpAVP_N)
                except Exception, e:
                    print "ERROR for AVP {0}".format(name)
                    print "Exception:\n{0}".format(str(e))
                pass
            else:
                if fileRec:
                    index = self.getIndexFromHeader(name)
                    if index is not None:
                        value = utils.format(name, fileRec[index].strip())
                try:
                    atmAvp = Node.DiameterAtom(name)
                    atmAvp.setContent(value)
                    grpAvp.addItem(atmAvp)
                except Exception, e:
                    print "ERROR for AVP {0}".format(name)
                    print "Exception:\n{0}".format(str(e))
        return grpAvp



    """
        Function which will create a single diameter AVP using 
        the default values provided in the event structure.
    """
    def start_default(self, fileRec = None):
        print "Start of event formation for {0}.".format(self.eventType)
        self.initEvent()
        for avpName, avpValue in self.event.iteritems():
            if isinstance(avpValue, dict):
                grpAVP    = self.groupHandler(avpName, avpValue, fileRec)
                serBuffer = grpAVP.serialize()
                self.formatter.addAsIs(serBuffer)
            else:
                self.atomHandler(avpName, avpValue, fileRec)

        ## Update the Message Length
        self.formatter.updateMessageLength()

        ## Put the event to Queue
        self.put()

        return True



    """
        Function which will be called to create multiple
        diameter events as per the values for the AVP
        provided in the File.
    """
    def start_multi(self):
        fd = open(self.fileName, "r")
        ## 1. Read the header
        line = fd.readline().splitlines()[0]
        headList = line.split(',')
        self.header = [elem.strip() for elem in headList]

        for line in fd.readlines():
            line = line.splitlines()[0]
            recs = line.split(',') 
            self.start_default(recs)

        print "Finished with processing file for {0}".format(self.eventType)
        return True



    """
        This function must be called externally
        to start creating the event
    """
    def start(self):
        if self.fileName == None:
            # Create one event with default value
            self.start_default()
            self.put(None)
        else:
            self.start_multi()
            self.put(None)
        return True



## Basic Testing
if __name__ == "__main__":
    obj = EventFormatter(File = "voice_events.dat", eventType = 'VOICE') 
    #obj = EventFormatter(eventType = 'VOICE')
    obj.start()
