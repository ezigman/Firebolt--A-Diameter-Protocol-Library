########################################################################
# Project: Firebolt
# Desc   : Diameter Library in Python 
#
# File   : EventGenerator.py
# Domain : Tools
#
# Author : Arun Muralidharan
# Dated  : August 2013
#########################################################################

import os
import sys
import Queue
import datetime
import time
import multiprocessing as mpc

import firebolt.Config.EventStructureConfig as evtStruct
import firebolt.Lib.EventFormation as creator
import DiameterRawEventViewer as drv


def sendCER(connection):
    try:
        cerEvent = evtStruct.eventStructure['CER']
    except Exception, e:
        print "ERROR\nException = {0}".format(str(e))
        return False

    evtFmt = creator.EventFormatter(eventType = 'CER') 
    if evtFmt.start():
        #Sorry, accessing data directly instead of using Queue
        #interface
        connection.send(evtFmt.formatter.diamMessage.getvalue())

        try:
            result = connection.recv(1024)
        except Exception,e:
            if 'timed out' in e:
                print 'Time out, event may be dropped'
            elif 'Connection refused' in e:
                print 'Connection refused, Server may be crashed'
            else:
                print "ERROR: Unknown exception.\nException = {0}".format(str(e))
            return False

    return True


def worker_online(eventType, eventConfig):
    print "Worker started for event type (online): {0}".format(eventType)

    import socket
    sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sd.settimeout(eventConfig['ReceiveTO'])

    try:
        sd.connect((eventConfig['Host'], eventConfig['Port']))
    except Exception, e:
        print "ERROR: connection issue. \nException = {0}".format(str(e))
        return False

    if sendCER(sd):
        evtFmt = creator.EventFormatter(eventConfig['InputFileLocation'], eventType)
        manager = mpc.Manager()
        queue = manager.Queue()
        evtFmt.subscribe(queue)

        proc = mpc.Process(target = evtFmt.start)
        proc.start()

        while True:
            tmp = queue.get()
            if tmp == None:
                break
            else:
                sd.send(tmp)
                try:
                    result = sd.recv(2048)
                    print "DEBUG: response received"

                    obj = cStringIO.StringIO()
                    obj.write(result)
                    drv.parser(obj)

                    # TODO: Parse Result-code
                except Exception,e:
                    if 'timed out' in e:
                        print 'Time out, event may be dropped'
                    elif 'Connection refused' in e:
                        print 'Connection refused, Server may be crashed'
                    else:
                        print "ERROR: Unknown exception.\nException = {0}".format(str(e))
                    #return False
    else:
        print "CER Failed."
        return False
                
    return True


def worker_offline(eventType, eventConfig):
    print "Worker started for event type (offline): {0}".format(eventType)
    evtFmt = creator.EventFormatter(eventConfig['InputFileLocation'], eventType)
    ## Creating Queue out of manager since the queue needs to be passed to
    ## another function.
    manager = mpc.Manager()
    queue = manager.Queue()    
    evtFmt.subscribe(queue)

    proc = mpc.Process(target = evtFmt.start)
    proc.start()

    now = datetime.datetime.now()
    fmt = now.strftime("%Y_%m_%d_%H_%M_%S")

    opFileName = eventConfig['OutputFileLocation'] + "/" + "{0}_{1}.dat".format(eventType, fmt)
    fd = open(opFileName, "wb")

    recordCount = 0

    while True:
        tmp = queue.get()
        if tmp == None:
            break
        else:
            fd.write(tmp)
            recordCount += 1

    fd.close()

    try:
        registerFileToAC1(opFileName, recordCount)
    except Exception, e:
        print "Exception: {0}".format(str(e))

    return True



## Registers the File in AC1_CONTROL for File2E
def registerFileToAC1(FileName = None, recordCount = 0, file_format = "TCUSAGE"):

    conn_string = os.getenv('APP_DB_USER') + '/' + os.getenv('APP_DB_PASS') + '@' + os.getenv('APP_DB_INST')
    dirName = os.path.dirname(FileName)
    filename = os.path.basename(FileName)
    command = "AC1RunFileCreatorSA_Sh -g SMM -a {0} -d {1}".format(file_format, conn_string) + ' -n {0} -p {1} -r _TCUSAGE -t _TCUSAGE -f {2} -w {3}'.format(filename, dirName, file_format, recordCount)
    print command
   
    import subprocess
    process = subprocess.Popen([command],shell=True)  
    process.wait()


##-----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    online_jobs  = []
    offline_jobs = []

    if len(sys.argv) < 2:
        option = '-m'
    else:
        option = sys.argv[1]

    for eventType in evtStruct.eventTypes:
        eventConfig = evtStruct.eventTypeConfig[eventType]

        if eventConfig['Runnable']:

            if eventConfig['Mode']  == 'offline':
                proc = mpc.Process(target = worker_offline, args = (eventType,eventConfig))
                offline_jobs.append(proc)

            elif eventConfig['Mode'] == 'online':
                proc = mpc.Process(target = worker_online, args = (eventType,eventConfig))
                online_jobs.append(proc)

            else:
                print "ERROR: Unknown mode configured for event type : {0}".format(eventType)
        else:
            print "{0} event type is not Runnable".format(eventType)


    all_jobs = online_jobs + offline_jobs
    ## Start the jobs
    for job in all_jobs:
        job.start()
        if option == "-s":
            job.join()


    ## wait for jobs to finish
    if option != "-s":
        for job in all_jobs:
            job.join()
